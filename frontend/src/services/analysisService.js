import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const analyzeText = async (text, imageData = null) => {
    try {
        const requestBody = {
            text,
            analyze_image: !!imageData,
        };

        // Add image URL if provided (base64 data URL)
        if (imageData) {
            requestBody.image_url = imageData;
        }

        const response = await api.post('/api/analysis/analyze-text', requestBody);
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'Analysis failed');
    }
};

export const submitFeedback = async (analysisId, rating, comment, isCorrect) => {
    try {
        const response = await api.post('/api/analysis/feedback', {
            analysis_id: analysisId,
            rating,
            comment,
            is_correct: isCorrect,
        });
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'Feedback submission failed');
    }
};

export const getHistory = async (limit = 10) => {
    try {
        const response = await api.get(`/api/analysis/history?limit=${limit}`);
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'Failed to fetch history');
    }
};

export const clearHistory = async () => {
    try {
        const response = await api.delete('/api/analysis/clear-history');
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'Failed to clear history');
    }
};

export default api;
