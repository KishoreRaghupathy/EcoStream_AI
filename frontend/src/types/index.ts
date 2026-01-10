export interface AirQualityData {
    timestamp: string;
    pm25: number;
    pm10?: number;
    no2?: number;
    o3?: number;
    temperature?: number;
    humidity?: number;
    location: string;
    latitude: number;
    longitude: number;
    aqi: number;
    aqi_category: 'Good' | 'Moderate' | 'Unhealthy for Sensitive Groups' | 'Unhealthy' | 'Very Unhealthy' | 'Hazardous';
}

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    sources?: string[];
}

export interface ForecastPoint {
    timestamp: string;
    pm25: number;
    lower_bound?: number;
    upper_bound?: number;
}
