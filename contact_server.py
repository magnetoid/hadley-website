"""Fixed-recipient contact delivery. No visitor content is logged or persisted."""
import json
import os
import re
import smtplib
import ssl
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from collections import OrderedDict
from threading import Lock
import time

RECIPIENT = 'jgunn@hadleyconsulting.global'
ORIGINS = {'https://www.hadleyconsulting.global', 'https://hadleyconsulting.global'}
AREAS = {'Management Consulting', 'Public & Corporate Affairs', 'Strategic Business Development', 'Project & Transaction Advisory', 'Defence & Security', 'General Enquiry'}
lock = Lock()
requests = OrderedDict()


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Invalid form data.')
    limits = {'fname': 100, 'lname': 100, 'org': 200, 'email': 254, 'enquiry': 100, 'msg': 5000, 'website': 200}
    result = {}
    for key, limit in limits.items():
        value = data.get(key, '')
        if not isinstance(value, str) or len(value) > limit or '\x00' in value:
            raise ValueError('Please check the form fields.')
        result[key] = value.strip()
    if not all(result[k] for k in ('fname', 'lname', 'email', 'msg')):
        raise ValueError('Please enter your name, email address and enquiry.')
    if not re.fullmatch(r'[^\s@\r\n]+@[^\s@\r\n]+\.[^\s@\r\n]+', result['email']):
        raise ValueError('Please enter a valid email address.')
    if any('\r' in result[k] or '\n' in result[k] for k in ('fname', 'lname', 'email', 'enquiry', 'org')):
        raise ValueError('Please check the form fields.')
    if result['enquiry'] and result['enquiry'] not in AREAS:
        raise ValueError('Please select a valid practice area.')
    return result


def deliver(data):
    message = EmailMessage()
    message['From'] = 'Hadley Website <jgunn@hadleyconsulting.global>'
    message['To'] = RECIPIENT
    message['Reply-To'] = data['email']
    message['Subject'] = 'Website enquiry: ' + (data['enquiry'] or 'General Enquiry')
    message.set_content('\n'.join([
        'New enquiry from the Hadley website.', '',
        'Name: ' + data['fname'] + ' ' + data['lname'],
        'Organisation: ' + data['org'], 'Email: ' + data['email'],
        'Practice area: ' + data['enquiry'], '', data['msg']]))
    # Recipient is a local mailbox on this server. Never permit arbitrary recipients.
    with smtplib.SMTP(os.getenv('SMTP_HOST', 'tetra.imbamarketing.com'), 587, timeout=15) as smtp:
        smtp.ehlo()
        smtp.starttls(context=ssl.create_default_context())
        smtp.ehlo()
        smtp.login(RECIPIENT, os.environ['SMTP_PASSWORD'])
        refused = smtp.send_message(message)
        if refused:
            raise smtplib.SMTPException('Recipient refused')


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, status, message):
        body = json.dumps({'ok': status == 200, 'message': message}).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.respond(200 if self.path == '/health' else 405, '')

    def do_POST(self):
        if self.path != '/api/contact':
            return self.respond(404, 'Not found.')
        if self.headers.get('Origin') not in ORIGINS:
            return self.respond(403, 'Please submit from the Hadley website.')
        if self.headers.get_content_type() != 'application/json':
            return self.respond(415, 'JSON required.')
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            return self.respond(400, 'Invalid request.')
        if length <= 0 or length > 16384:
            return self.respond(413, 'Invalid request size.')
        ip = self.headers.get('X-Client-IP', self.client_address[0])
        now = time.monotonic()
        with lock:
            previous = [t for t in requests.pop(ip, []) if now - t < 3600]
            if len(previous) >= 5:
                requests[ip] = previous
                return self.respond(429, 'Too many attempts. Please email us directly or try again later.')
            requests[ip] = previous + [now]
            if len(requests) > 10000:
                requests.popitem(last=False)
        try:
            data = validate(json.loads(self.rfile.read(length)))
        except (ValueError, UnicodeError):
            return self.respond(400, 'Please check your name, email address and enquiry.')
        if data['website']:
            return self.respond(400, 'Unable to submit this enquiry.')
        try:
            deliver(data)
        except Exception:
            print('contact_delivery_failed', flush=True)
            return self.respond(503, 'Unable to send right now. Please email jgunn@hadleyconsulting.global directly.')
        self.respond(200, 'Enquiry accepted.')


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8000), Handler).serve_forever()
