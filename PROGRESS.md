# 進度

## 目前：Module 3（分頁與 generator）⭐

尚未開始。CURRICULUM 標記的三個關鍵節點之一（3 generator / 5 decorator+exception / 7 context manager），建議放慢。

要做的：Step A 先寫 list 版本，Step B 再寫 generator 版本，兩步都要寫不能跳。

## 已完成
- Module 0：建立 venv、src layout 專案結構、pyproject.toml（`[build-system]` 用 hatchling）、`pip install -e .` 成功、確認同一個 venv 下任何目錄都能 import
- Module 1：52 行的無結構 script，用 HMAC 簽章成功打到 `GET /v1/orders`，印出真實訂單資料。刻意保留的壞味道：secret 寫死、沒有函式、沒有錯誤處理、只抓第一頁
- Module 2：四個項目全部完成 + 驗收通過 + 延伸題完成
  - ✅ 讀文件確認簽章涵蓋欄位與順序
  - ✅ `hmac` + `hashlib` + `base64` 產生簽章
  - ✅ 改用 `datetime` 產生時間戳：`email.utils.format_datetime(datetime.now(tz=timezone.utc), usegmt=True)`，`import time` 已移除
  - ✅ 引進 `requests.Session`
  - ✅ **驗收通過**：時間提前 10 分鐘 → 401，時間正常 → 200（單一變因對照組）
  - ✅ **延伸題完成**：簽章邏輯已改寫成 `requests.auth.AuthBase` 的子類別 `CbzAuth`，掛在 `session.auth` 上

## 卡住的地方
（尚無）

## 未解的疑問
- **為什麼含 query 和不含 query 的 request-line 兩種簽法都能通過？** 目前最合理的解釋是「伺服器不只用一種形式比對」，但這是推論不是實證。詳見下方「簽章實際涵蓋的範圍」。

## 環境操作備忘（venv）

日常啟用（`.venv/` 已存在，Python 3.13）：

```bash
cd /Users/guoqian/Desktop/cyberbiz-extract-practice
source .venv/bin/activate     # zsh / bash 都是這行
which python                  # 驗證：應印出 .../cyberbiz-extract-practice/.venv/bin/python
deactivate                    # 離開
```

重建（venv 壞掉或換機器才需要）：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

VS Code：`Cmd+Shift+P` → `Python: Select Interpreter` → 選 `.venv/bin/python`，之後 integrated terminal 會自動 activate。

**activate 實際上只是在改環境變數**
- shell 靠 `PATH`（一串資料夾路徑）由前往後找執行檔。打 `python` 時，找到的是 `PATH` 裡第一個叫 `python` 的。
- `activate` 只做三件事：把 `.venv/bin` 插到 `PATH` 最前面、設 `VIRTUAL_ENV`、備份舊 `PATH` 給 `deactivate` 用。沒有啟動任何 process，沒有「環境被開啟」這回事。
- 由此推出三件事：(1) 環境變數只活在那一個 shell process 裡，新開 terminal 就要重打；(2) 必須用 `source` 而不是直接執行 script，因為直接執行會開子 shell，改完隨子 shell 消失，改不到手上這個 shell；(3) 直接打 `.venv/bin/python` 與 activate 後打 `python` **完全等價**，activate 只是懶得打全路徑的捷徑。
- 這也解釋了上面「editable install 是綁在特定 venv 上的」：`import` 找不找得到 package，取決於當下跑的是哪個直譯器。

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

**Cyberbiz 簽章實際涵蓋的範圍**（Module 2 實測後修正）
- `sig_str = 'x-date: ' + x_date + '\n' + rline`，所以被簽的只有 **x-date 的值** 和 **request-line（method + path + protocol version）**。
- 原本寫「不包含 query string，所以簽章對 `page` / `per_page` / `offset` 沒有保護力」——**這句是從讀範例 code 推論來的，Module 2 實測後證明不能這樣斷言**，已修正如下。
- **實測結果**（其他變因全部固定，只改簽章裡的 path）：

  | 簽章裡的 request-line | 實際送出的 path | 結果 |
  |---|---|---|
  | `/v1/orders`（不含 query） | `/v1/orders?page=1&...` | 200 |
  | `/v1/orders?page=1&per_page=1&offset=0` | `/v1/orders?page=1&...` | 200 |
  | `/v1/products`（錯的 path） | `/v1/orders?page=1&...` | **401** |

