// ai.js

/**
 * Simulates a predictive revenue model using a simple linear trend.
 * @param {number[]} historicalData - Array of daily revenue numbers.
 * @returns {number[]} - Array of predicted daily revenue numbers.
 */
function predictRevenue(historicalData) {
  // Simple AI logic: Predict next 30 days based on the average of the last 7 days
  if (historicalData.length < 7) {
    return [];
  }
  
  const lastSevenDays = historicalData.slice(-7);
  const averageRevenue = lastSevenDays.reduce((sum, val) => sum + val, 0) / 7;
  
  const predictedData = [];
  for (let i = 0; i < 30; i++) {
    // Add some random variance to the prediction to make it more realistic
    const dailyPrediction = Math.round(averageRevenue * (1 + (Math.random() - 0.5) * 0.2)); // +/- 10% variance
    predictedData.push(dailyPrediction > 0 ? dailyPrediction : 0);
  }
  
  return predictedData;
}

/**
 * Simulates an AI-powered platform recommendation system.
 * @param {string} movieGenre - The genre of the movie.
 * @returns {string} - The recommended platform.
 */
function getPlatformRecommendation(movieGenre) {
  const genrePlatformMap = {
    'Sci-Fi': 'Amazon Prime',
    'Action': 'Netflix',
    'Drama': 'Disney+'
  };
  
  // Return a recommendation based on a simple rule set (a form of AI)
  return genrePlatformMap[movieGenre] || 'Other Platform';
}

/**
 * Simulates an AI-powered risk analysis system.
 * @param {Object} movieData - Data about the movie (revenue, piracy, etc.).
 * @returns {string} - The risk score (e.g., "Low", "Medium", "High").
 */
function getRiskScore(movieData) {
  // Simple AI logic: Check for revenue vs. a threshold and a simulated piracy flag
  const isPirated = movieData.isPirated || Math.random() < 0.1; // 10% chance of being pirated
  
  if (isPirated) {
    return 'High';
  }
  
  if (movieData.revenue < 100000) {
    return 'Medium';
  }
  
  return 'Low';
}

// Make functions available globally for cinechain.js to use
window.predictRevenue = predictRevenue;
window.getPlatformRecommendation = getPlatformRecommendation;
window.getRiskScore = getRiskScore;