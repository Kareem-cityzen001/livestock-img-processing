import base64
import sys
import io
try:
    import requests
except Exception:
    requests = None
import urllib.request
import uuid

PNG_1x1_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)

def make_image(path='test_img.png'):
    data = base64.b64decode(PNG_1x1_BASE64)
    with open(path, 'wb') as f:
        f.write(data)
    return path


def post_image(url='http://127.0.0.1:5000/upload', img_path='test_img.png'):
    if requests:
        try:
            with open(img_path, 'rb') as f:
                files = {'image': (img_path, f, 'image/png')}
                data = {'behavior_description': 'Automated test upload'}
                resp = requests.post(url, files=files, data=data, timeout=20)
                print('Status:', resp.status_code)
                print('Headers:', resp.headers.get('content-type'))
                print('Response text:', resp.text[:1000])
        except Exception as e:
            print('Request failed (requests):', e)
    else:
        # Use urllib as fallback
        boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
        CRLF = '\r\n'
        with open(img_path, 'rb') as f:
            img_data = f.read()

        body = bytearray()
        # behavior_description field
        body.extend(('--' + boundary + CRLF).encode())
        body.extend(('Content-Disposition: form-data; name="behavior_description"' + CRLF + CRLF).encode())
        body.extend(('Automated test upload' + CRLF).encode())

        # file field
        body.extend(('--' + boundary + CRLF).encode())
        body.extend(('Content-Disposition: form-data; name="image"; filename="' + img_path + '"' + CRLF).encode())
        body.extend(('Content-Type: image/png' + CRLF + CRLF).encode())
        body.extend(img_data)
        body.extend(CRLF.encode())

        # closing boundary
        body.extend(('--' + boundary + '--' + CRLF).encode())

        req = urllib.request.Request(url, data=bytes(body))
        req.add_header('Content-Type', 'multipart/form-data; boundary=' + boundary)
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_text = resp.read().decode('utf-8', errors='replace')
                print('Status:', resp.getcode())
                print('Headers:', resp.getheader('Content-Type'))
                print('Response text:', resp_text[:1000])
        except Exception as e:
            print('Request failed (urllib):', e)

if __name__ == '__main__':
    path = make_image()
    print('Created test image at', path)
    post_image()
