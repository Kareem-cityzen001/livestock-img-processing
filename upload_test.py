import requests
import time
url='http://127.0.0.1:5000/upload'
img_path='uploads/footrot.jpg'
files={'image': open(img_path,'rb')}
try:
    print('Posting', img_path)
    r=requests.post(url, files=files, timeout=30)
    print('Status code:', r.status_code)
    try:
        print('Response JSON:', r.json())
    except Exception as e:
        print('Response text:', r.text)
except Exception as e:
    print('Error posting:', e)
