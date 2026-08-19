# 進度

## 目前：Module 5 進行中 🚧（錯誤處理與重試）⭐

Module 5 是 CURRICULUM 標記的三個關鍵節點之一（3 generator / **5 decorator+exception** / 7 context manager）。

### 這個 Module 的三層地圖（用來定位現在做到哪）

程式碼目前的路徑是 `session.get(...)` → `r.json()` → `return`，**中間沒有任何一行在問「這次成功了嗎」**。要插進去三層：

| 層 | 做什麼 | 狀態 |
|---|---|---|
| 1. **偵測** | 看 status code，判斷「這是哪一種失敗」 | ⬜ 還沒開始 |
| 2. **分類** | 把它變成一個有名字的例外丟出來（exception 階層） | 🚧 進行中 |
| 3. **反應** | 接住例外，決定重試還是放棄（手刻 retry → tenacity） | ⬜ 還沒開始 |

順序不能調換：沒有第 1 層就沒東西可分類；沒有第 2 層，第 3 層分不出「該重試的」和「重試也沒用的」。

### 已完成的步驟

- **痛點實測完成**：把 `per_page` 改成 500 觸發伺服器 500，單獨呼叫一次 `fetch_page`，確認錯誤會一路無聲流到五層之外才炸。完整推導與結論記在 LEARNINGS.md〈目前這支程式對失敗完全沒有防護〉。
- **`errors.py` 已建立**，五個類別的骨架寫好了，但**根部接錯**（見下方「停在哪裡」）。

### 停在哪裡（下一輪從這裡接）

`src/cyberbiz_extract_practice/errors.py` 有兩個待處理的點，兩個都要在 REPL 實測後才往下走：

1. **`class Error: pass` 這個自己造的根要拿掉。** 直覺是對的（「應該要有一個更廣泛的父類別標記所有錯誤」），但 Python 已經有那棵樹了，而且自己造的這棵**會直接壞掉**——只有繼承自 `BaseException` 的類別才能被 `raise`。
   - **待做**：REPL 跑 `class Error: pass` 然後 `raise Error()`，看錯誤訊息，據此決定 `CyberbizError` 的括號裡填什麼。
   - **待講**：`BaseException` 和 `Exception` 的差別（下一輪要補的觀念）。
2. **第 7 行的裸標註 `error: str`**。這個 class 沒有 `@dataclass`，沒有人會去讀 `__annotations__` 幫忙生欄位。
   - **待做**：REPL 跑 `CyberbizError().error` 看會發生什麼，並釐清當初寫這行時期待的是什麼。

### 這一輪修正掉的錯誤推論（避免再犯）

- 曾經以為「例外往外傳的過程中會**經過** `CyberbizError`」。**錯的**，混淆了呼叫堆疊和類別階層兩個不同的「往上」。詳見 LEARNINGS.md〈例外的兩個「往上」是完全不同的東西〉。
- 曾經以為「照現在第 111-119 行那段跑會形成無窮迴圈」。**錯的**，`islice(yield_orders, 3)` 拿滿 3 筆就不再要，generator 直接凍在原地。無窮迴圈的條件是**呼叫端要到底**，不是這段程式的必然結果——決定權在 Module 3 就交給呼叫端了。

### Module 5 剩下要做的事（CURRICULUM 原文）

定義 exception 階層：

```
CyberbizError
  ├─ AuthError        (401 → 不重試)
  ├─ RateLimitError   (429 → 重試，看 Retry-After)
  ├─ ServerError      (5xx → 重試)
  └─ SchemaError      (資料壞掉 → 不重試)
```

然後：

- 先**手刻**一次 retry：`for attempt in range(n)` + `time.sleep(2 ** attempt)`
- 再換成 `tenacity`，比較兩者
- 讀 `tenacity` 的 `retry` decorator 原始碼，看它怎麼包裝你的函式

**驗收條件**：用一個假的 local server（`http.server` 就夠）模擬 429 和 401，確認前者會重試、後者立刻拋出。

**學習重點**：exception 繼承、`raise ... from e` 保留原始 traceback、`finally` 的執行時機、decorator 怎麼改變一個函式的行為。

