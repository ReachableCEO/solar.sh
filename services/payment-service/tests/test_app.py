import unittest
import json
from unittest import mock
import os
import stripe # Added this line

# Mock environment variables before importing app
with mock.patch.dict(os.environ, {
    'STRIPE_SECRET_KEY': 'sk_test_mock',
    'STRIPE_WEBHOOK_SECRET': 'whsec_mock',
    'DATABASE_URL': 'postgresql://user:password@host:5432/testdb',
    'STRIPE_PRODUCT_PRICE_ID': 'price_12345',
}):
    from app import app, get_db_connection

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        app.testing = True

    @mock.patch('stripe.checkout.Session.create')
    def test_checkout(self, mock_stripe_checkout_session_create):
        mock_stripe_checkout_session_create.return_value = mock.Mock(url='https://checkout.stripe.com/mock_session')

        response = self.app.post('/api/checkout',
                                   data=json.dumps({"project_id": "test_project_123"}),
                                   content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertIn('checkout_url', data)
        self.assertEqual(data['checkout_url'], 'https://checkout.stripe.com/mock_session')

        mock_stripe_checkout_session_create.assert_called_once_with(
            line_items=[
                {
                    'price': 'price_12345',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='https://example.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://example.com/cancel',
            client_reference_id='test_project_123',
            metadata={'project_id': 'test_project_123'}
        )

    def test_checkout_missing_project_id(self):
        response = self.app.post('/api/checkout',
                                   data=json.dumps({}),
                                   content_type='application/json')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'project_id is required')

    @mock.patch('stripe.Webhook.construct_event')
    @mock.patch('app.get_db_connection')
    def test_stripe_webhook_checkout_completed(self, mock_get_db_connection, mock_stripe_webhook_construct_event):
        # Mock Stripe event
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'client_reference_id': 'test_project_456',
                    'id': 'cs_test_123',
                }
            }
        }
        mock_stripe_webhook_construct_event.return_value = mock_event

        # Mock DB connection and cursor
        mock_conn = mock.Mock()
        mock_cur = mock.Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_db_connection.return_value = mock_conn

        response = self.app.post('/webhooks/stripe',
                                   headers={'stripe-signature': 'mock_signature'},
                                   data=json.dumps({"id": "evt_test", "type": "checkout.session.completed"}),
                                   content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

        mock_stripe_webhook_construct_event.assert_called_once()
        mock_get_db_connection.assert_called_once()
        mock_cur.execute.assert_called_once_with(
            "UPDATE projects SET status = %s WHERE id = %s",
            ('paid', 'test_project_456')
        )
        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @mock.patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_invalid_signature(self, mock_stripe_webhook_construct_event):
        mock_stripe_webhook_construct_event.side_effect = stripe.error.SignatureVerificationError('Invalid signature', 'header', 'payload')

        response = self.app.post('/webhooks/stripe',
                                   headers={'stripe-signature': 'invalid_signature'},
                                   data=json.dumps({"id": "evt_test", "type": "checkout.session.completed"}),
                                   content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_data(as_text=True), 'Invalid signature')

    @mock.patch('app.get_db_connection')
    def test_health_check_db_success(self, mock_get_db_connection):
        mock_conn = mock.Mock()
        mock_get_db_connection.return_value = mock_conn

        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'OK')
        mock_get_db_connection.assert_called_once()
        mock_conn.close.assert_called_once()

    @mock.patch('app.get_db_connection')
    def test_health_check_db_failure(self, mock_get_db_connection):
        mock_get_db_connection.side_effect = Exception("DB connection error")

        response = self.app.get('/health')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_data(as_text=True), 'Database connection failed')
        mock_get_db_connection.assert_called_once()

if __name__ == '__main__':
    unittest.main()
