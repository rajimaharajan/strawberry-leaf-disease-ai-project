import http.client
import os
import json

boundary = '----PythonFormBoundary'
file_path = 'test.jpg'
with open(file_path, 'rb') as f:
    file_data = f.read()

body = (
    b'--' + boundary.encode() + b'\r\n'
    b'Content-Disposition: form-data; name="file"; filename="' + os.path.basename(file_path).encode() + b'"\r\n'
    b'Content-Type: image/jpeg\r\n\r\n'
    + file_data + b'\r\n'
    b'--' + boundary.encode() + b'--\r\n'
)

conn = http.client.HTTPConnection('localhost', 5000)
conn.request('POST', '/predict', body, {'Content-Type': 'multipart/form-data; boundary=' + boundary})
resp = conn.getresponse()
print('Status:', resp.status)
print(json.loads(resp.read().decode()))

