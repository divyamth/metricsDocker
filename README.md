# metricsDocker

## Frontend
The frontend is built using **NextJS**, making it easier to create routes and dynamically fetch data from the backend server.
It allows easier and more streamlined development with a better user interface that is pleasing to use. It uses the shad-cn UI library for styling configurations and Typescript for development.

The frontend uses **interface** to ensure type safety in the structure of data that is being fetched and displayed. Using interfaces also provides other benefits like code readability and error prevention.

The **RealTimeMetrics** component contains state variables that store the data defined. Using the **useEffect** hook, data is fetched in real-time with event listeners. The **EventSource** enables **Server-Sent Events (SSE)** which is used to establish a connection to the server.
Further, functions like **fetchHealthCheck** and **fetchHistoricalMetrics** are used to fetch the health check status and past metrics respectively and display them in the frontend website to the user.

Using **Cleanup**, the SSE connection established earlier is closed and all the resources are cleaned up to ensure optimization.

The website displays the following information:
- CPU Usage
- Memory Usage with Total Memory and Free Memory
- Network Activity
- Per Port Network Activity
- Services running on the system
- Health Check
- Historical Metrics

The entire system works in real-time with updates taking place once per second.

## Backend
The backend uses the **Python-based Flask server** that can be used to create an API to fetch the system metrics. Using **Cross-origin Resource Sharing (CORS)**, the backend can be accessed by front-end applications hosted on different domains.
The backend also has a Redis client which can be used to store system metrics persistently. There is a file logging logic used in the backend which logs the processes of the backend rotationally. Once the logs reach 1MB, they roll over, keeping a maximum of 3 backup files. This allows easier tracking of errors and exceptions along with the working. Some functions fetch and expose the system metrics and proper routing ensures that the frontend receives data in real-time.
Various API endpoints ensure different routes and systematic logging and reporting of system metrics.

## Docker
The **Docker** files provide proper configuration for containerizing the entire application. This allows for easier implementation and ensures scalability.

## Nginx
Using **Nginx** ensures that proper routing and reserve proxies can be configured. It further allows for rate limiting and securing API endpoints with proper SSL/TLS security configurations.

The entire solution presents a frontend that is user-centric and displays the metrics in an easily-readable manner. It also shows the health checks and historical metrics along with the real-time metrics that further increases the user-friendly nature of this solution.

## Unit Tests
<a href="unit test"><img src="https://github.com/divyamth/metricsDocker/images/unit-test.png" align="middle" width="2336" height="352"></a>
