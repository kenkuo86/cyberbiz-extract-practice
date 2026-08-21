from datetime import datetime, timezone, timedelta
from email import utils
import hmac
import hashlib
import base64
import requests
from requests.auth import AuthBase
import itertools
from collections.abc import Iterator
from cyberbiz_extract_practice.models import Order
from cyberbiz_extract_practice.errors import CyberbizError, AuthError, RateLimitError, ServerError, SchemaError, ClientError
import time

username = 'apidemo'
secret = b'apidemo' # 最前面的 b 的效果是把後面的字串轉成 bytes

class CbzAuth(AuthBase):
    def __init__(self, username: str, secret: bytes) -> None:
       # 只放跟 auth 相關，且整個 session 中不會變的東西
       self.username = username
       self.header_params = 'x-date request-line'
       self.secret = secret

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        # x-date
        # 參考範例：'Tue, 10 Oct 2017 00:00:00 GMT'
        x_date = utils.format_datetime(datetime.now(tz=timezone.utc), usegmt=True)

        # request line
        if r.method is None:
            raise Exception('HTTP method required.')
        
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
def fetch_page(url: str, session: requests.Session, page_num: int) -> list:

    # payload
    payload = {'page': page_num, 'per_page': 50}

    for attempt in range(5):
        # 在 session 物件中送出一個 get request
        try: 
            r = session.get(url, params=payload) 

            if r.status_code == 200:
                return r.json() 
            else:
                err_msg = f'錯誤發生在 page {page_num}，status code: {r.status_code}，回傳訊息：{r.text}'

                if r.status_code == 401:
                    raise AuthError('授權錯誤，請檢查權限。'+err_msg)
                elif r.status_code == 429:
                    raise RateLimitError('達到速度上限，稍後重試。'+err_msg)
                elif 400 <= r.status_code < 500:
                    raise ClientError('用戶端錯誤。'+err_msg)
                elif r.status_code >= 500:
                    raise ServerError('伺服器錯誤。'+err_msg)
                else:
                    raise CyberbizError('例外狀況，沒有順利拿到回傳資料。'+err_msg)
        except (RateLimitError, ServerError) as e:
            time.sleep(2 ** attempt)
        
    raise Exception(e.args)


# Step A: 所有資料塞進一個 list 裡
def fetch_all_orders() -> list:
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

        if order_data:
            all_orders.extend(order_data)
            page_num += 1
        else:
            break
    
    return all_orders

# all_orders = fetch_all_orders()

# print(len(all_orders))

# Step B: 用 yield 逐筆撈出資料

def fetch_all_orders_with_yield() -> Iterator[dict]:
    # api url
    url_base = 'https://api.cyberbiz.co'
    url_path = '/v1/orders'
    url = url_base + url_path

    # 用 Session 送 request
    s = requests.Session() # 建立一個 session 空物件
    s.auth = CbzAuth(username=username, secret=secret)

    page_num = 1

    while True:
        data = fetch_page(url, s, page_num)

        if data:
            yield from data
            page_num += 1
        else:
            return

ts = requests.Session() # 建立一個 session 空物件
ts.auth = CbzAuth(username=username, secret=secret)

test_orders = fetch_page('https://api.cyberbiz.co/v1/orders', ts, 1)
# test_orders = fetch_page('https://api.cyberbiz.co/v1/nonsense', ts, 1)

print(test_orders)
print(type(test_orders))


# yield_orders = fetch_all_orders_with_yield()

# order_list = []

# for order in itertools.islice(yield_orders, 3):
#     o = Order.from_api(order)
#     order_list.append(o.subtotal_price)

# print(order_list)

# for i, order in enumerate(yield_orders):
#     if i < 1:
#         o = json.dumps(order, indent=2, ensure_ascii=False)
        # print(i, o)
#     else:
#         break