- **可以確定的事**：request-line **確實有被驗證**（第 3 列證明了，簽錯 path 就是不給過）。
- **目前的推論（非實證）**：HMAC 比對是逐位元組全等，差一個字元結果就完全不同、沒有「接近」這回事。所以前兩列都過的唯一合理解釋是**伺服器不只用一種形式去重建 sig_str 比對**（例如兩種都試）。這只是最合理的解釋，還沒有證據。
- **由此做的決定**：程式裡用 `r.path_url`（= path + query），理由是**讓簽的字串和實際送出的 request-line 字面一致**。既然兩種都能過，就選跟真實請求相符的那種；哪天 Cyberbiz 把驗證收嚴成嚴格相符，這個選擇才不會壞掉。
- Authorization header 裡的 `username`、`algorithm`、`headers` 都是明文「說明書」，不是被簽的內容：告訴伺服器該用誰的 secret、什麼演算法、照哪些欄位什麼順序重組 sig_str。伺服器要先讀得懂 username 才知道拿哪把 secret 來驗，所以它不可能被簽在裡面。
- 伺服器的驗證動作是：照說明書，用它收到的 X-Date header 和 request line **自己重建一份一樣的 sig_str**，重算 HMAC，再跟送來的 signature 比對。

**為什麼時間戳必須被簽、且伺服器要獨立檢查新鮮度（防重放攻擊）**
- 重放攻擊：攻擊者不需要知道 secret，只要側錄一個合法請求、原封不動重送，簽章一樣會通過。對 GET 影響有限，對「建立訂單」「扣款」這類請求後果嚴重。
- 解法要兩層：(1) x-date 被簽進 sig_str，攻擊者不能改時間（改了簽章對不上）；(2) 伺服器獨立拒絕太舊的時間戳，讓側錄下來的請求過幾分鐘就失效。缺一不可。
- 常見誤解：以為「時間不對 → hash 算出來不一樣 → 驗證失敗」。**這是錯的**——因為 x_date 同時用在 sig_str 和 X-Date header，兩邊一致，伺服器重算後簽章會吻合。真正擋下來的是伺服器的時間新鮮度檢查。這也是為什麼 Module 2 的「調快 10 分鐘」驗收方式才有意義。
- 同理，`time.gmtime()` 換成 `time.localtime()` 會失敗，不是因為簽章對不上，而是因為送出了一個標示為 GMT、實際快 8 小時（台灣 = GMT+8）的時間，超出伺服器容許窗口。

---

以下為 Module 2 學到的觀念。

**HTTP 是文字，但送出去之前要先接通一條線路**
- request / response 本質上就是一段有格式的文字（request-line、headers、body）。但在能送出這段文字之前，電腦必須先跟伺服器**接通一條連線**。這是原本完全沒概念的那一層。
- 完整流程分四段，用打電話類比：
  1. **撥號、對方接起、確認雙方聽得到** = TCP 三向交握。來回三個訊息，內容完全不含要傳的資料，純粹在確認「線通了，而且雙方都知道通了」。
  2. **約定暗號，避免旁人聽懂** = TLS 交握，只有 `https` 才有。雙方交換資訊、算出一組只有彼此知道的金鑰。比第 1 段更貴，因為多了幾個來回再加上運算。
  3. **開始講話** = HTTP request / response，也就是原本唯一有概念的那一段。
  4. **掛電話** = 關閉連線。
- 成本重點：第 1 + 2 段加起來，對一台在國外的伺服器可能吃掉一兩百毫秒，而這整段時間裡，一個 byte 的 HTTP 都還沒送出去。

