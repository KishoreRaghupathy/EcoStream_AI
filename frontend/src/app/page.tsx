'use client';

import { useQuery } from '@tanstack/react-query';
import { AirQualityMap } from '@/components/map/AirQualityMap';
import { AnalyticsCharts } from '@/components/dashboard/AnalyticsCharts';
import { AIAnalyst } from '@/components/chat/AIAnalyst';
import { getHistory, getForecast } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle, Loader2 } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function Home() {
  const {
    data: historyData,
    isLoading: historyLoading,
    error: historyError
  } = useQuery({ queryKey: ['history'], queryFn: getHistory });

  const {
    data: forecastData,
    isLoading: forecastLoading
  } = useQuery({ queryKey: ['forecast'], queryFn: getForecast });

  const isLoading = historyLoading || forecastLoading;

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2 text-lg font-medium text-muted-foreground">Loading EcoStream...</span>
      </div>
    );
  }

  if (historyError) {
    return (
      <div className="container mx-auto p-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            Failed to load air quality data. Please try again later.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const latestReading = historyData?.[0]; // Assuming sorted descending or just first
  const currentAQI = latestReading?.aqi || 0;
  const currentPM25 = latestReading?.pm25 || 0;

  return (
    <div className="container mx-auto p-4 md:p-6 space-y-6">

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current AQI</CardTitle>
            <div className={`h-4 w-4 rounded-full ${currentAQI < 50 ? 'bg-green-500' : 'bg-yellow-500'}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentAQI.toFixed(0)}</div>
            <p className="text-xs text-muted-foreground">{latestReading?.aqi_category}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">PM2.5 Level</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentPM25.toFixed(1)} µg/m³</div>
            <p className="text-xs text-muted-foreground">Updated just now</p>
          </CardContent>
        </Card>
        {/* Add more KPIs if needed */}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Map Area - Spans 2 cols */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="overflow-hidden">
            <CardHeader className="pb-0">
              <CardTitle>Live Monitor</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <AirQualityMap data={historyData || []} />
            </CardContent>
          </Card>

          <div className="w-full">
            <AnalyticsCharts
              history={historyData || []}
              forecast={forecastData || []}
            />
          </div>
        </div>

        {/* Sidebar / Analyst Panel */}
        <div className="space-y-6">
          <AIAnalyst />

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Ingestion</span>
                  <span className="text-green-500 font-medium">Active</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Forecasting</span>
                  <span className="text-green-500 font-medium">Synced</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Last Drift Check</span>
                  <span>2 mins ago</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
