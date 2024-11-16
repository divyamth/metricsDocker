import unittest
from unittest.mock import patch, MagicMock
from app import app, redis_client, sys_uptime, store_metrics


class TestSystemMetricsAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.psutil')
    def test_home_route(self, mock_psutil):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Welcome to the System Metrics API"})

    @patch('app.psutil')
    @patch('app.sys_uptime', return_value="1 day, 2:00:00")
    def test_livemetrics(self, mock_uptime, mock_psutil):
        mock_psutil.cpu_percent.return_value = 50
        mock_psutil.virtual_memory.return_value = MagicMock(
            total=16 * 1024 * 1024 * 1024,
            available=8 * 1024 * 1024 * 1024,
            used=8 * 1024 * 1024 * 1024,
            percent=50
        )
        mock_psutil.net_connections.return_value = []

        # Simulate request
        response = self.app.get('/realmetrics', headers={'Accept': 'text/event-stream'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/event-stream', response.content_type)

        # Assert SSE data format
        for line in response.response:
            self.assertTrue(line.startswith(b"data:") or line == b'\n')
            break  # Only check the first SSE message for simplicity

    @patch.object(redis_client, 'lrange', return_value=['{"cpu_usage": 20, "memory": {}}'])
    def test_historical_metrics(self, mock_lrange):
        response = self.app.get('/historical-metrics')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json,
            {"historical-metrics": ['{"cpu_usage": 20, "memory": {}}']}
        )

    @patch.object(redis_client, 'lpush')
    @patch.object(redis_client, 'ltrim')
    def test_store_metrics(self, mock_ltrim, mock_lpush):
        metrics_data = '{"cpu_usage": 20, "memory": {}}'
        store_metrics(metrics_data)
        mock_lpush.assert_called_once_with("metrics", metrics_data)
        mock_ltrim.assert_called_once_with("metrics", 0, 99)

    @patch('app.psutil.boot_time', return_value=1684275600.0)  # Mock a specific boot time
    def test_sys_uptime(self, mock_boot_time):
        uptime = sys_uptime()
        self.assertIsInstance(uptime, str)
        self.assertIn("days", uptime)  # Check if uptime includes days/hours

    def test_error_handling(self):
        # Test non-existing route
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