**HTTP/1.1 預設不掛線（keep-alive）**
- 第 3 段結束（拿到 response）之後，連線**不一定要關掉**。HTTP/1.1 預設讓它繼續開著，於是通往同一台主機的下一個請求可以直接跳到第 3 段，省掉撥號和約暗號。
- 這就是「連線值得重用」的全部理由。Module 3 要翻完所有分頁，假設 200 頁，不重用連線就是撥號 200 次，其中 199 次是純浪費——對象根本是同一台主機。

**`requests.Session` 是 class，不是 method**
- 命名慣例（PEP 8）：`CapWords` 大寫開頭是類別，`lower_case` 是函式 / 方法。所以 `requests.get` 是模組層級的**函式**，`requests.Session` 是**類別**，要先實例化成 `requests.Session()` 才能用。
- 這個區別不是咬文嚼字，它是 Session 有用的根本原因：**類別的實例可以持有狀態**。函式呼叫完就消失，物件會繼續活著。

**`requests.Session` 是純 client 端的物件，伺服器完全不知情**
- 最重要的一句：**伺服器不知道我有一個 Session**。沒有 session ID，伺服器端沒有任何對應的東西存在。全程是單方面的、client 端的事。
- 它就是一個自己這邊拿著的盒子，裡面放兩類東西：(1) **還開著的連線**（連線池）(2) 記住的**設定**（headers、auth、cookies）。
- 所以「誰在負責記錄 / 打包出一個 session」的答案是：**我自己的 Python 程式，也就是 `requests` 這個函式庫**。
- 盒子裡最值得重複使用的是**連線**，headers 只是順便。原本的理解「把可共用的東西暫時記起來」方向是對的，缺的是「最主要被記起來的其實是連線」。

**Session 的開頭與結尾**
- **開頭**：`requests.Session()` 這一行**沒有發生任何網路動作**，只是建了一個空盒子。連線是等到第一次真的送請求時才建立，然後被留在盒子裡。
- **結尾**：`session.close()` 把盒子裡還開著的連線全部關掉。`with requests.Session() as s:` 的意思是「離開這個區塊時自動幫我 close」（`with` 本身的機制是 Module 7 的主題，現在當成「自動收尾」理解就夠）。
- `requests.get()` 的內部實作（`requests/api.py`）本體只有兩行：`with sessions.Session() as session: return session.request(...)`。也就是**建盒子 → 用一次 → 關掉連線**。
- 推論：**一直都在用 Session，只是每次都用完就丟。** `requests.get()` 不是「Session 的簡化替代品」，它是「一次性 Session 的包裝紙」。所以「引進 Session」實際上是**停止每次把它丟掉**。

**兩個同名不同物的「session」**
- **網站登入的 session**：這個**是**伺服器端的狀態。伺服器發一個 cookie 給你，記住「這是誰」。有明確的開始（登入）和結束（登出 / 過期）。
- **`requests.Session`**：純 client 端，跟上面無關。
- 兩者唯一的關聯：因為 `requests.Session` 會保存 cookies，所以它**有能力參與**前者，但它本身不是前者。
- Cyberbiz API 用簽章認證、不用 cookie，所以這個專案完全不會碰到前者。「session」這個字的撞名是當初混淆的來源。

**`session.headers` 不是「不用重送」，是「幫你每次自動補上」**
- 曾經誤以為：放進 `session.headers` 的東西代表之後的請求不必再送。**錯的**——HTTP 沒有「這個 header 上次送過了、這次省略」的機制，每個請求都會把所有 header 完整送出去。
- 它真正的意思是：**requests 在每次送出前自動幫你補上去**，純粹 client 端省打字。wire 上的 bytes 跟每次手動傳 `headers=` 完全一樣。
- 這件事其實可以從「伺服器不知道我有一個 Session」直接推出來：伺服器既然不知道 Session 存在，就不可能知道「上次那個 header 這次還算數」。

**哪些 header 適合放 `session.headers`**
- 判準不是「會不會變」，而是**這個 header 的值綁在什麼東西上**：
  - 綁在「我是誰、我是什麼 client」→ 屬於整個 session（`User-Agent`、`Accept` 這類），適合放。
  - 綁在「這一次請求本身」→ 不屬於 session，不能放。
