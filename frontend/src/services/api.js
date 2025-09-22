import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 404) {
      throw new Error('URL not found');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data.detail || 'Bad request');
    } else if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.');
    }
    throw error;
  }
);

export const urlService = {
  // Create a new shortened URL
  createUrl: async (urlData) => {
    const response = await api.post('/urls/', urlData);
    return response.data;
  },

  // Get URL information
  getUrlInfo: async (shortCode) => {
    const response = await api.get(`/urls/${shortCode}/info`);
    return response.data;
  },

  // Update URL
  updateUrl: async (urlId, urlData) => {
    const response = await api.put(`/urls/${urlId}`, urlData);
    return response.data;
  },

  // Delete URL
  deleteUrl: async (urlId) => {
    const response = await api.delete(`/urls/${urlId}`);
    return response.data;
  },

  // Get URL analytics
  getAnalytics: async (urlId) => {
    const response = await api.get(`/urls/${urlId}/analytics`);
    return response.data;
  },
};

export default api;