### 已經先踩到的相關線索

- **`raise Exception(...)` 太籠統要換掉**：`CbzAuth.__call__` 裡處理 `r.method is None` 時用的是裸 `Exception`。它是例外階層的最頂端，接的人分不出是什麼問題。詳見 LEARNINGS.md〈「什麼都是」等於「沒說什麼」〉。
- **`per_page` 超過上限時 API 回 500**，但那是「參數給錯」造成的，**重試幾次都不會成功**。CURRICULUM 的階層把 5xx 歸在「重試」類，這不是階層設計錯，是伺服器用錯狀態碼。詳見 LEARNINGS.md〈分頁參數的實測結果〉。
- **`session` 已經是 `fetch_page` 的參數**，所以要傳假的 session 進去測錯誤處理是可行的（Module 3 刻意留的伏筆）。

## 已完成

- **Module 0**：建立 venv、src layout 專案結構、pyproject.toml（`[build-system]` 用 hatchling）、`pip install -e .` 成功、確認同一個 venv 下任何目錄都能 import
- **Module 1**：52 行的無結構 script，用 HMAC 簽章成功打到 `GET /v1/orders`，印出真實訂單資料。刻意保留的壞味道：secret 寫死、沒有函式、沒有錯誤處理、只抓第一頁
- **Module 2**：四個項目全部完成 + 驗收通過 + 延伸題完成
  - 讀文件確認簽章涵蓋欄位與順序
  - `hmac` + `hashlib` + `base64` 產生簽章
  - 改用 `datetime` 產生時間戳：`email.utils.format_datetime(datetime.now(tz=timezone.utc), usegmt=True)`
  - 引進 `requests.Session`
  - **驗收通過**：時間提前 10 分鐘 → 401，時間正常 → 200（單一變因對照組）
  - **延伸題完成**：簽章邏輯改寫成 `requests.auth.AuthBase` 的子類別 `CbzAuth`，掛在 `session.auth` 上
- **Module 3**：Step A + Step B 都完成，**驗收逐條通過**
  - Step A：`fetch_page(url, session, page_num)` 抓單頁、`fetch_all_orders()` 用 `while True` 翻完所有頁並回傳完整 list，實跑 3366 筆
  - Step B：改寫成 generator，`yield from` 逐筆交出
  - 驗收對照 CURRICULUM 第 108-113 行：兩個版本都跑過 ✅／三個 print 都到位 ✅／能回答「`fetch_page` 何時被呼叫」✅／能回答「只取前 10 筆會怎樣」✅（1 次 vs 69 次，有實測數據）／「同一個 generator 跑兩次」已驗證 ✅
- **Module 4**：四個項目全部完成，**驗收逐條通過**
  - `Order` dataclass（`models.py`），9 個欄位、型別標註齊全
  - `from_api(cls, raw: dict) -> "Order"` classmethod，簽章與 CURRICULUM 一致
  - 六個函式簽章全部補上標註：`CbzAuth.__init__`／`__call__`／`fetch_page`／`fetch_all_orders`／`fetch_all_orders_with_yield`／`Order.from_api`
  - 裝 `mypy` + `types-requests`，**修掉的是真 bug**（`r.method` 可能是 `None`，改用 `raise` 中止），不是為了讓工具閉嘴
  - **驗收通過**：`mypy src/` 乾淨 ✅／`o.subtotal_pirce` 被抓到並提示正確拼法 ✅／對照組 `order['subtotal_pirce']` 完全沒被抓到 ✅
  - 快問快答四題全通：classmethod 的三個理由、mypy 靜態檢查的原理、Optional 的一致性、邊界該畫在哪
  - 途中做的欄位盤點：`scan.py` 掃 50 筆樣本，統計每個 key 出現過哪些型別

## 待處理的小事

**Module 4 留下的（不影響驗收）**