- `X-Date` 和 `Authorization` 都屬於後者，**兩個都不能放**：`X-Date` 的正確值取決於送出當下幾點，`Authorization` 的簽章又涵蓋 x-date 和 request-line。
- 而且這個 bug 特別惡劣：如果兩個都凍住，簽章與 header 仍然互相一致，簽章比對**會過**，擋下你的是新鮮度檢查——所以**一開始好好的，跑久了才突然全掛**。Module 3 要翻幾十上百頁，正好是會踩到的場景。「一定會失敗」比「跑到一半才開始失敗」好查太多。
- 另外，如果同一個 session 打不同 endpoint，凍住的 `Authorization` 還會有第二種失敗：request-line 變了但簽章沒變（已由上面第 3 列實測證實會 401）。

**`AuthBase` 不是「用來產出 auth 字串」的東西**
- 看它的形狀就知道：`__call__(self, r)` **收到整個請求物件、回傳整個請求物件**。如果它的職責只是產字串，簽章會長成 `def get_auth(self) -> str`。
- 它真正的身分是：**一個在請求送出前拿到整個請求、可以任意修改它的 hook**。文件的原句是 "will be called before the request is dispatched and can **modify the request**"。
- 名字叫 auth 只是因為最常見的用途是認證。而認證資訊要進到 HTTP 請求裡**只能透過 header**，所以「設定 header」不是範例的額外行為，那就是它唯一的工作方式（內建的 `HTTPBasicAuth` 也是這樣做）。
- 由此推出：`X-Date` 也該由 `CbzAuth` 負責。更硬的理由是——**X-Date header 的值和 sig_str 裡的時間戳必須完全相同**，它們不是兩件獨立的事，是同一次計算的兩個產物。分散在兩個地方產生，就有機會漂開。
- 犯過的錯：在 `__call__` 裡寫 `self.headers[...] = ...`。改 `self` 對即將送出的請求沒有任何影響，**要改的是參數 `r` 身上的 headers**。

**`__init__` 和 `__call__` 的執行時機（這一輪最大的收穫）**
- `__init__` 在 **`CbzAuth(...)` 那個括號被執行的當下**跑，一次。跟送不送請求、送幾次完全無關。
- `__call__` 在**每次請求送出前**跑，送幾次就跑幾次。
- 實測（在兩者各放一個 `print`，用同一個 session 送兩次請求）：`__init__` 印 1 次，`__call__` 印 2 次。而且 `PreparedRequest` 先印、`200` 後印，證實 `__call__` 確實在請求送出**之前**執行。
- 曾經誤以為「`__init__` 是被第一個 `s.get()` 觸發的，之後被記住所以沒再跑」。結果同樣是「一次」，但原因完全不同。驗證方法：**把所有 `s.get()` 註解掉再跑一次，`__init__` 的 print 照樣會出現。**
- 為什麼這個時機非搞清楚不可：`__init__` 執行的那一刻，它對「接下來會有什麼請求」**一無所知**——不知道要打哪個 path、送幾次、什麼時間送。所以任何取決於「這次請求」的東西（時間戳、method、path）在 `__init__` 裡根本**算不出來**，不是「算了會過期」而是當下沒有資訊可算。這就是 `x_date` 不能放 `__init__` 的真正理由。
- 通則：`CbzAuth(...)` 和 `requests.Session()` 是同一回事，**括號一打物件就建好，沒有任何網路動作發生**。這不是 Session 的特性，是所有 class 的通則。

**class 的職責切法**
- `__init__` 放**建立物件時就能決定、之後不變**的（`username`、`secret`）；`__call__` 放**必須等到送出那一刻才能決定**的（`x_date`、`rline`）。
- 要不要放進這個 class，判準**不是「共不共用」**。`url_base` 也是共用的，但它跟「怎麼認證」無關，塞進去這個 class 就開始管不屬於它的事了。判準是「**這個 class 完成它的職責需不需要它**」。
- 需要的東西還要再分來源：外面傳進來（會換的，如帳號密碼）／從 `r` 身上拿（每次可能不同的，如 method、path）／寫死（永遠不變的常數）。

