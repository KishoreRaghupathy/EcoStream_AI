import axios from 'axios';
import { AirQualityData, ForecastPoint, ChatMessage } from '@/types';
import { MOCK_HISTORY, MOCK_FORECAST, getMockAIResponse } from './mockData';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const USE_DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === 'true';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getHistory = async (): Promise<AirQualityData[]> => {
    if (USE_DEMO_MODE) {
        // Simulate delay
        await new Promise(resolve => setTimeout(resolve, 800));
        return MOCK_HISTORY;
    }
    const response = await api.get('/api/history');
    return response.data;
};

export const getForecast = async (): Promise<ForecastPoint[]> => {
    if (USE_DEMO_MODE) {
        await new Promise(resolve => setTimeout(resolve, 800));
        return MOCK_FORECAST;
    }
    const response = await api.get('/api/forecast');
    return response.data;
};

export const sendChat = async (message: string): Promise<{ response: string; sources: string[] }> => {
    if (USE_DEMO_MODE) {
        await new Promise(resolve => setTimeout(resolve, 1500));
        return getMockAIResponse(message);
    }
    const response = await api.post('/chat/aq', { question: message, session_id: 'prod-session' }); // Assuming backend expects this
    return {
        response: response.data.answer,
        sources: response.data.sources || [],
    };
};

export { API_BASE_URL, USE_DEMO_MODE };
