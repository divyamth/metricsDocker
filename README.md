﻿# metricsDocker
## Project Information
### Frontend
The frontend is built using **NextJS**, making it easier to create routes and dynamically fetch data from the backend server.
It allows easier and more streamlined development with a better user interface that is pleasing to use. It uses the shad-cn UI library for styling configurations and Typescript for development.

The frontend uses **interface** to ensure type safety in the data structure being fetched and displayed. Using interfaces also provides other benefits like code readability and error prevention.

The **RealTimeMetrics** component contains state variables that store the data defined. Using the **useEffect** hook, data is fetched in real time with event listeners. The **EventSource** enables **Server-Sent Events (SSE)**, which is used to establish a connection to the server.
Further, functions like **fetchHealthCheck** fetch the health check status and past metrics respectively and display them in the frontend website to the user.

Using **Cleanup**, the SSE connection established earlier is closed and all the resources are cleaned up to ensure optimization.

The website displays the following information:
- CPU Usage
- Memory Usage with Total Memory and Free Memory
- Network Activity
- Per Port Network Activity
- Services running on the system
- Health Check

The entire system works in real-time with updates taking place once per second.

### Backend
The backend uses the **Python-based Flask server** that can be used to create an API to fetch the system metrics. Using **Cross-origin Resource Sharing (CORS)**, the backend can be accessed by front-end applications hosted on different domains.
The backend also has a Redis client which can be used to store system metrics persistently. There is a file logging logic used in the backend which logs the processes of the backend rotationally. Once the logs reach 1MB, they roll over, keeping a maximum of 3 backup files. This allows easier tracking of errors and exceptions along with the working. Some functions fetch and expose the system metrics and proper routing ensures that the frontend receives data in real-time.
Various API endpoints ensure different routes and systematic logging and reporting of system metrics.

### Docker
The **Docker** files provide proper configuration for containerizing the entire application. This allows for easier implementation and ensures scalability.

### Nginx
Using **Nginx** ensures that proper routing and reserve proxies can be configured. It further allows for rate limiting and securing API endpoints with proper SSL/TLS security configurations.

The entire solution presents a frontend that is user-centric and displays the metrics in an easily-readable manner. It also shows the health check along with the real-time metrics that further increase the user-friendly nature of this solution.

## Setup Instruction
- Click on the green-coloured **Code** button.
- Click on the **Download ZIP** option.
- Unzip the downloaded file using **7-Zip** or **WinRAR**.
- Install [**Docker**](https://www.docker.com/products/docker-desktop/).
- Run Docker with **administrative/superuser privileges**.
- Open the unzipped directory in VSCode or a similar code editor with a built-in terminal.
- Run **docker-compose up --build** to create a Docker container.
- Access the website by visiting **https://localhost** using your web browser.

## API Documentation
The following API endpoints perform the following
- /realmetrics - Endpoint which will record the system metrics in real-time and expose them to the frontend.
- /health - Endpoint that performs a health check of the Docker container and gives the output.

## Security Considerations
The certificates used are developer certificates resulting in a warning after deployment and access. To counter this, the certificate must be added to **Trusted Root Certification Authority**.
To do this, follow the steps:
- Press **Windows + R** on your Windows system and type in **certmgr.msc**.
- Find and right-click on **Trusted Root Certification Authority** to access a sub-menu.
- Click on **import** and select the **certificate.crt** to ensure that the system recognizes the certificate used by this program.

Another security consideration is a lack of user-authentication. This can be tackled by using **OAuth** or similar authentication services like **Clerk Authentication** in future revisions.

## Unit Tests
<a href="unit-test"><img src="images/unit-test.png" align="middle" width="1080" height="352"></a>
The Unit Tests involve testing all API endpoints for error handling and proper functioning. They ensure that all routes and APIs are properly configured and respond accordingly with no loopholes in execution to ensure proper functioning and future scalability.

## System Architecture
<a href="unit-test"><img src="images/metricsDocker_System-Architecture.png" align="middle" width="1280" height="720"></a>
