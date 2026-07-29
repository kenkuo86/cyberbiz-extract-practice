# 進度

## 目前：Module 2（HTTP Signature 手刻）

進 Module 2 要注意的事：
- 課綱指定用 `datetime` 產生時間戳，目前 Module 1 版本用的是 `time.strftime` + `time.gmtime`，要換掉
- 要引進 `requests.Session`，並理解為什麼比每次 `requests.get()` 好
- 驗收：把系統時間往前調 10 分鐘，請求要被拒絕，而且要能解釋為什麼
- 延伸題：把簽章邏輯寫成 `requests.auth.AuthBase` 的子類別

## 已完成
- Module 0：建立 venv、src layout 專案結構、pyproject.toml（`[build-system]` 用 hatchling）、`pip install -e .` 成功、確認同一個 venv 下任何目錄都能 import
- Module 1：52 行的無結構 script，用 HMAC 簽章成功打到 `GET /v1/orders`，印出真實訂單資料。刻意保留的壞味道：secret 寫死、沒有函式、沒有錯誤處理、只抓第一頁

## 卡住的地方
（尚無，Module 0 / 1 遇到的卡點都已解決，整理進下方觀念）

## 已經懂了的觀念

**distribution name vs import name 是兩個不同的東西**
- `pyproject.toml` 裡 `[project].name` 是 distribution name（PyPI 上、`pip install XXX` 時打的字串），PyPI 對這個名字的 `-`/`_`/`.` 視為等價（PEP 503 normalization），所以可以用 hyphen。
- import name 是由**實際資料夾名稱**決定的（裡面有 `__init__.py` 那個），必須是合法的 Python identifier，不能有 hyphen。
- 兩者只是「慣例上」常取成對應的樣子，不是同一個設定值。

**hatchling 怎麼決定要打包哪個資料夾**
- hatchling 預設用「distribution name 正規化成 underscore」去猜對應的資料夾名稱（例如 `cyberbiz-extract-practice` → 猜 `cyberbiz_extract_practice`），猜不到時整個 `pip install -e .` 會在 metadata 準備階段失敗。
- 解法有兩條：(1) 把資料夾改名去對應猜測結果，或 (2) 在 `pyproject.toml` 用 `[tool.hatch.build.targets.wheel]` 的 `packages = [...]` 明確指定路徑。但無論哪條路，那個路徑指到的資料夾名稱本身仍然要是合法 identifier，不然還是無法用 `import` 語法正常引入。

**`pip install -e .` 實際在做什麼**
- `.` 是路徑引數，告訴 pip「這裡是專案根目錄」，pip 會去讀這裡的 `pyproject.toml`。
- pip 讀 `[build-system]` 決定用哪個 build backend，透過 PEP 517 / PEP 660 定義的標準化 hook 呼叫該 backend；backend 的工作是判斷「哪些檔案算套件內容」。
- `-e`（editable）代表安裝一個指回原始碼位置的指標，而不是把檔案複製進 `site-packages`，所以改 code 不用重新 install。

**editable install 是綁在特定 venv 上的**
- 上述指標只存在於當下啟用的那個 venv 的 `site-packages` 裡。開一個沒有啟用同一個 venv 的新 terminal，`import` 會失敗，因為那個 terminal 用的是別的 Python 直譯器。可用 `which python` 或 `python -c "import sys; print(sys.executable)"` 確認目前指到哪個直譯器。

**src layout 的用意**
- 把 code 放在 `src/` 底下，是為了避免「工作目錄剛好被加進 `sys.path`」造成的假成功（沒裝 package 也能 import，只是巧合），逼你一定要透過正式的安裝管道才能 import 到，這樣本機測試結果才會跟別人真的 `pip install` 之後一致。

---

以下為 Module 1 學到的觀念。

**dependencies 只列第三方套件**
- `pyproject.toml` 的 `[project].dependencies` 只寫需要透過 pip 從 PyPI 下載的第三方套件（例如 `requests`）。
- `base64`、`hmac`、`hashlib`、`time`、`datetime`、`json` 這些是標準庫，裝好 Python 就有，寫進 dependencies 會讓 pip 去 PyPI 找不到而報 `No matching distribution found`。標準庫清單見 https://docs.python.org/3/library/

