from datetime import datetime, timezone, timedelta
from email import utils
import hmac
import hashlib
import base64
import requests
from requests.auth import AuthBase

username = 'apidemo'
secret = b'apidemo' # 最前面的 b 的效果是把後面的字串轉成 bytes

# print('===== Get Example =====')
http_method = 'GET'
url_base = 'https://api.cyberbiz.co'
url_path = '/v1/orders'
headers = 'x-date request-line'

# api url
url = url_base + url_path

# x-date
# 參考範例：'Tue, 10 Oct 2017 00:00:00 GMT'
x_date = utils.format_datetime(datetime.now(tz=timezone.utc), usegmt=True)
# print('===== x-date-datetime =====')
# print(x_date)

# request-line
rline = http_method + ' ' + url_path + ' HTTP/1.1'
# print('===== request-line =====')
# print(rline)
# print('==========')

# payload
payload = 'page=1&per_page=1&offset=0'

# sig_str
sig_str = 'x-date: ' + x_date + '\n' + rline
# print('===== sig_str =====')
# print(sig_str)
# print('==========')

# authorization
dig = hmac.new(secret, msg=sig_str.encode(), digestmod=hashlib.sha256).digest()
sig = base64.b64encode(dig).decode()
auth = 'hmac username="' + username + '", algorithm="hmac-sha256", headers="' + headers + '", signature="' + sig + '"'
# print('===== authorization =====')
# print(auth)
# print('==========')

# Send HTTP GET request
request_headers = {'X-Date': x_date, 'Authorization': auth}
# r = requests.get(url, headers=request_headers, params=payload)
# print('===== Done ' + http_method + ' =====')
# print(r.text)
# print('==========')


# 讓 Session 的 Auth 可以隨著每次 request 更改必要的值
# 引入 AuthBase：可以在送出 request 前修改 request 的內容（看 __call__：輸入 r，回傳 r）
# 要修改哪些內容，就會需要我們在專用的 CbzAuth 裡面指定
# 延續 Session 的精神：可以共用的東西只呼叫一次，需要去回頭看 request 裡面有哪些東西是多次呼叫中一樣 & 不一樣的
# 一樣的就放 __init__，不一樣的就放 __call__

# 單次呼叫的標準內容：requests.get(url, headers=request_headers, params=payload)
# auth = 'hmac username="' + username + '", algorithm="hmac-sha256", headers="' + headers + '", signature="' + sig + '"'
# headers = 'x-date request-line'

class CbzAuth(AuthBase):
    def __init__(self, username, secret, headers):
        # 只放跟 auth 相關，且整個 session 中不會變的東西
       self.username = username
       self.headers = headers
       self.secret = secret

    def __call__(self, r):
        x_date = utils.format_datetime(datetime.now(tz=timezone.utc), usegmt=True)

        # rline = r.method + ' ' + r.path_url + ' HTTP/1.1'
        rline = r.method + ' /v1/orders HTTP/1.1'

        sig_str = 'x-date: ' + x_date + '\n' + rline

        dig = hmac.new(self.secret, msg=sig_str.encode(), digestmod=hashlib.sha256).digest()
        sig = base64.b64encode(dig).decode()
        auth = 'hmac username="' + self.username + '", algorithm="hmac-sha256", headers="' + self.headers + '", signature="' + sig + '"'

        r.headers['X-Date'] = x_date
        r.headers['Authorization'] = auth
        print(r.path_url)
        print(r)
        return r
    
# 用 Session 送 request
s = requests.Session() # 建立一個 session 空物件
s.auth = CbzAuth(username=username, secret=secret, headers=headers)

r1 = s.get(url, params=payload) # 在 session 物件中送出一個 get request
print(r1.status_code)

# r2 = s.get(url, params=payload) 
# print(r2.status_code)