- **`field(default_factory=...)` 沒踩到**：CURRICULUM 列為學習重點的經典坑，因為 `Order` 的 9 個欄位全是純量而沒遇到。**等把 `line_items` 這類 list 欄位收進來時會出現。**
- **`Order` 只收 9 欄，raw 有 53 欄**：B 組 11 個巢狀 dict（`customer`、`prices`、`statuses`…）、C 組 7 個 list（`line_items`、`fulfillments`…）全部沒處理。第二版要做時，`customer` 是三層巢狀（`customer.address.detail_address`），要先決定攤平還是開子 dataclass。
- **15 個欄位在 50 筆樣本裡全是 `None`**（`logistics_id`、`card4no`、`referral_code`、`pos_info` 相關等），型別無從得知。判定為「demo 商店沒開的功能」，不再追。
- **`TypedDict` 只討論了觀念，沒實際寫**。要動手的時機是「需要 raw dict 完整通過、但又想要 mypy 罩得住」的時候。

**更早留下的**

- **函式名 `fetch_all_orders_with_yield` 名不符實**：`all` 承諾「給你全部」，但呼叫端 `break` 之後它並沒有給全部。CURRICULUM 用的名字是 `iter_orders`——`iter` 只承諾「給你一個可以走的東西」。
- **url 與 session 的建構在兩個函式裡重複**：`fetch_all_orders` 和 `fetch_all_orders_with_yield` 各有一份一模一樣的 url 組裝和 `Session()` + `CbzAuth` 設定。（Module 6 收進 `Config` 時會一起處理。）
- **`fetch_page` 裡原本的 print 已移除**，但 Module 10 做 logging 時要注意：log 要能區分「請求送出去了」和「回應已經收到」。
- **session 的生命週期**：generator 暫停時 session 還開著，呼叫端提前 `break` 時沒有人 `close()` 它。這是 Module 7 context manager 要解決的。

## 檔案現況

| 檔案 | 用途 | 備註 |
|---|---|---|
| `src/cyberbiz_extract_practice/main.py` | 認證 + 抓分頁 | ⚠️ **目前是實驗狀態**，見下表 |
| `src/cyberbiz_extract_practice/errors.py` | 例外階層 | Module 5 新增，**尚未完成**（根部接錯） |
| `src/cyberbiz_extract_practice/models.py` | `Order` dataclass + `from_api` | Module 4 新增 |
| `scan.py` | 欄位盤點工具（掃樣本統計型別） | 在專案根目錄，不在 `src/` 底下，所以 `mypy src/` 不會檢查它 |
| `sample_page.json` | 50 筆真實訂單樣本 | **含 PII，已 gitignore** |

**`main.py` 目前被改成實驗狀態，做完 Module 5 的偵測層之後要記得處理：**

| 位置 | 現在是什麼 | 原本是什麼 |
|---|---|---|
| `fetch_page` 裡的 `per_page` | `500`（故意觸發伺服器 500） | `50` |
| 底部執行區塊 | 單獨呼叫一次 `fetch_page` 並印出回傳值與 `type()` | generator + `islice(3)` + `Order.from_api` |

（`islice` 那段已註解保留在檔案裡，沒有刪掉。）

## 卡住的地方

（尚無）

## 未解的疑問

- **為什麼含 query 和不含 query 的 request-line 兩種簽法都能通過？** 目前最合理的解釋是「伺服器不只用一種形式比對」，但這是推論不是實證。詳見 LEARNINGS.md〈Cyberbiz 簽章實際涵蓋的範圍〉。
- **`/v1/orders` 的資料排序方向、以及 `offset` 實際怎麼運作**（Module 3 刻意跳過，因為只用 `page` + `per_page` 不受影響）。實測數據留在 LEARNINGS.md〈分頁參數的實測結果〉。
- **分頁期間如果有新訂單插入怎麼辦？** 排序若是「新的在前」，抓第 1 頁時進來一張新訂單，會把所有資料往後推一格，導致**漏抓或重複抓，而且不會報錯**。這是所有 page/offset 分頁的通病。Module 8 的「重疊區間」就是在解這個。
- **文件寫的「每個請求上限 2 MB（apidemo 為 2 KB）」到底指什麼？** 不可能是 response 大小——實測 `per_page=50` 拿得到完整 50 筆訂單，遠超過 2 KB。
- **`subtotal_price` 是 `float`**，金額用浮點數是經典地雷（精度問題）。目前照收，沒決定要不要換成 `Decimal`。
