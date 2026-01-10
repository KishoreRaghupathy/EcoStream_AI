'use client';

import * as React from 'react';
import Map, { Source, Layer, NavigationControl, Popup } from 'react-map-gl/maplibre';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { AirQualityData } from '@/types';
import { useTheme } from 'next-themes';

interface AirQualityMapProps {
    data: AirQualityData[];
}

export function AirQualityMap({ data }: AirQualityMapProps) {
    const [popupInfo, setPopupInfo] = React.useState<AirQualityData | null>(null);

    const geoJsonData = React.useMemo(() => {
        return {
            type: 'FeatureCollection',
            features: data.map((d) => ({
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [d.longitude, d.latitude],
                },
                properties: {
                    pm25: d.pm25,
                    aqi: d.aqi,
                    ...d,
                },
            })),
        };
    }, [data]);

    const heatmapLayer = {
        id: 'heatmap',
        type: 'heatmap',
        paint: {
            'heatmap-weight': [
                'interpolate',
                ['linear'],
                ['get', 'pm25'],
                0, 0,
                50, 1
            ],
            'heatmap-intensity': [
                'interpolate',
                ['linear'],
                ['zoom'],
                0, 1,
                9, 3
            ],
            'heatmap-color': [
                'interpolate',
                ['linear'],
                ['heatmap-density'],
                0, 'rgba(33,102,172,0)',
                0.2, 'rgb(103,169,207)',
                0.4, 'rgb(209,229,240)',
                0.6, 'rgb(253,219,199)',
                0.8, 'rgb(239,138,98)',
                1, 'rgb(178,24,43)'
            ],
            'heatmap-radius': [
                'interpolate',
                ['linear'],
                ['zoom'],
                0, 2,
                9, 20
            ],
            'heatmap-opacity': 0.8,
        },
    };

    const circleLayer = {
        id: 'circle',
        type: 'circle',
        paint: {
            'circle-radius': 5,
            'circle-color': [
                'interpolate',
                ['linear'],
                ['get', 'pm25'],
                0, '#00ff00',
                12, '#ffff00',
                35, '#ff9900',
                55, '#ff0000',
                150, '#660099',
                250, '#7e0023'
            ],
            'circle-stroke-color': 'white',
            'circle-stroke-width': 1,
            'circle-opacity': 0.8
        }
    };

    return (
        <div className="h-[400px] w-full rounded-xl overflow-hidden shadow-sm border relative">
            <Map
                initialViewState={{
                    longitude: -122.4194,
                    latitude: 37.7749,
                    zoom: 10
                }}
                mapLib={maplibregl}
                style={{ width: '100%', height: '100%' }}
                mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"

            >
                <NavigationControl position="top-right" />
                <Source type="geojson" data={geoJsonData as any}>
                    <Layer {...heatmapLayer as any} />
                    <Layer {...circleLayer as any} />
                </Source>

                {/* Interactive Popup Logic could happen here with onClick handlers on layers */}
            </Map>
            <div className="absolute bottom-4 right-4 bg-background/90 p-2 rounded-md text-xs border shadow-sm">
                <div className="font-semibold mb-1">PM2.5 Heatmap</div>
                <div className="flex items-center gap-1">
                    <span className="w-3 h-3 bg-blue-500 rounded-full"></span> Low
                    <span className="w-3 h-3 bg-red-500 rounded-full ml-2"></span> High
                </div>
            </div>
        </div>
    );
}
