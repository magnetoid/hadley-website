import json
import threading
import unittest
import urllib.request
import urllib.error
from unittest.mock import patch
import contact_server as app

class ContactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.url = 'http://127.0.0.1:%d/api/contact' % cls.server.server_port
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
    def setUp(self):
        app.requests.clear()
        self.data = dict(fname='Contact', lname='Test', email='test@example.com', msg='Integration test', enquiry='General Enquiry')
    def post(self, data=None, origin='https://www.hadleyconsulting.global'):
        req = urllib.request.Request(self.url, data=json.dumps(self.data if data is None else data).encode(), headers={'Content-Type':'application/json','Origin':origin})
        try:
            with urllib.request.urlopen(req) as r: return r.status, json.load(r)
        except urllib.error.HTTPError as r: return r.code, json.load(r)
    @patch.object(app, 'deliver')
    def test_success(self, send):
        self.assertEqual(self.post()[0], 200)
        send.assert_called_once()
    @patch.object(app, 'deliver', side_effect=RuntimeError('SMTP unavailable'))
    def test_failure_never_success(self, send):
        self.assertEqual(self.post()[0], 503)
    @patch.object(app, 'deliver')
    def test_bad_origin(self, send):
        self.assertEqual(self.post(origin='https://evil.example')[0], 403)
        send.assert_not_called()
    @patch.object(app, 'deliver')
    def test_invalid_email(self, send):
        self.data['email']='test@example.com\r\nBcc: bad@example.com'
        self.assertEqual(self.post()[0], 400)
        send.assert_not_called()
    @patch.object(app, 'deliver')
    def test_honeypot(self, send):
        self.data['website']='spam'
        self.assertEqual(self.post()[0], 400)
        send.assert_not_called()
    @patch.object(app, 'deliver')
    def test_rate_limit(self, send):
        for _ in range(5): self.assertEqual(self.post()[0], 200)
        self.assertEqual(self.post()[0], 429)
    def test_size_and_required(self):
        with self.assertRaises(ValueError): app.validate({'fname':'x'})
        self.data['msg']='x'*5001
        with self.assertRaises(ValueError): app.validate(self.data)

if __name__ == '__main__': unittest.main()
