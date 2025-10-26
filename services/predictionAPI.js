const API_BASE_URL = process.env.REACT_APP_PREDICTION_API_URL || 'http://localhost:5000';

export const predictionAPI = {
    predictPrices: async (productData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(productData),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Prediction API error:', error);
            throw new Error('Failed to get price predictions. Please try again.');
        }
    },

    healthCheck: async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check error:', error);
            throw new Error('Prediction service unavailable');
        }
    }
};