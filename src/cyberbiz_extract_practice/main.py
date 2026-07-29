import time
import hmac
import hashlib
import base64
import requests

username = 'apidemo'
secret = b'apidemo' # 最前面的 b 的效果是把後面的字串轉成 bytes

print('===== Get Example =====')
http_method = 'GET'
url_base = 'https://api.cyberbiz.co'
url_path = '/v1/orders'
headers = 'x-date request-line'

# api url
url = url_base + url_path

# x-date
x_date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
print('===== x-date =====')
print(x_date)
print('==========')

# request-line
rline = http_method + ' ' + url_path + ' HTTP/1.1'
print('===== request-line =====')
print(rline)
print('==========')

# payload
payload = 'page=1&per_page=1&offset=0'

# sig_str
sig_str = 'x-date: ' + x_date + '\n' + rline
print('===== sig_str =====')
print(sig_str)
print('==========')

# authorization
dig = hmac.new(secret, msg=sig_str.encode(), digestmod=hashlib.sha256).digest()
sig = base64.b64encode(dig).decode()
auth = 'hmac username="' + username + '", algorithm="hmac-sha256", headers="' + headers + '", signature="' + sig + '"'
print('===== authorization =====')
print(auth)
print('==========')

request_headers = {'X-Date': x_date, 'Authorization': auth}
r = requests.get(url, headers=request_headers, params=payload)
print('===== Done ' + http_method + ' =====')
print(r.text)
print('==========')