**`requests` 基本用法**
- `requests.get(url, headers={...}, params=...)` 回傳一個 response 物件，常用屬性：`.status_code`、`.text`、`.json()`、`.headers`。
- `requests` 只做 HTTP 層，**不會執行 JavaScript**。所以拿公開網頁時，抓到的是原始 HTML，跟瀏覽器「執行完 JS 之後看到的畫面」可能差很多。需要後者要用 Selenium / Playwright 這類會跑瀏覽器引擎的工具。
- 打 API 通常沒這個問題，因為 API 直接回 JSON（設計給程式讀），網頁 HTML 是設計給瀏覽器 + 人眼讀的。

**`str` vs `bytes`，以及兩種不同的 encode**
- `str` 是「人看得懂的文字」，`bytes` 是「實際儲存/傳輸的位元組」。雜湊函式只吃 bytes，傳 str 進去會報 `Strings must be encoded before hashing`。
- `str.encode()`：文字 → bytes，依字元編碼規則（預設 UTF-8）。`b'apidemo'` 這種 `b` 前綴是同一件事的字面值寫法，所以 `secret = 'apidemo'` 搭配 `secret.encode()` 效果等同 `secret = b'apidemo'`。
- `base64.b64encode()`：bytes → bytes，但把內容限制在安全可印出的 ASCII 範圍，目的是讓任意二進位資料能塞進只吃文字的管道（如 HTTP header）。輸出仍是 bytes，所以還要再 `.decode()` 轉回 str 才能拼字串。
- 兩者名字都有 encode 但完全不同：一個處理「文字怎麼變位元組」，一個處理「位元組怎麼變安全文字」。

**`hmac.new(key, msg, digestmod)` 三個參數角色不對等**
- `msg`：**被保護的內容**。它會原封不動送出去，簽章證明它傳輸中沒被改過。
- `key`（secret）：確實會參與運算，但角色是「只有雙方知道的秘密」，永遠不送出去。第三方即使看到 msg 和 signature，也算不出下一個請求的簽章。
- `digestmod`：只是選演算法，不是資料。
- `.digest()` 回傳原始 bytes（要接 base64 就用這個）；`.hexdigest()` 回傳同樣內容的 16 進位文字表示。
- 判斷「哪些東西受簽章保護」的方法：**看 `msg` 是什麼**，保護範圍就是 msg 的範圍。

**Cyberbiz 簽章實際涵蓋的範圍**
- `sig_str = 'x-date: ' + x_date + '\n' + rline`，所以被簽的只有 **x-date 的值** 和 **request-line（method + path + protocol version）**。
- **不包含 query string**（`page`、`per_page`、`offset` 都沒被簽），代表簽章對這些參數完全沒有保護力，中途被竄改伺服器也驗不出來。實務上主要靠 HTTPS/TLS 擋這種竄改，但那是另一層防護，不該跟簽章混為一談。
- Authorization header 裡的 `username`、`algorithm`、`headers` 都是明文「說明書」，不是被簽的內容：告訴伺服器該用誰的 secret、什麼演算法、照哪些欄位什麼順序重組 sig_str。伺服器要先讀得懂 username 才知道拿哪把 secret 來驗，所以它不可能被簽在裡面。
- 伺服器的驗證動作是：照說明書，用它收到的 X-Date header 和 request line **自己重建一份一樣的 sig_str**，重算 HMAC，再跟送來的 signature 比對。

**為什麼時間戳必須被簽、且伺服器要獨立檢查新鮮度（防重放攻擊）**
- 重放攻擊：攻擊者不需要知道 secret，只要側錄一個合法請求、原封不動重送，簽章一樣會通過。對 GET 影響有限，對「建立訂單」「扣款」這類請求後果嚴重。
- 解法要兩層：(1) x-date 被簽進 sig_str，攻擊者不能改時間（改了簽章對不上）；(2) 伺服器獨立拒絕太舊的時間戳，讓側錄下來的請求過幾分鐘就失效。缺一不可。
- 常見誤解：以為「時間不對 → hash 算出來不一樣 → 驗證失敗」。**這是錯的**——因為 x_date 同時用在 sig_str 和 X-Date header，兩邊一致，伺服器重算後簽章會吻合。真正擋下來的是伺服器的時間新鮮度檢查。這也是為什麼 Module 2 的「調快 10 分鐘」驗收方式才有意義。
- 同理，`time.gmtime()` 換成 `time.localtime()` 會失敗，不是因為簽章對不上，而是因為送出了一個標示為 GMT、實際快 8 小時（台灣 = GMT+8）的時間，超出伺服器容許窗口。