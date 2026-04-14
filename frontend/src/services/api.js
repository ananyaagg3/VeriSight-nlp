import axios from 'axios';

// Get API URL from environment or fallback
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30 seconds for model inference
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        // Log requests in development
        if (import.meta.env.DEV) {
            console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Handle common errors
        if (error.response) {
            // Server responded with error
            const status = error.response.status;
            const message = error.response.data?.detail || error.message;

            switch (status) {
                case 400:
                    console.error('Bad Request:', message);
                    break;
                case 404:
                    console.error('Not Found:', message);
                    break;
                case 500:
                    console.error('Server Error:', message);
                    break;
                case 429:
                    console.error('Rate limit exceeded');
                    break;
                default:
                    console.error('API Error:', message);
            }
        } else if (error.request) {
            // Request made but no response
            console.error('Network Error: No response from server');
        } else {
            // Error in request setup
            console.error('Request Error:', error.message);
        }

        return Promise.reject(error);
    }
);

// API Service
const api = {
    // Analyze text
    analyzeText: async (text, analyzeImage = false, imageUrl = null) => {
        const response = await apiClient.post('/api/analysis/analyze-text', {
            text,
            analyze_image: analyzeImage,
            image_url: imageUrl,
        });
        return response.data;
    },

    // Upload and analyze image
    analyzeImage: async (formData) => {
        const response = await apiClient.post('/api/analysis/analyze-image', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    // Analyze URL
    analyzeUrl: async (url) => {
        const response = await apiClient.post('/api/analysis/analyze-url', {
            url,
        });
        return response.data;
    },

    // Submit feedback
    submitFeedback: async (analysisId, rating, isCorrect, comment = '') => {
        const response = await apiClient.post('/api/analysis/feedback', {
            analysis_id: analysisId,
            rating,
            is_correct: isCorrect,
            comment,
        });
        return response.data;
    },

    // Get analysis history
    getHistory: async (limit = 10) => {
        const response = await apiClient.get('/api/analysis/history', {
            params: { limit },
        });
        return response.data;
    },

    // Health check
    healthCheck: async () => {
        const response = await apiClient.get('/health');
        return response.data;
    },

    // Get system info
    getSystemInfo: async () => {
        const response = await apiClient.get('/');
        return response.data;
    },
};

export default api;
export { API_BASE_URL };
