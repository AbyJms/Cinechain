from flask import Flask, send_from_directory, request, jsonify
import os
import json
from google import genai
from google.genai import types

# --- 1. Flask App Setup ---
# Initialize Flask app
app = Flask(__name__, static_url_path='', static_folder='.')

# Set up environment variables
# IMPORTANT: Replace YOUR_API_KEY with your actual Gemini API key
# For local development, it is recommended to set this as an environment variable (GEMINI_API_KEY)
# We use a placeholder here, but the code will look for the env var.
if 'GEMINI_API_KEY' not in os.environ:
    print("Warning: GEMINI_API_KEY environment variable not set.")
    # Fallback to an empty string; Canvas environment will provide the key at runtime.
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
else:
    GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

# Initialize the Gemini Client
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    # Handle the case where the key might be invalid or missing during init
    print(f"Error initializing Gemini client: {e}")

# --- 2. Simulated External Data (CSV Replacement) ---
# This data simulates the content of your bms_seatdata.csv file
MOVIE_DATA = [
    {"movie_name": "The Cyberpunk Runner", "characters": ["Kira", "Jax"], "attendance": 850000, "income": 15000000},
    {"movie_name": "Eternal Horizon", "characters": ["Elias", "Zara"], "attendance": 1200000, "income": 28000000},
    {"movie_name": "The Time Traveler's Wife", "characters": ["Clare", "Henry"], "attendance": 250000, "income": 5000000},
    {"movie_name": "Shadow Realm", "characters": ["Vex", "Rhea"], "attendance": 550000, "income": 11000000},
]

# --- 3. Function Calling Tool Logic (The Python Function) ---

def get_movie_data(movie_name: str, detail_type: str) -> str:
    """
    Retrieves the attendance or income data for a specified movie.
    The detail_type must be 'attendance' or 'income'.
    """
    detail_type = detail_type.lower()
    if detail_type not in ["attendance", "income"]:
        return json.dumps({"error": f"Invalid detail type requested: {detail_type}. Please ask for 'attendance' or 'income'."})

    # Simple fuzzy matching (character similarity removed for simplicity)
    # The LLM is responsible for identifying the correct movie name from context.
    movie_name_lower = movie_name.lower()
    
    # Iterate through simulated data to find a match
    for movie in MOVIE_DATA:
        if movie["movie_name"].lower() == movie_name_lower:
            # Format the output based on detail type
            value = movie.get(detail_type)
            if detail_type == 'income':
                # Format income as currency
                value_formatted = f"${value:,}" 
            else:
                # Format attendance with commas
                value_formatted = f"{value:,}"

            return json.dumps({
                "movie": movie["movie_name"],
                "detail": detail_type,
                "value": value_formatted,
                "success": True
            })

    # If no movie is found
    return json.dumps({"error": f"Movie '{movie_name}' not found in the database. Please specify a different movie."})

# --- 4. Function Declaration (The Model's Schema) ---
# This defines the structure the LLM needs to call the Python function.
MOVIE_STAT_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_movie_data",
            description="Retrieves attendance (number of seats sold) or income (revenue generated) for a specific movie from the internal movie database. This is used after the user provides a movie name.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "movie_name": types.Schema(
                        type=types.Type.STRING,
                        description="The full name of the movie to query."
                    ),
                    "detail_type": types.Schema(
                        type=types.Type.STRING,
                        description="The specific metric the user wants: 'attendance' or 'income'. If the user asks for 'stats' or 'details', prompt them to choose one of these two metrics."
                    )
                },
                required=["movie_name", "detail_type"]
            ),
        )
    ]
)

# Map function names to the actual Python functions
AVAILABLE_FUNCTIONS = {
    "get_movie_data": get_movie_data,
}

# --- 5. Flask Routes ---

@app.route('/')
def index():
    # Serve the main chat interface
    return send_from_directory('.', 'index.html')

# We remove the unused routes like /cinechain.css, /cinechain.js, etc., for the single-file UI.
# Keeping /api/dashboard-data as provided by the user, although it's not used by the chatbot logic
# and the CSV file is not present on the backend.
@app.route('/api/dashboard-data')
def get_dashboard_data():
     # Using the MOVIE_DATA from above to simulate CSV read for this route
    total_attendance = sum(m["attendance"] for m in MOVIE_DATA)
    total_revenue = sum(m["income"] for m in MOVIE_DATA)
    total_movies = len(MOVIE_DATA)
    
    return jsonify({
        "movies_distributing": total_movies,
        "total_attendance": f"{total_attendance:,}",
        "total_revenue": f"${total_revenue:,}"
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handles the full conversational logic with Function Calling."""
    
    data = request.get_json()
    user_message = data.get('message')
    history_json = data.get('history', [])
    
    # Convert history from JSON list of objects to GenAI Content objects
    history = [
        types.Content(role=item['role'], parts=[types.Part.from_text(item['text'])])
        for item in history_json
    ]
    
    # Initial System Instruction & Greeting (to enforce the 'movbot' persona and first message)
    system_instruction = types.Content(
        role="system",
        parts=[types.Part.from_text("You are MovBot, a specialized conversational AI that helps users find movie statistics. You ONLY use the available 'get_movie_data' tool when asked about attendance or income for a movie. If the user asks for 'movie' in the second turn, ask 'which movie would you like to know more about?'. If they provide a movie name but not a detail, prompt them to choose 'attendance' or 'income'.")]
    )

    # Add the system instruction to the start of the current chat history for context
    if not history or history[0].role != 'system':
        history.insert(0, system_instruction)

    # Append the latest user message
    history.append(types.Content(role="user", parts=[types.Part.from_text(user_message)]))
    
    # Step 1: Send the conversation history to the model with the tool
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-05-20',
            contents=history,
            config=types.GenerateContentConfig(
                tools=[MOVIE_STAT_TOOL]
            )
        )
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return jsonify({"response": "I'm sorry, I'm having trouble connecting to my database right now. Please try again later.", "history": history_json})

    # Step 2: Check for Function Call request from the model
    if response.function_calls:
        call = response.function_calls[0]
        
        # 2a. Execute the local Python function
        if call.name in AVAILABLE_FUNCTIONS:
            
            # Extract arguments and call the function
            args = dict(call.args.items())
            function_output = AVAILABLE_FUNCTIONS[call.name](**args)
            
            # 2b. Add the function call and output to the history
            history.append(types.Content(
                role="model", 
                parts=[types.Part.from_function_call(call)]
            ))
            history.append(types.Content(
                role="function", 
                parts=[types.Part.from_function_response(name=call.name, response={"response": function_output})]
            ))
            
            # Step 3: Send the history (including tool output) back to the model for the final, natural response
            final_response = client.models.generate_content(
                model='gemini-2.5-flash-preview-05-20',
                contents=history,
                config=types.GenerateContentConfig(
                    tools=[MOVIE_STAT_TOOL]
                )
            )
            # Use the final generated text
            final_text = final_response.text
            
    else:
        # If no function call, the model generated a direct text response
        final_text = response.text

    # Step 4: Add the model's final response to the history for next turn
    history.append(types.Content(role="model", parts=[types.Part.from_text(final_text)]))
    
    # Prepare the final history for the client (as JSON list of strings/objects)
    # Note: Function calls and responses are complex, but the client only needs the text history.
    new_history = [{ 'role': h.role, 'text': h.parts[0].text } for h in history if h.role in ('user', 'model')]

    return jsonify({"response": final_text, "history": new_history})


if __name__ == '__main__':
    # Flask runs on port 5000 by default
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
