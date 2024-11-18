from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import psutil
from datetime import datetime
import json
import time
import redis
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
CORS(app)

# Set up Redis client
redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

# Set up logging
log_handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=3)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log_handler.setFormatter(formatter)
app.logger.addHandler(log_handler)

def sys_uptime():
    boot_time_timestamp = psutil.boot_time()
    boot_time = datetime.fromtimestamp(boot_time_timestamp)
    return str(datetime.now() - boot_time)

@app.route('/')
def home():
    app.logger.info("Home endpoint accessed.")
    return jsonify({"message": "Welcome to the System Metrics API"})

@app.route('/health', methods=['GET'])
def health_check():
    app.logger.info("Health check endpoint accessed.")
    return jsonify({"status": "healthy"})

def validate_integer_param(param, default=1):
    """Validate integer parameter in the request."""
    try:
        value = int(param)
        if value <= 0:
            raise ValueError("The value must be greater than zero.")
        return value
    except (ValueError, TypeError):
        app.logger.warning(f"Invalid value for parameter, using default: {default}")
        return default  # Return default if validation fails

@app.route('/realmetrics', methods=['GET'])
def livemetrics():
    # Get the interval parameter from the request
    interval_param = request.args.get('interval', '1')  # Default to '1' as string for validation
    
    # Validate the 'interval' parameter to control refresh time in seconds
    if not interval_param.isdigit() or int(interval_param) <= 0:
        return jsonify({"error": "Invalid interval: must be a positive integer"}), 400
    
    interval = int(interval_param)

    def generate_metrics():
        while True:
            try:
                # Get CPU, Memory, and Uptime data
                cpu_usage = psutil.cpu_percent(interval=interval)
                memory_info = psutil.virtual_memory()
                uptime = sys_uptime()

                # Get network connections
                network_connections = [
                    {
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        'status': conn.status
                    }
                    for conn in psutil.net_connections(kind='inet') if conn.status == psutil.CONN_ESTABLISHED
                ]

                # Get active ports (listening ports)
                active_ports = [
                    f"{conn.laddr.ip}:{conn.laddr.port}"
                    for conn in psutil.net_connections(kind='inet') if conn.status == psutil.CONN_LISTEN
                ]

                # Get services associated with active ports
                active_services = []
                for conn in psutil.net_connections(kind='inet'):
                    if conn.status == psutil.CONN_LISTEN:
                        try:
                            # Cross-reference connections with processes
                            for proc in psutil.process_iter(['pid', 'name']):
                                if conn.pid == proc.info['pid']:
                                    active_services.append({
                                        'pid': proc.info['pid'],
                                        'name': proc.info['name'],
                                        'port': f"{conn.laddr.ip}:{conn.laddr.port}"
                                    })
                        except psutil.NoSuchProcess:
                            continue  # If process doesn't exist, skip it
                        except psutil.AccessDenied:
                            continue  # If access to process is denied, skip it

                # Package all the metrics together
                metrics = json.dumps({
                    'cpu_usage': cpu_usage,
                    'memory': {
                        'total': memory_info.total,
                        'available': memory_info.available,
                        'used': memory_info.used,
                        'percent': memory_info.percent
                    },
                    'uptime': uptime,
                    'network_connections': network_connections,
                    'active_ports': active_ports,
                    'active_services': active_services
                })

                # Store the metrics in Redis for persistence
                store_metrics(metrics)

                # Send the data as an SSE event
                yield f"data: {metrics}\n\n"
                time.sleep(interval)  # Wait for the interval before the next update

            except Exception as e:
                app.logger.error(f"Error generating metrics: {e}")
                yield f"data: {json.dumps({'error': 'Internal server error'})}\n\n"

    app.logger.info(f"Real-time metrics endpoint accessed with interval {interval} seconds.")
    return Response(generate_metrics(), mimetype='text/event-stream')

@app.route("/historical-metrics", methods=['GET'])
def historical_metrics():
    # Get pagination parameters
    start_param = request.args.get('start', None)
    end_param = request.args.get('end', None)

    # Set default values for start and end
    start = 0 if start_param is None else validate_integer_param(start_param)
    end = -1 if end_param is None else validate_integer_param(end_param)

    try:
        metrics = redis_client.lrange("metrics", start, end)
        app.logger.info(f"Historical metrics fetched from index {start} to {end}.")
        return jsonify({"historical-metrics": metrics})
    except redis.RedisError as e:
        app.logger.error(f"Error fetching historical metrics from Redis: {e}")
        return jsonify({"error": "Failed to retrieve historical metrics"}), 500

def store_metrics(metrics):
    try:
        # Store metrics in Redis list (lpush adds to the front of the list)
        redis_client.lpush("metrics", metrics)
        # Optionally trim the list to keep only the last 100 metrics
        redis_client.ltrim("metrics", 0, 99)
        app.logger.info("Metrics stored successfully in Redis.")
    except redis.RedisError as e:
        app.logger.error(f"Error storing metrics in Redis: {e}")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", threaded=True)