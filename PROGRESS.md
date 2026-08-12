# 進度

## 目前：Module 3 已通過 ✅　下一步 Module 4（資料模型與型別）

Module 3 是 CURRICULUM 標記的三個關鍵節點之一（3 generator / 5 decorator+exception / 7 context manager），已完整通過。

### Module 4 要做的事（CURRICULUM 原文）

- 用 `dataclass` 定義 `Order`，欄位加上型別標註
- 寫一個 `from_api(cls, raw: dict) -> "Order"` 的 classmethod
- 全專案的函式簽章補上型別標註
- 裝 `mypy` 跑一次，把錯誤修掉

**驗收條件**：`mypy src/` 沒有錯誤。以及——刻意在某處把 `order.total` 打成 `order.totl`，確認 mypy 抓得到（`dict["totl"]` 抓不到，這就是重點）。

**學習重點**：`dataclass` 的 `field(default_factory=...)`（為什麼不能直接寫 `= []`）、`Optional[X]` 的意義、`TypedDict` 和 `dataclass` 分別適合什麼場景。

**思考題**：raw API response 該用 `TypedDict` 還是 `dataclass`？兩者的邊界在哪？

已經先踩到的相關線索（詳見 LEARNINGS.md〈Cyberbiz 訂單資料裡已經踩到的型別陷阱〉）：`order_number` 是 int 而 `order_name` 是 str 卻裝同一個數字、`subtotal_price` 是 float。

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
  - 驗收對照 CURRICULUM 第 108-113 行：兩個版本都跑過 ✅／三個 print 都到位（`fetch_page` 內、generator 迴圈內、呼叫端 `for` 內）✅／能回答「`fetch_page` 何時被呼叫」✅／能回答「只取前 10 筆會怎樣」✅（1 次 vs 69 次，有實測數據）／學習重點「同一個 generator 跑兩次」已驗證 ✅
  - 通過後的快問快答也做了：`yield` vs `yield from`、materialize 之後 lazy 還省不省、generator function 的身分何時決定

## 待處理的小事（Module 3 留下的，不影響驗收）

- **函式名 `fetch_all_orders_with_yield` 名不符實**：`all` 承諾「給你全部」，但呼叫端 `break` 之後它並沒有給全部。CURRICULUM 用的名字是 `iter_orders`——`iter` 只承諾「給你一個可以走的東西」。名字挑錯會讓自己讀 code 時被誤導。
- **url 與 session 的建構在兩個函式裡重複**：`fetch_all_orders` 和 `fetch_all_orders_with_yield` 各有一份一模一樣的 url 組裝和 `Session()` + `CbzAuth` 設定。API domain 改一次要改兩個地方。（Module 6 收進 `Config` 時會一起處理。）
- **`fetch_page` 裡的 print 放在 `session.get` 之後**：所以它印出來的時間點其實是「回應已經收到」，看不出「請求送出去了但還沒回來」。（Module 10 做 logging 時這個區分會變重要。）
- **session 的生命週期**：generator 暫停時 session 還開著，呼叫端提前 `break` 時沒有人 `close()` 它。這是 Module 7 context manager 要解決的，Step B 刻意先不處理。

## 卡住的地方

（尚無）

## 未解的疑問

- **為什麼含 query 和不含 query 的 request-line 兩種簽法都能通過？** 目前最合理的解釋是「伺服器不只用一種形式比對」，但這是推論不是實證。詳見 LEARNINGS.md〈Cyberbiz 簽章實際涵蓋的範圍〉。
- **`/v1/orders` 的資料排序方向、以及 `offset` 實際怎麼運作**（Module 3 刻意跳過，因為只用 `page` + `per_page` 不受影響）。實測數據留在 LEARNINGS.md〈分頁參數的實測結果〉，之後要查再回去看。
- **分頁期間如果有新訂單插入怎麼辦？** 排序若是「新的在前」，抓第 1 頁時進來一張新訂單，會把所有資料往後推一格，導致**漏抓或重複抓，而且不會報錯**。這是所有 page/offset 分頁的通病，不是 Cyberbiz 的問題。Module 8 的「重疊區間」就是在解這個。
- **文件寫的「每個請求上限 2 MB（apidemo 為 2 KB）」到底指什麼？** 不可能是 response 大小——實測 `per_page=50` 拿得到完整 50 筆訂單，遠超過 2 KB。