**繼承框架的類別 = 不能決定自己怎麼被呼叫**
- 犯過的錯：把 `__call__` 宣告成 `def __call__(self, r, http_method, url_path)`。**這個 method 不是自己呼叫的，是 requests 呼叫的**，而 requests 只會傳一個 `r`，多宣告的參數永遠不會有值 → `TypeError`。
- 需要的資訊要從 `r` 身上拿，不能（也不該）從外面傳。這就是「繼承框架的類別」的感覺：**形狀是框架訂的，你只能照它給的形狀去接。**

**`__call__` 讓實例可以被當成函式呼叫**
- 一個 class 定義了 `__call__` 之後，它的**實例**可以用 `instance(...)` 的寫法呼叫，這會觸發 `__call__`。
- 這解釋了之前查文件卡住的地方：文件說 auth 接受 "any callable"，而 `CbzAuth` 的實例因為有 `__call__`，**它就是一個 callable**。
- 也解釋了 `session.auth` 和 `session.headers` 的本質差異：

  | | 放進去的是 |
  |---|---|
  | `session.headers` | 一個**值**，requests 每次原封不動抄上去 |
  | `session.auth` | 一個**會被呼叫的東西**，requests 每次呼叫它、拿它當下算出來的結果 |

- 一個是名詞、一個是動詞。這就是「會過期的東西放 headers 會爆、放 auth 不會」的根本原因。
- 要分清三種東西：`CbzAuth` 是類別（設計圖）、`CbzAuth(...)` 是實例（要交出去的）、呼叫它是 requests 內部做的事——**自己永遠不會去呼叫 `__call__`**。

**文件沒寫的時候怎麼辦（`path_url` 為例）**
- requests 官方 API 文件對 `PreparedRequest.path_url` 只有一句 "Build the path URL to use."，完全沒說它含不含 query string。
- 兩條路：(1) **看原始碼**（`requests/models.py`，它是個 property，實作就是把 url 拆開取 path，有 query 就接在後面）；(2) **直接印出來看**——更快，而且是自己的一手證據。
- 教訓：**「文件沒寫」不是死路。** 原始碼隨時可以看、值隨時可以印。這一輪就是因為忘了印出來，才對 `path_url` 到底是什麼猜了半天。
- 順帶：`PreparedRequest` 上跟網址有關的只有 `r.url`（完整網址）和 `r.path_url`（path + query），**沒有「只有 path」的現成屬性**。真的需要的話得自己用標準庫 `urllib.parse` 的 `urlsplit` 切。

**實驗方法：對照組與單一變因（這一輪反覆用到）**
- 「跑出 401」或「跑出 200」**單獨看都不構成證據**。因為同一個 401 可能來自時間戳太舊、簽章對不上、或帳號錯——狀態碼不會告訴你是哪一個。
- 要能歸因，必須：(1) **只改一個變因**；(2) **同時有成功組和失敗組**。時間戳驗收之所以成立，是因為「時間正常 → 200」和「提前 10 分鐘 → 401」其他完全一樣。
- 第一次做的時候只印了 `status_code` 沒印 `r.text`，等於丟掉伺服器給的最直接線索（實際訊息是 `HMAC signature cannot be verified, a valid date or x-date header is required for HMAC Authentication`）。
- **「拿到 200」不等於「我的理解是對的」**。query string 那題就是活生生的例子：兩種完全不同的簽法都拿到 200，代表當時的實驗設計根本分不出真假。要製造一個**明確該失敗**的情況（故意簽錯 path），才問得出答案。
- 犯過的推論錯誤：從 401 的錯誤訊息推論「新鮮度檢查是在驗算 HMAC **之後**才做的」。**這個從外部證不出來**——「先檢查時間再算 HMAC」和「先算 HMAC 再檢查時間」會回傳一模一樣的東西。真正證明了的是「簽章比對這關不可能因為對不上而失敗，所以擋下我的只能是獨立的時間新鮮度檢查」，拿掉多講的那句，論證反而更強。
- 通則：**寫筆記時把「實測結果」和「推論」分開寫。** 之後遇到打臉的證據，才會清楚該推翻的是哪一句。