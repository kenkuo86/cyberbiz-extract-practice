from datetime import datetime, timezone
from email import utils
import hmac
import hashlib
import base64
import requests
from requests.auth import AuthBase

username = 'apidemo'
secret = b'apidemo' # 最前面的 b 的效果是把後面的字串轉成 bytes

class CbzAuth(AuthBase):
    def __init__(self, username, secret):
       # 只放跟 auth 相關，且整個 session 中不會變的東西
       self.username = username
       self.header_params = 'x-date request-line'
       self.secret = secret

    def __call__(self, r):
        # x-date
        # 參考範例：'Tue, 10 Oct 2017 00:00:00 GMT'
        x_date = utils.format_datetime(datetime.now(tz=timezone.utc), usegmt=True)

        # request line
        rline = r.method + ' ' + r.path_url + ' HTTP/1.1'

        # 製作要放入簽章的字串
        sig_str = 'x-date: ' + x_date + '\n' + rline

        dig = hmac.new(self.secret, msg=sig_str.encode(), digestmod=hashlib.sha256).digest()
        sig = base64.b64encode(dig).decode()
        auth = 'hmac username="' + self.username + '", algorithm="hmac-sha256", headers="' + self.header_params + '", signature="' + sig + '"'

        r.headers['X-Date'] = x_date
        r.headers['Authorization'] = auth
        return r


# 函式目標：收到頁碼，回傳該頁的資料
def fetch_page(url, session, page_num):
    # payload
    payload = {'page': page_num, 'per_page': 50}

    # 在 session 物件中送出一個 get request
    r = session.get(url, params=payload) 
  
    return r.json()

def fetch_all_orders():
    # api url
    url_base = 'https://api.cyberbiz.co'
    url_path = '/v1/orders'
    url = url_base + url_path
    
    # 存所有資料的 list
    all_orders = []

    

    # 用 Session 送 request
    s = requests.Session() # 建立一個 session 空物件
    s.auth = CbzAuth(username=username, secret=secret)
    
    page_num = 1

    while True:
        order_data = fetch_page(url, s, page_num)
        # print(len(order_data))

        if order_data:
            all_orders.extend(order_data)
            page_num += 1
        else:
            break
    
    return all_orders

all_orders = fetch_all_orders()

print(len(all_orders))