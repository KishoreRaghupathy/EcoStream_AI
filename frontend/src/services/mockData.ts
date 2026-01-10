import { AirQualityData, ForecastPoint } from '@/types';

export const MOCK_HISTORY: AirQualityData[] = Array.from({ length: 24 }).map((_, i) => {
    const hour = i;
    const pm25 = 15 + Math.random() * 20 + (hour > 8 && hour < 20 ? 10 : 0); // Traffic peak
    return {
        timestamp: new Date(Date.now() - (24 - i) * 3600000).toISOString(),
        pm25,
        aqi: pm25 * 3.5, // Rough conversion
        aqi_category: pm25 < 12 ? 'Good' : pm25 < 35.4 ? 'Moderate' : 'Unhealthy',
        location: 'San Francisco',
        latitude: 37.7749 + (Math.random() - 0.5) * 0.05,
        longitude: -122.4194 + (Math.random() - 0.5) * 0.05,
        temperature: 15 + Math.sin(i / 4) * 5,
        humidity: 60 + Math.cos(i / 4) * 10,
    };
});

export const MOCK_FORECAST: ForecastPoint[] = Array.from({ length: 24 }).map((_, i) => {
    const pm25 = 20 + Math.sin(i / 3) * 10;
    return {
        timestamp: new Date(Date.now() + (i + 1) * 3600000).toISOString(),
        pm25,
        lower_bound: pm25 - 5,
        upper_bound: pm25 + 5,
    };
});

export const getMockAIResponse = (query: string) => {
    return {
        response: `This is a simulated analysis for "${query}". In demo mode, we see PM2.5 trending upwards due to simulated morning traffic. The forecast suggests clearing by afternoon.`,
        sources: ['Simulated Sensor #1', 'Historical Trend DB'],
    };
};
