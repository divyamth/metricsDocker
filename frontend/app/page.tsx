'use client'

import { useEffect, useState } from "react";

interface MetricData {
    cpu_usage: number;
    memory: {
        total: number;
        available: number;
        used: number;
        percent: number;
    };
    uptime: string;
    network_connections: Array<{
        local_address: string;
        remote_address: string | null;
        status: string;
    }>;
    active_ports: string[];
    active_services: Array<{
        pid: number;
        name: string;
        port: string;
    }>;
}

interface HealthCheckData{
    status: string;
    details: Record<string, string>;
}

// interface HistoricalMetricData{
//     timestamp: string;
//     cpu_usage: number;
//     memory_percent: number;
// }

// interface HistoricalMetricRaw{
//     timestamp: string;
//     cpu_usage: number;
//     memory_percent: number;
// }

const RealTimeMetrics = () => {
    const [metrics, setMetrics] = useState<MetricData | null>(null);
    const [healthCheck, setHealthCheck] = useState<HealthCheckData | null>(null);
    // const [historicalMetrics, setHistoricalMetrics] = useState<HistoricalMetricData[]>([]);

    useEffect(() => {
        // Create an EventSource to listen for updates from Flask
        const eventSource = new EventSource(`${process.env.NEXT_PUBLIC_BACKEND_URL}/realmetrics`);

        eventSource.onopen = () => {
            console.log("EventSource connection opened.");
        };

        eventSource.onmessage = (event) => {
            console.log("Received event data:", event.data);
            try {
                const data: MetricData = JSON.parse(event.data);
                setMetrics(data);
                console.log("Metrics updated:", data);
            } catch (error) {
                console.error("Error parsing SSE data:", error);
            }
        };

        eventSource.onerror = (error) => {
            console.error("EventSource failed:", error);
            eventSource.close();
        };

        const fetchHealthCheck = async () => {
            try{
                const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/health`);
                const data: HealthCheckData = await response.json();
                setHealthCheck(data);
            }catch(error){
                console.error('Error fetching health check data:', error);
            }
        };

        // const fetchHistoricalMetrics = async () => {
        //     try{
        //         const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/historical-metrics`);
        //         if(!response.ok){
        //             throw new Error('Failed to fetch historical metrics');
        //         }
        //         const data = await response.json();
        //         const metrics = data["historical-metrics"].map((metric: string) => {
        //             const parsedMetric: HistoricalMetricRaw = JSON.parse(metric);
        //             return{
        //                 timestamp: parsedMetric.timestamp,
        //                 cpu_usage: parsedMetric.cpu_usage,
        //                 memory_percent: parsedMetric.memory_percent,
        //             };
        //         });
        //         setHistoricalMetrics(metrics);
        //     } catch(error){
        //         console.error('Error fetching historical metrics:', error);
        //     }
        // };

        fetchHealthCheck();
        // fetchHistoricalMetrics();

        //Cleanup: Close the connection when the component unmounts
        return () => {
            eventSource.close();
        };
    }, []);

    if (!metrics) return <p>Loading metrics...</p>;

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <div className="w-full max-w-6xl bg-white rounded-lg shadow-lg p-8 space-y-6">
                <h2 className="text-2xl font-bold text-center text-gray-700">Real-Time System Metrics</h2>
                <div className="flex flex-wrap justify-between gap-6">
                    {/* CPU Usage */}
                    <div className="flex-1 border p-4 rounded-lg bg-gray-50 shadow">
                        <p className="text-lg font-semibold text-gray-800">CPU Usage</p>
                        <p className="text-2xl font-bold text-indigo-600">{metrics.cpu_usage}%</p>
                    </div>

                    {/* Memory Usage */}
                    <div className="flex-1 border p-4 rounded-lg bg-gray-50 shadow">
                        <p className="text-lg font-semibold text-gray-800">Memory Usage</p>
                        <p className="text-2xl font-bold text-indigo-600">{metrics?.memory?.percent || 0    }%</p>
                        <p className="text-sm text-gray-600">Total: {(metrics.memory.total / (1024 ** 3)).toFixed(2)} GB</p>
                        <p className="text-sm text-gray-600">Available: {(metrics.memory.available / (1024 ** 3)).toFixed(2)} GB</p>
                    </div>

                    {/* System Uptime */}
                    <div className="flex-1 border p-4 rounded-lg bg-gray-50 shadow">
                        <p className="text-lg font-semibold text-gray-800">System Uptime</p>
                        <p className="text-2xl font-bold text-indigo-600">{metrics.uptime}</p>
                    </div>
                </div>

                <div className="flex flex-wrap justify-between gap-6 mt-6">
                    {/* Network Connections */}
                    <div className="flex-1 border p-4 rounded-lg bg-gray-50 shadow">
                        <p className="text-lg font-semibold text-gray-800">Network Connections</p>
                        {metrics.network_connections.length > 0 ? (
                            <ul className="space-y-2 mt-2">
                                {metrics.network_connections.map((conn, index) => (
                                    <li key={index} className="p-2 bg-gray-100 rounded">
                                        <p><strong>Local:</strong> {conn.local_address}</p>
                                        <p><strong>Remote:</strong> {conn.remote_address || "N/A"}</p>
                                        <p><strong>Status:</strong> {conn.status}</p>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="text-gray-600">No active network connections</p>
                        )}
                    </div>

                    {/* Active Ports */}
                    <div className="flex-1 border p-4 rounded-lg bg-gray-50 shadow">
                        <p className="text-lg font-semibold text-gray-800">Active Ports</p>
                        {metrics.active_ports.length > 0 ? (
                            <ul className="space-y-2 mt-2">
                                {metrics.active_ports.map((port, index) => (
                                    <li key={index} className="p-2 bg-gray-100 rounded">
                                        {port}
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="text-gray-600">No active ports</p>
                        )}
                    </div>

                    {/* Active Services */}
                    <div className="flex-1 border p-4 rounded-lg bg-gray-50 shadow">
                        <p className="text-lg font-semibold text-gray-800">Active Services</p>
                        {metrics.active_services.length > 0 ? (
                            <ul className="space-y-2 mt-2">
                                {metrics.active_services.map((service, index) => (
                                    <li key={index} className="p-2 bg-gray-100 rounded">
                                        <p><strong>PID:</strong> {service.pid}</p>
                                        <p><strong>Name:</strong> {service.name}</p>
                                        <p><strong>Port:</strong> {service.port}</p>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="text-gray-600">No active services</p>
                        )}
                    </div>

                    {/* Health Check */}
                    <div className="border-t pt-6">
                        <h3 className="text-xl font-bold text-gray-700">Health Check</h3>
                        {healthCheck ? (
                            <div className={`p-4 rounded-lg ${healthCheck.status === 'healthy' ? 'bg-green-100' : 'bg-red-100'}`}>
                                <p className="text-lg font-semibold">{healthCheck.status.toUpperCase()}</p>
                                {healthCheck.details && Object.keys(healthCheck.details).length > 0 ? (
                                <ul className="mt-2">
                                    {Object.entries(healthCheck.details).map(([key, value], index) => (
                                        <li key={index} className="text-sm">
                                            <strong>{key}:</strong> {value}
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="text-sm text-gray-600">No additional details available.</p>
                            )}
                        </div>
                    ) : (
                            <p>Loading health check data...</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RealTimeMetrics;