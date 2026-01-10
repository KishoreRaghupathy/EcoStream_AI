'use client';

import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { format } from 'date-fns';
import { AirQualityData, ForecastPoint } from '@/types';

interface AnalyticsChartsProps {
    history: AirQualityData[];
    forecast: ForecastPoint[];
}

export function AnalyticsCharts({ history, forecast }: AnalyticsChartsProps) {
    // Combine data for visualization
    const combinedData = [
        ...history.map(d => ({
            timestamp: d.timestamp,
            pm25: d.pm25,
            type: 'history'
        })),
        ...forecast.map(d => ({
            timestamp: d.timestamp,
            pm25_forecast: d.pm25,
            lower_bound: d.lower_bound,
            upper_bound: d.upper_bound,
            type: 'forecast'
        }))
    ];

    const now = new Date().toISOString();

    return (
        <Card className="col-span-4">
            <CardHeader>
                <CardTitle className="text-xl">PM2.5 Conc. & Forecast (µg/m³)</CardTitle>
                <CardDescription>
                    Historical data (past 24h) and AI-driven forecast (next 24h).
                </CardDescription>
            </CardHeader>
            <CardContent className="pl-2">
                <ResponsiveContainer width="100%" height={350}>
                    <AreaChart data={combinedData}>
                        <defs>
                            <linearGradient id="colorPm25" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <XAxis
                            dataKey="timestamp"
                            tickFormatter={(str) => format(new Date(str), 'HH:mm')}
                            stroke="#888888"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                            minTickGap={30}
                        />
                        <YAxis
                            stroke="#888888"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(value) => `${value}`}
                        />
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                        <Tooltip
                            content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                    const data = payload[0].payload;
                                    return (
                                        <div className="rounded-lg border bg-background p-2 shadow-sm">
                                            <div className="grid grid-cols-2 gap-2">
                                                <div className="flex flex-col">
                                                    <span className="text-[0.70rem] uppercase text-muted-foreground">
                                                        Time
                                                    </span>
                                                    <span className="font-bold text-muted-foreground">
                                                        {format(new Date(data.timestamp), 'MMM d, HH:mm')}
                                                    </span>
                                                </div>
                                                <div className="flex flex-col">
                                                    <span className="text-[0.70rem] uppercase text-muted-foreground">
                                                        PM2.5
                                                    </span>
                                                    <span className="font-bold">
                                                        {data.pm25 ? data.pm25.toFixed(1) : data.pm25_forecast?.toFixed(1)}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                }
                                return null;
                            }}
                        />
                        <ReferenceLine x={now} stroke="red" strokeDasharray="3 3" label="Now" />
                        <Area
                            type="monotone"
                            dataKey="pm25"
                            stroke="#10b981"
                            fillOpacity={1}
                            fill="url(#colorPm25)"
                            strokeWidth={2}
                        />
                        <Area
                            type="monotone"
                            dataKey="pm25_forecast"
                            stroke="#3b82f6"
                            fillOpacity={1}
                            fill="url(#colorForecast)"
                            strokeDasharray="5 5"
                            strokeWidth={2}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
