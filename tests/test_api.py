#!/usr/bin/env python3
"""
UNITPLAST API Tests - Unit & Integration Tests
Tests all v1 endpoints for correctness and performance
"""

import unittest
import json
from datetime import datetime
from app.app import create_app

class TestAPIEndpoints(unittest.TestCase):
    """Test API v1 endpoints"""

    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.client = self.app.test_client()

    def test_api_health_check(self):
        """Test API health endpoint"""
        response = self.client.get('/api/v1/status')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'operational')
        self.assertIn('endpoints', data)

    def test_get_calculations(self):
        """Test GET /api/v1/calculations"""
        response = self.client.get('/api/v1/calculations')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(len(data['calculations']), 0)

        # Check calculation structure
        calc = data['calculations'][0]
        self.assertIn('id', calc)
        self.assertIn('type', calc)
        self.assertIn('price', calc)
        self.assertIn('status', calc)

    def test_get_specific_calculation(self):
        """Test GET /api/v1/calculations/<id>"""
        response = self.client.get('/api/v1/calculations/2506')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('calculation', data)
        self.assertEqual(data['calculation']['id'], 2506)

    def test_create_calculation(self):
        """Test POST /api/v1/calculations"""
        payload = {'quantity': 100}
        response = self.client.post('/api/v1/calculations',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('calculation_id', data)
        self.assertGreater(data['price'], 0)

    def test_get_orders(self):
        """Test GET /api/v1/orders"""
        response = self.client.get('/api/v1/orders')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(len(data['orders']), 0)
        self.assertIn('statuses', data)

        # Check order structure
        order = data['orders'][0]
        self.assertIn('id', order)
        self.assertIn('status', order)
        self.assertIn('price', order)
        self.assertIn('progress', order)

    def test_get_orders_filter_by_status(self):
        """Test GET /api/v1/orders?status=<status>"""
        response = self.client.get('/api/v1/orders?status=in_progress')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        # All returned orders should have in_progress status
        for order in data['orders']:
            self.assertEqual(order['status'], 'in_progress')

    def test_get_specific_order(self):
        """Test GET /api/v1/orders/<id>"""
        response = self.client.get('/api/v1/orders/2506')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('order', data)
        self.assertEqual(data['order']['id'], 2506)

    def test_create_order(self):
        """Test POST /api/v1/orders"""
        payload = {'calculation_id': 2506}
        response = self.client.post('/api/v1/orders',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('order_id', data)

    def test_get_materials(self):
        """Test GET /api/v1/materials"""
        response = self.client.get('/api/v1/materials')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('materials', data)
        # Check all three types exist
        self.assertIn('UP', data['materials'])
        self.assertIn('UF', data['materials'])
        self.assertIn('UM', data['materials'])

    def test_get_analytics_dashboard(self):
        """Test GET /api/v1/analytics/dashboard"""
        response = self.client.get('/api/v1/analytics/dashboard')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('metrics', data)
        self.assertIn('by_type', data)

        # Check metrics
        metrics = data['metrics']
        self.assertGreater(metrics['revenue'], 0)
        self.assertGreater(metrics['orders'], 0)
        self.assertGreaterEqual(metrics['production_efficiency'], 0)
        self.assertLessEqual(metrics['production_efficiency'], 100)

    def test_get_production_analytics(self):
        """Test GET /api/v1/analytics/production"""
        response = self.client.get('/api/v1/analytics/production')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('lines', data)
        self.assertGreater(len(data['lines']), 0)

    def test_get_team_members(self):
        """Test GET /api/v1/team/members"""
        response = self.client.get('/api/v1/team/members')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('team', data)
        self.assertGreater(len(data['team']), 0)

        # Check team member structure
        member = data['team'][0]
        self.assertIn('id', member)
        self.assertIn('name', member)
        self.assertIn('role', member)
        self.assertIn('status', member)

    def test_sync_1c(self):
        """Test POST /api/v1/sync/1c"""
        response = self.client.post('/api/v1/sync/1c')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('synced', data)
        self.assertGreater(data['synced']['documents'], 0)

    def test_sync_1c_status(self):
        """Test GET /api/v1/sync/1c/status"""
        response = self.client.get('/api/v1/sync/1c/status')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('status', data)

    def test_export_orders_excel(self):
        """Test POST /api/v1/export/orders/xlsx"""
        response = self.client.post('/api/v1/export/orders/xlsx')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('filename', data)
        self.assertTrue(data['filename'].endswith('.xlsx'))

    def test_export_orders_csv(self):
        """Test POST /api/v1/export/orders/csv"""
        response = self.client.post('/api/v1/export/orders/csv')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['filename'].endswith('.csv'))

    def test_export_invalid_format(self):
        """Test POST /api/v1/export/orders with invalid format"""
        response = self.client.post('/api/v1/export/orders/invalid')
        self.assertEqual(response.status_code, 400)

    def test_health_endpoint(self):
        """Test legacy /health endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'OK')

    def test_landing_page(self):
        """Test landing page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('UNITPLAST', response.get_data(as_text=True))

    def test_mini_app(self):
        """Test mini app loads"""
        response = self.client.get('/app/miniapp')
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        self.assertIn('UNITPLAST AI', data)


class TestAPIPerformance(unittest.TestCase):
    """Test API performance"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_api_response_time(self):
        """Test API responds within 500ms"""
        import time
        start = time.time()
        self.client.get('/api/v1/status')
        elapsed = (time.time() - start) * 1000
        self.assertLess(elapsed, 500)

    def test_calculations_endpoint_response_time(self):
        """Test calculations endpoint responds within 500ms"""
        import time
        start = time.time()
        self.client.get('/api/v1/calculations')
        elapsed = (time.time() - start) * 1000
        self.assertLess(elapsed, 500)


if __name__ == '__main__':
    unittest.main()
