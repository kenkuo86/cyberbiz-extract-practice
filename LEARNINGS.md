# 學習筆記

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
- 這也解釋了下面「editable install 是綁在特定 venv 上的」：`import` 找不找得到 package，取決於當下跑的是哪個直譯器。

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
- 另外，如果同一個 session 打不同 endpoint，凍住的 `Authorization` 還會有第二種失敗：request-line 變了但簽章沒變（已由「Cyberbiz 簽章實際涵蓋的範圍」那張表的第 3 列實測證實會 401）。

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

---

以下為 Module 3 學到的觀念（Step A 階段）。

**`r.json()` 之後，看到的已經不是 JSON 了**
- `r.json()` 把 JSON 文字轉換成 **Python 物件**（list / dict / str / int / float / None）。之後印出來的是 Python 的 repr，不是 JSON。
- 分辨方法：JSON 只能用**雙引號**、寫 `null` / `true`；Python repr 用**單引號**、寫 `None` / `True`。看到 `{'id': ...}` 和 `None` 就知道轉換已經發生了。
- 所以「JSON 看不出型別」是個誤會——**型別全都在**，只是要熟悉 Python 印出來的長相：

  | 看到的 | 型別 | 判斷依據 |
  |---|---|---|
  | `55508353` | `int` | 無引號、無小數點 |
  | `1000.0` | `float` | 無引號、**有**小數點 |
  | `'4377'` | `str` | 有引號 |
  | `None` / `True` | `NoneType` / `bool` | JSON 的 `null` / `true` |

- 但**別靠肉眼，用 `type()`**。這跟 Module 2 學到的「文件沒寫就直接印出來看」是同一招。

**Cyberbiz 訂單資料裡已經踩到的型別陷阱**
- `'order_number': 4377`（int）和 `'order_name': '4377'`（str）——**同一個數字、兩種型別**。`4377 == '4377'` 在 Python 是 `False`，之後跨系統比對會出事。這就是 Module 4 要用 `dataclass` + 型別標註的具體理由。
- `'subtotal_price': 1000.0` 是 `float`。**金額用浮點數是經典地雷**（精度問題），現在不處理但要記得。

**探索巢狀資料的方法**
- 結構就是 list 和 dict 層層包起來，導覽只有兩種操作：list 用 `[數字]`、dict 用 `['key']`。
- 別盯著一整坨值看。**一層一層來**，每層印 `type(它)`，是 dict 就再印 `.keys()` 拿一份乾淨的欄位清單。
- 排版工具：`json.dumps()` 加上縮排參數 + `ensure_ascii=False`（不然中文會變成 `\uXXXX`）。`ensure_ascii=False` 在 Module 7 寫 NDJSON 時會再遇到一次。
- **範圍控制**：Module 3 只需要知道「訂單清單在哪一層」和「沒有下一頁時長什麼樣」。欄位怎麼拆是 Module 4 的事，現在鑽進去只會在分頁還沒做完時就迷路。

**分頁參數的實測結果（`/v1/orders`）**
- 回傳的最外層是**一個裸 list**，不是有 `orders` key 的 dict。
- **終止訊號**：頁碼超過總頁數時回傳**空陣列 `[]`**（實測 `page=9999`）。
- `per_page=50` 實際拿到 50 筆。超過上限時回 **500** + `{"error":["系統有誤，請聯絡 CYBERBIZ"]}`——是**吵的失敗**（noisy failure），程式會停下來，不會默默給你錯的資料，這算好消息。
  - ⚠️ 給 Module 5 的預告：這個 500 是「參數給錯」造成的，**重試幾次都不會成功**。但 CURRICULUM 的 exception 階層把 5xx 歸在「重試」類。這不是階層設計錯，是伺服器用錯狀態碼（應該回 4xx）。真實世界的 API 常這樣。
- `offset` 已移除。實測「拿掉 offset」= 「offset=0」，它是多餘的；同時用兩套分頁機制卻只遞增其中一套是自找麻煩。**少一個變因，少一種出錯的方式。**
- 空陣列當終止條件的兩個延伸：
  - **一定會多送一次請求**（抓完最後一頁時還不知道那是最後一頁，要再問一次拿到空陣列才知道）。這是正常的。
  - **不要用「筆數 < per_page 就停」**：如果伺服器某次默默少給幾筆，這條件會提早成立、讓你以為抓完了。空陣列不受影響。

**Python truthiness（真假值）**
- 空的 list / dict / str，以及 `0`、`None`，在 `if` 裡都算「假」。
- 所以不用寫 `if len(data) == 0`，直接 `if not data:` 就成立。這個規則在 Python code 裡到處都是。

**`while True` + `break`：Python 沒有 do-while**
- 「**得先做一次才知道要不要繼續**」的迴圈，`while` 的條件式裡沒有東西可以檢查——要檢查的值是迴圈跑完一輪才產生的。
- 有些語言有 `do...while`，Python 沒有，慣用寫法就是條件寫 `True`、判斷放迴圈裡、用 `break` 跳出。
- `break` = 跳出整個迴圈；`continue` = 跳過這圈剩下的、直接進下一圈。

**`append` vs `extend`（踩過的地雷）**
- `fetch_page` 回傳的是**一頁的 list**（50 筆）。用 `append` 會把「整個 list」當成一個元素塞進去 → 得到 list of lists；用 `extend` 才是把裡面的元素逐個加進去。
- **兩個都不會報錯**，只會給你一個結構錯掉的東西。當時抓 10 頁、`len()` 印出 10，數字看起來很合理，差點矇混過去。
- 檢查方法：印 `len(all_orders[0])` 和 `type(all_orders[0])`，看第 0 個元素是一張訂單還是一整頁。

**函式的名字就是它的合約**
- 犯過的錯：`fetch_page` 同時做了三件事——送請求、把結果塞進外面的 `all_orders`、回傳 `all_orders`。但名字只承諾了一件事。
- 而且它**回傳錯東西**導致了另一個卡關：終止條件需要檢查「這一頁」是不是空的，但 `all_orders` 從第一次累積之後就永遠不是空的。**「不知道 while 條件怎麼寫」的真正原因是函式回傳錯東西。**
- 正確切法：`fetch_page` 收頁碼、回傳那一頁，就這樣。「累積到哪裡」是呼叫端的事。

**全域變數在函式之間拉出「看不見的線」**
- 靠修改外面的全域變數來傳結果，呼叫端得自己知道「喔它會偷偷改一個叫 `all_orders` 的東西」，函式回傳 `None`。這就是 Module 1「全域變數到處流竄」的味道。
- 改法：把 list 建在函式裡面當**區域變數**，最後 `return`。
- 判準（給參數用）：**這個函式，能不能只看它自己就知道它需要什麼？** `session` 因此變成參數（Module 5 要傳假的 session 進去測錯誤處理時會回本）。
- **常數和狀態是兩回事**：`url` 留在全域比 `session` 無害得多——它不會被改、也不持有連線。（Module 6 會收進 `Config`。）

**變數作用域，以及 `.extend()` 為什麼「能」改到全域**
- 函式裡面的變數是那個函式的私有物，外面看不見。
- 但當時 `append_orders(data)` 能改到全域的 `all_orders`，是因為 **`.extend()` 是就地修改**（沒有重新綁定名字）。
- 如果寫成 `all_orders = all_orders + data`（**重新賦值**），Python 會直接報 `UnboundLocalError`。**兩種寫法看起來差不多，行為完全不同。**

**開發時要給迴圈加保險**
- 除錯階段先在 `while` 裡加硬上限（例如超過 20 頁就 break）。終止條件寫錯時，無窮迴圈會一直打**別人的**伺服器，可能被限流。確認邏輯正確後再拿掉。

**Step A 的痛（親身感受到的，不是課本說的）**
- 實跑 3366 筆、每頁 50 筆 ≈ 68 次請求，**等很久**。
- 三個具體痛點：(1) 在整包 list 回傳之前，呼叫端拿不到任何東西——第一筆訂單其實幾百毫秒就到手了，卻要等全部跑完才碰得到；(2) 所有資料同時佔記憶體；(3) **第 87 頁掛掉，前 86 頁的成果全部陪葬**。
- 對 Step B 的期待要先校準好：

  | 痛點 | generator 解嗎 |
  |---|---|
  | 要等全部抓完才拿得到第一筆 | **解** |
  | 全部資料同時佔記憶體 | **解**（一次只留一頁） |
  | 第 87 頁掛掉，前面的成果 | **部分解**（前面的已經流出去被處理掉，不會陪葬） |
  | 掛掉之後**自動重試** | **不解**，那是 Module 5 |

- 關鍵：**generator 不會讓失敗消失，但它讓「失敗之前的工作」不會白做。**

---

以下為 Module 3 學到的觀念（Step B：generator）。

**generator function 和 generator 物件是兩個不同的東西**
- 函式體裡有 `yield` 的那個函式叫 **generator function**；呼叫它得到的才是 **generator 物件**。
- **建立 frame 的動作是「呼叫」，不是「指派給變數」**。`iter_orders()` 那對括號一打，物件就建好了；指派只是給這個已經存在的物件取個名字。就算不指派（`for x in iter_orders():`）也一樣。
- 函式可以呼叫很多次，每次給一個**全新的** generator；generator 物件用完就沒了。
- 犯過的錯：以為「宣告成兩個不同的變數就能跑兩次」。`r2 = r` 確實是兩個變數，但它們是**同一個物件**的兩個名字，游標只有一個，第二個迴圈照樣一圈都不跑。**變數不同 ≠ 物件不同。**

**`yield` 是暫停，不是輸出**
- 曾經的心智模型（模型 A）：函式從頭跑到尾，一路上遇到 `yield` 就往外丟一個值，像水管漏水。**錯的。**
- 實際（模型 B）：跑到 `yield` 就**凍結**，控制權交還呼叫端。區域變數、迴圈跑到第幾圈、執行到第幾行全部保留。呼叫端下次要值，才從凍結的那一行**繼續**。
- 保存這些東西的是**執行框架（stack frame）**。普通函式 `return` 的瞬間 frame 被丟掉，所以沒有記憶；generator 的 frame 掛在物件身上，不丟。
- `yield` 的英文原意是「讓出（控制權）」，不是「產出」。這就是「控制流反轉」：普通函式是你呼叫它、它跑完還你；generator 是兩邊**輪流跑**，一人一段。
- 實測驗證三步：`r = f()` 之後函式體**一行都沒跑**（第一個 print 沒出現）→ 第一次 `next()` 才開始跑 → 第二次 `next()` 從上次停的地方繼續（函式內迴圈的計數器**沒有歸零**，這就是「暫停」而非「重跑」的證據）。

**`yield` 後面接的是表達式，會先被求值**
- 踩過的坑：寫 `yield print("hello")`。實際順序是「先呼叫 `print` → 畫面出現 hello、拿到它的回傳值 → `yield` **那個回傳值**」。
- **`print()` 的回傳值是 `None`**，所以呼叫端拿到的是 `None`。文件沒特別寫，因為 Python 的通則是：函式沒有 `return`、或 `return` 後面沒接東西，回傳值就是 `None`。凡是文件裡沒有 "Return" 那段的函式都是這種。
- 通則：Python 不會把「一段程式碼」當成值傳來傳去，它一定先算出結果再交出去。`yield` 在這點上跟 `return` 沒有任何差別。
- 教訓：**「函式內部印出來的東西」和「交給呼叫端的值」是兩條不同的路。** 觀察 generator 時這兩件事要分開寫，不要疊在同一行。

**iterator protocol：`for` 迴圈的真面目**
- dunder method（前後兩條底線）是 Python 的**協定**：語法糖背後對應到特定名字的方法。`len(x)` → `x.__len__()`，`a + b` → `a.__add__(b)`。
- **iterable**（可迭代物）：有 `__iter__()`，意思是「我可以被走過一遍」。list、dict、str、檔案物件都是。
- **iterator**（迭代器）：有 `__next__()`，是一個**有狀態的游標**，記得自己走到哪了。
- `for x in things:` 實際做三件事：(1) 呼叫 `iter(things)` 拿到一個 iterator；(2) 反覆呼叫它的 `__next__()`，每次跑一輪迴圈本體；(3) 接到 `StopIteration` 就結束。
- 所以 **`for` 從來沒有「一次拿到全部資料」過**，它一直都是一次要一個。這就是 generator 能無縫接上 `for` 的原因。
- 文件說「generator 會自動產生 `__iter__()` 和 `__next__()`」的意思是：這件事以前要手寫一個 class、自己用 instance 變數記進度；`yield` 讓「記進度」變成「保留 frame 的執行位置」，寫函式就好。文件在講的是**省掉了什麼**。

**`StopIteration` 一定會被丟出來，只是 `for` 幫你接住**
- 手動 `next()` 到底 → 沒人接 → traceback 直接炸到畫面上（實測看到了）。
- 用 `for` → 例外被 `for` 內部的 `try` 吃掉 → 迴圈安靜結束。
- `next()` 可以傳第二個參數當預設值，值用完回傳它而不丟例外。

**generator 只能走一次，而且是「安靜地」失敗**
- 對同一個 generator 物件跑第二次 `for`：**一圈都不跑，也不報錯**，輸出裡完全感受不到它的存在。
- 原因是結構性的：list 是 iterable 但**不是** iterator，每次 `iter()` 給你一個全新的游標；**generator 的 `__iter__()` 回傳的是它自己**，資料和游標長在一起。
- 對照組：同一段程式把 generator 換成 list，兩個迴圈各跑滿。
- **這是實務上最該提防的 bug 類型。** 對照 `yield` / `yield from` 寫反會直接丟 `TypeError`——**會炸的 bug 是好 bug**，安靜的這種才難查。要再跑一次只能**重新呼叫一次 generator function**。

**`yield from` = 攤平一層**
- `yield from <可迭代物>` **完全等於**「對它跑一個 `for`，每一圈把元素 `yield` 出去」。
- 兩個誤解先擋掉：它**不是**「一次把整個 list 交出去」（呼叫端拿到的還是一個一個的元素）；`from` 後面接的是**要被拆開來逐一交出去的東西**，不是「資料來源」的意思。
- 實測：把 `yield from data` 改成 `yield data`（少一個字），呼叫端的「一單位」就從一筆訂單變成一頁 50 筆，`order['id']` 直接丟 `TypeError: list indices must be integers`。
- 這一個字就是 Step B 的核心：**`yield from` 讓呼叫端不必知道有分頁這回事**；`yield data` 會把分頁的存在洩漏給呼叫端。
- 「這一頁發到第幾筆了」**不需要自己用變數記**——那是 frame 的工作。規劃時曾寫過「看有沒有暫存的資料 → 有就逐筆發、沒有才抓下一頁」的分支判斷，那整套是在手動重建 Python 已經做好的事，一個 `yield from` 就沒了。

**generator 裡的 `return`**
- 它同時終結**兩個不同地方的迴圈**：generator 內部的 `while`，以及**呼叫端的 `for`**。
- 機制：函式結束 → 觸發 `StopIteration` → 呼叫端的 `for` 收到訊號結束。這是 generator 跟呼叫端**唯一的溝通管道**。
- `break` 和 `return` 在這裡效果相同（`break` 跳出 while 之後函式一樣執行到底 → 一樣觸發 `StopIteration`）。CURRICULUM 用 `return` 只是少一層縮排。
- generator 裡的 `return X` 不再是「回傳 X 給呼叫端」。所以**不可能寫一個「有時候回傳 list、有時候 yield」的函式**。

**generator function 的身分在編譯期就決定**
- 函式體裡只要出現 `yield`，這個函式**整個**變成 generator function——就算那個 `yield` 寫在 `if False:` 底下、或 `return` 後面的死碼裡也一樣。
- 判斷發生在**編譯期**（原始碼轉 bytecode 的階段），早於任何一行被執行，跟執行路徑無關。

**lazy 的好處什麼時候才兌現**
- 兩種暫存要分清楚：

  | | 存什麼 | 大小 | 會不會長大 |
  |---|---|---|---|
  | **有界的暫存** | `fetch_page` 剛拿回來的那一頁 | 50 筆 | 不會，下一頁蓋掉上一頁 |
  | **無界的累積** | `all_orders` | 最後 3366 筆 | 會，一路長到跑完 |

- Module 3 要拆掉的是第二種。第一種**非存不可**——HTTP 一次就回 50 筆，總得先落在某個變數上。
- 記憶體峰值：Step A 是 3366；Step B 是 50（當頁）+ 1（呼叫端手上那筆）= 51，**跟總筆數無關**。3366 筆能跑，336 萬筆也能跑，程式一個字不用改。
- **但一旦 materialize 就沒省到**：`list(iter_orders())` 一行就等價於整個 Step A，峰值回到 3366。**lazy 的好處只在「不需要同時持有全部」時才存在。**
- 就算 materialize，還有兩個好處不會消失：第一筆資料**更快到手**（不用等 69 次 HTTP 全跑完）、呼叫端**可以提早中止**。
- 真正需要「全部到齊」的操作是：**排序、隨機存取、要走第二次**。**加總不算**——加總可以邊走邊累加，記憶體是常數。曾經以為「要算總金額所以得先湊齊」，那是錯的。
- `all_orders` 在 Step A 存在的理由，其實是被 `return` 逼出來的：**`return` 只能交出一次，所以必須先湊齊。** `yield` 可以交 3366 次，這個理由就消失了。
- 由此看控制流反轉的真正意義：中間層不再替呼叫端決定「你會拿到全部」，而是把**「要不要全部、要多少」的決定權交還給呼叫端**。

**Step B 的實測數據（驗收證據）**
- 完整跑一次：`fetch_page` 被呼叫 **69 次**。3366 ÷ 50 = 67.32，所以 68 頁有資料（第 68 頁只有 16 筆），第 69 次拿到空陣列才知道結束。
- 呼叫端只取前 10 筆：`fetch_page` 只被呼叫 **1 次**。這是 lazy evaluation 最直接的證據。
- **`fetch_page` 到底什麼時候被呼叫**：呼叫端每要一筆，generator 解凍一次；但絕大多數時候只是把手上 `data` 的下一筆交出去就再度凍結。**只有這一頁 50 筆全部交完，`yield from` 才結束、`while` 才進下一圈去呼叫 `fetch_page`。** 具體說：呼叫端第 1 次要求觸發 HTTP，第 2～50 次都是從記憶體拿，第 51 次才觸發第二次。
- 三個 print 的位置缺一不可：`fetch_page` 裡（HTTP 何時發生）、generator 迴圈裡（換頁）、**呼叫端的 `for` 裡（第幾筆）**。第三個最關鍵——沒有它就只看得到 generator 這一側，看不出「兩邊在輪流跑」。呼叫端沒有 `page_num` 這個變數，只能印累計筆數；**兩把不同的尺交錯起來**才構成證據。

**`itertools.islice`：給 iterator 用的切片**
- list 可以 `lst[:10]`，generator 不行——它不支援 `[]`。因為切片預設你可以「跳到第 10 個」，而 generator 只能一步一步往前走，沒有「第幾個」這個概念。
- 簽章：`islice(可迭代物, stop)` / `islice(可迭代物, start, stop[, step])`。
- 三個性質：(1) 它自己也是 lazy 的，回傳 iterator 不是 list，所以 `islice(gen, 10)` 這行執行完一筆都還沒抓；(2) 用法是放到 `for` 的 `in` 後面；(3) **只能往前走**，`islice(gen, 100, 110)` 是真的把前 100 筆走過去丟掉，不是跳過去。
- 跟手寫 `enumerate` + `if / else / break` 比：功能相同，但 `islice` 把「要幾筆」表達在**一個地方**，而不是散在控制流裡。

**怎麼讀 Python 官方文件（這一輪的方法論收穫）**
- 文件分四種，用途完全不同：

  | 類型 | 網址 | 性質 |
  |---|---|---|
  | Tutorial | `/tutorial/` | 教材，循序漸進、有範例 |
  | HOWTO | `/howto/` | 專題教學，針對一個主題深入講，範例多 |
  | **Library Reference** | `/library/` | **規格書**，假設你已經知道這東西大概是什麼，來查參數和行為 |
  | Language Reference | `/reference/` | 語言的形式規格，給實作 Python 的人看 |

- **看不懂通常是文件類型選錯，不是閱讀能力問題。** 正確順序是 HOWTO / Tutorial 建立概念 → Library Reference 查細節，反過來會很痛苦。以 itertools 為例，該先讀的是 https://docs.python.org/3/howto/functional.html#the-itertools-module
- 讀一個函式條目：粗體那行是**簽章（signature）**，括號裡是參數，**參數名本身就是資訊**（`iterable` 在告訴你該放什麼）；方括號 `[...]` 表示選用參數；列兩行代表有兩種呼叫形式。
- **itertools 特有的坑**：每個條目附一段 "Roughly equivalent to:" 的等價 Python 實作（因為真正的實作是 C，看不到原始碼）。對熟手最精確，對初學者是災難，**可以直接跳過那段**。
- 模組頁的**第一句話**就是它的定位（itertools 是 "Functions creating iterators for efficient looping"）。頁面上方通常有**摘要表格**，先看表再看條目，比從頭讀到尾有效率。
- 卡住時的三個動作：(1) 開 REPL 邊讀邊試，拿 `range(100)` 當白老鼠；(2) REPL 裡 `help(某個東西)` 直接印出文件，不用切瀏覽器；(3) 看原始碼。這是 Module 2「文件沒寫就直接印出來看」的延伸。

---

以下為 Module 4 學到的觀念（資料模型與型別）。

**型別標註在 runtime 只是「備註」，不是「規則」**
- 實測：`Order` 的 `id` 標成 `int`，然後 `o.id = 'hello'`，Python 完全照收，不報錯也不警告。
- 原因：Python 只是把標註**登記**在 `__annotations__` 裡就沒事了，沒有任何機制會去讀它、拿它比對。它是備註，不是檢查。
- 所以型別標註**單獨存在時毫無防護力**。它要跟 mypy 成組才有意義。

**mypy 預設不檢查沒有標註的函式內部——標註是在「開權限」**
- 實測（這輪最有價值的實驗）：在完全沒標註的 `fetch_page` 裡塞一行 `x: int = "我是一個字串"`（不折不扣的型別錯誤），跑 `mypy src/` → **`Success: no issues found`**。
- mypy 自己說出原因：`By default the bodies of untyped functions are not checked`。
- 只把 `fetch_page` 的簽章加上標註，同一行程式碼、同一個 mypy → **立刻抓到**。
- 結論：**沒標註的函式對 mypy 是一塊進不去的黑箱。** 標註不是裝飾也不是文件，是在對 mypy 開權限。CURRICULUM 要求「全專案函式簽章補上標註」的真正理由在這裡。
- 推論：一個專案如果只標了一半，`mypy` 跑出 `Success` 可能只是因為它根本沒看那一半。

**「靜態」的意思，以及 mypy 為什麼抓得到 `.totl` 卻抓不到 `["totl"]`**
- 驗收實測：
  | 寫法 | mypy |
  |---|---|
  | `o.subtotal_pirce`（`o` 是 `Order`） | `"Order" has no attribute "subtotal_pirce"; maybe "subtotal_price"?` |
  | `order['subtotal_pirce']`（`order` 是 `dict`） | `Success`，完全沒吭聲 |
- 一句話的原因：**`Order` 帶著一份「我有哪些名字」的清單，`dict` 沒有。**
- 為什麼 dict 不可能有：dict 的本質就是「執行時想放什麼 key 就放什麼 key」，隨時可以 `d['隨便什麼'] = 1`。「合法 key 清單」這個東西對 dict 根本不存在。
- 更深一層是**時間點**：`Order` 的名單寫死在原始碼裡，用讀的就讀到了；dict 有哪些 key 要等程式跑起來、API 回應了才知道，**那時候 mypy 早就下班了**。
- **static（靜態）= 不執行程式，只讀原始碼。** mypy 只看得到「寫在原始碼裡的事實」。
- 所以 `dataclass` 真正在做的事是：**把「這筆資料有哪些欄位」這個知識，從執行時搬到原始碼裡，讓 mypy 讀得到。**
- 注意：`o.totl` 和 `raw['totl']` **在 runtime 都會炸**（`AttributeError` / `KeyError`），差別不在會不會炸，而在**炸之前有沒有人先攔住你**。

**`Optional`（`str | None`）的完整樣貌**
- 定義：一個「可能是 None」的值，被當成「一定不是 None」在用。
- 實測撞到兩次，錯誤訊息不同但病因相同：
  - `r.method + ' '` → `Unsupported left operand type for + ("None")`
  - `o.delivery_date.split('-')` → `Item "None" of "str | None" has no attribute "split"`
- **mypy 不接受口頭保證。** 說「實務上它一定有值」沒用，必須在程式碼裡**寫出**「萬一是 None 會怎樣」。
- 兩種處理方式：給替代值，或中止。**中止用 `raise`，不是 `return`。**
- 犯過的錯：寫 `return print('HTTP method required.')`。這根本不是中止——它印一行字，然後把 `print()` 的回傳值 `None` **交還給呼叫者**（requests），程式繼續帶著一個 `None` 往下跑。mypy 抓到了：`Incompatible return value type (got "None", expected "PreparedRequest")`。
- 順帶學到的寫法：不正常的情況**先擋掉就走人**，正常路徑留在主線上不要被包進 `if` 裡。用 `raise` 之後 `else:` 整塊就消失了。
- `if r.method:` 和 `if r.method is None:` 不一樣——前者連空字串 `''` 一起擋掉。mypy 要求排除的只有 `None`，多擋的那個是自己沒想清楚就加上去的行為。

**`r.method` 為什麼會是 `str | None`（不是 requests 的特例）**
- `PreparedRequest` 是一個**分階段組裝**的物件：requests 內部先建空殼，再逐步把 method、url、headers、body 填進去。所以型別定義裡 `method` 從一開始就宣告成「可能還沒填」。
- 實務上等 `__call__` 被呼叫時 method 早就填好了，所以程式跑幾十次都沒事。但**型別系統不知道「實務上」**，它只讀得到宣告。

**預設值只能用在「這個預設值本身就是對的」的時候**
- 曾經想過：`r.method` 沒值就預設用 `'GET'`，反正現在全部都是 GET，應該還是會成功。
- 為什麼是錯的：簽章的內容**必須跟實際送出去的請求一模一樣**。哪天有人加了 POST 而 method 剛好沒填 → 簽的是 `GET /...`、送的是 `POST /...` → 伺服器重算對不上 → **401**。
- 更糟的是**錯誤現場離原因很遠**：你會去查金鑰、時間戳、編碼、header 順序，查一整個下午，而真正的原因是 method 沒設定。
- 通則：**填預設值不是因為它對，而是因為在猜的時候，就是在製造這種 bug。**

**`classmethod` 作為「另一種建構子」是 Python 慣例**
- `Order.from_api(raw)` 和模組層級的 `make_order(raw)` **功能完全一樣**，差別在三件事。
- **1. 慣例**：同一個型別的各種建構方式，住在那個型別裡面。已經用過的例子就是 `datetime.now()` / `datetime.fromtimestamp()` / `datetime.fromisoformat()`——全是 classmethod，全是「造出一個 datetime 的不同方式」。沒有人寫 `make_datetime_from_timestamp()`。
- **2. 找得到**：編輯器打 `Order.` 就會列出 `from_api`。不用先知道名字就能發現它。散在模組裡的函式要靠記得名字或翻檔案。
- **3. `cls` 的真正用途**：`cls` = **「呼叫我的那個類別」**，不是「我被定義在哪個類別」。如果之後有 `class PosOrder(Order)`，`PosOrder.from_api(raw)` 因為 `cls` 收到的是 `PosOrder`，會生出 `PosOrder`；寫死 `return Order(...)` 的話會生出 `Order`——**型別錯了，而且錯得很安靜**。
- 所以「現在改成寫死 `Order(...)` 會不會壞」的答案是：現在不會，有繼承時才會。但那正是 `cls` 存在的理由。

**`-> "Order"` 為什麼要加引號**
- 那行簽章被執行的時候，`Order` 這個 class **還在定義中、還不存在**，直接寫 `Order` 會 `NameError`。
- 包成字串後 Python 不會去解析它，而 mypy 看得懂。

**一行簽章裡三個東西是獨立的**
- `def from_api(cls, raw: dict) -> "Order":`
  - **`cls`** — 類別被帶進來的地方。做這件事的是 `@classmethod`，跟任何標註無關。呼叫 `Order.from_api(x)` 時 Python 實際跑的是 `from_api(Order, x)`。
  - **`raw: dict`** — 參數標註。
  - **`-> "Order"`** — 回傳標註。**對執行完全沒有影響**：整段刪掉程式一模一樣跑，改成 `-> int` 也照跑、照回傳 `Order`。
- 曾經誤以為 `-> "Order"` 是「指定要帶進函式的 class」。不是。`cls` 是實際流進去的**貨**，`-> "Order"` 是貼在箱子外面的**標籤**。撕掉標籤箱子裡的東西不變，只是沒人知道裡面裝什麼。
- 標註的三個讀者：**mypy**（唯一會拿它抓錯的）、讀 code 的人、**編輯器**（`o.` 之後跳出 9 個欄位的自動完成就是靠它）。

**「什麼都是」等於「沒說什麼」——階層頂端的型別不要用**
- 犯過的錯：把 session 標成 `session: object`，mypy 報 `"object" has no attribute "get"`。
- `object` 是 Python 型別階層的**最頂端**，所有型別都是它的後代。標成 `object` 等於說「我只知道它存在，其他一無所知」，所以呼叫 `.get()` 就被攔。
- **這不是 mypy 找碴，是它照你的話做**：你聲明只給它一個泛泛的東西，卻要對它做具體的事。
- 要標的是**那個變數實際的類別**——看它是怎麼建出來的（`s = requests.Session()` → 型別是 `requests.Session`，去掉括號；括號是「呼叫它、生一個出來」）。
- 同一個形狀出現在例外上：`raise Exception(...)` 的 `Exception` 是例外階層的最頂端，接的人分不出這是網路問題、認證問題還是資料問題。（Module 5 要處理。）

**方括號是在說「裡面裝什麼」**
- `Iterator[dict]` = 「一個迭代器，每次交出一個 dict」。`list[str]` = 「裝 str 的 list」。`dict[str, int]` = 「key 是 str、value 是 int 的 dict」。
- 光寫 `list` 只說了容器種類，加方括號才說了內容物。
- generator function 的回傳型別標的是「**呼叫它會得到什麼**」——不是 list，是那個「之後可以逐筆走」的東西，所以是 `Iterator[dict]`（`from collections.abc import Iterator`）。

**「邊界」= 資料從哪裡開始被轉換成我們自己要的型別**
- 任何外部系統（API、資料庫、檔案）給的資料，格式都是**對方定的**。程式裡應該有一條線，資料跨過這條線就變成自己的型別。那條線就是邊界。
- 判斷標準只有一個：**邊界越靠外，程式裡「mypy 罩不到」的區域就越小。** 所以預設答案是「能多外就多外，資料進門第一時間就轉換」。
- 目前這個專案的資料流：`API → r.json() → dict → dict → dict → [邊界] → Order`，邊界在最右邊（呼叫端）。raw dict 一路流過 `fetch_page`、generator、到呼叫端，全程 mypy 幫不上忙。
- **但「越外越好」是預設值，不是鐵律。** 這個 pipeline 的主要工作是**搬運**——把 Cyberbiz 完整資料搬進 BQ，而 `Order` 只認識 9 個欄位。把邊界移到 generator 出口（`Iterator[Order]`）等於在邊界上**燒掉 44 個欄位**，下游再也拿不回來。
- 所以判斷是：**當一條路的任務就是「原封不動搬東西」時，不要在中間插一個只認識部分欄位的型別。**

**`TypedDict` vs `dataclass`（CURRICULUM 思考題的答案）**
- 矛盾是：**同時**想要「完整的 53 個欄位」和「mypy 看得住的型別」。`dataclass` 給你後者但犧牲前者。
- `TypedDict` 就是為這個情境存在的：

  | | `dataclass` | `TypedDict` |
  |---|---|---|
  | 執行時是什麼 | **一個新物件** | **還是那個 dict**，一模一樣 |
  | 取值 | `o.subtotal_price` | `raw["subtotal_price"]` |
  | mypy 有沒有名單 | 有 | **有** |
  | 能不能直接 `json.dump` | 不行，要先轉回 dict | 可以，它本來就是 dict |

- **關鍵在第一列：`TypedDict` 在執行時什麼都不做。** 它不建立新物件、不轉換任何東西，純粹是「附一張 key 名單給 mypy 看」。所以 dict 保持完整 53 欄、可以直接 dump 進 BQ，同時 `raw["subtotal_pirce"]` 會被 mypy 抓到。
- **兩者的邊界：資料只是路過 → `TypedDict`。資料要被程式讀欄位、做判斷、加方法 → `dataclass`。** 不是二選一，是兩件不同的事。

**一筆樣本不足以推論型別（這輪最實用的教訓）**
- 掃第 1 筆訂單時，`delivery_date` 是 `str`、`payment_name` 是 `str`、`einvoice` 是 `dict`，看起來都很安全。
- 掃 50 筆之後才發現**三個全都可以是 `null`**。只憑一筆就寫 `delivery_date: str`，程式會在某一筆訂單上炸掉。
- 所以盤點欄位的正確做法不是「印一筆出來看」，而是**掃一批、對每個 key 統計出現過哪些型別**（`defaultdict(set)` + `type(v).__name__`）。
- 反過來也要誠實：50 筆裡全是 `None` 的欄位，**只證明「這批樣本裡它是空的」**，不證明它的真實型別。這種欄位要嘛去翻文件，要嘛判定為「這個帳號沒開的功能」直接不收。

**Python 的日常工具（這輪補起來的基本功）**
- **互動模式**：終端機打 `python` 進 `>>>`，打什麼立刻執行並印出結果，不用寫檔存檔。`exit()` 或 Ctrl-D 離開。**測任何東西的第一選擇。**
  - 多行輸入：結尾有 `:` 按 Enter 後提示符變 `...`，下一行**要自己按空白鍵縮排**，打完後**再按一次 Enter（空行）**整段才會跑。看起來卡住通常就是漏了最後那個空行。
  - 上下方向鍵可以叫回上一次打過的內容。
- **`python -i script.py`**：跑完檔案後不退出，直接進互動模式，檔案裡所有變數都還活著可以摸。只吃 `.py`，不能吃 `.json`。
- **讀 JSON 檔**：`f = open('x.json', encoding='utf-8')` → `json.load(f)`。
- **寫 JSON 檔**：`f = open('x.json', 'w', encoding='utf-8')` → `json.dump(物件, f, indent=2, ensure_ascii=False)` → **`f.close()`**（不 close 資料可能還卡在記憶體沒落地，打開檔案會看到空的）。
  - 差別只有兩個：`open` 多第二個參數 `'w'`，`load`（讀進來）換成 `dump`（寫進去）。
- **`type(v).__name__`**：`type(v)` 給的是型別物件（印出來 `<class 'int'>`），`.__name__` 給的是乾淨字串 `'int'`。要放進表格、比對、當 set 的元素時用後者。`type(None).__name__` 是 `'NoneType'`。
- **`defaultdict`**：`counts['apple'] += 1` 對空 dict 會 `KeyError`，因為 `+=` 要先讀舊值。`defaultdict(int)` 在建容器時就講好「找不到就自動生一個」。
  - **傳的是函式本身（`int`、`list`、`set`），不是呼叫結果（`int()`）。** 差一對括號意思完全不同：前者是「這是製造預設值的方法，你需要時自己叫它」，後者是「這是一個已經做好的 0」。
  - **這跟 `dataclass` 的 `field(default_factory=list)` 是同一個概念**（本輪沒實際用到 `default_factory`，因為 9 個欄位全是純量）。
- **`set`**：`add()` 重複加同一個東西只會留一份。語意是「有出現過哪些」，不管幾次、不管順序。
- **`.items()`**：`for k, v in d.items():` 一次拿到 key 和 value。
- **`types-requests`**：`requests` 本身沒有型別標註（它比 type hints 早出生），社群另外維護一包**只有簽章、沒有實作**的 `.pyi` 檔案叫 **stub**（概念等同 C 的 header file），打包成 `types-requests`。沒裝的話 mypy 會報 `Library stubs not installed for "requests"`——**那不是你的 code 有問題，是 mypy 看不到 requests 的型別。**

---

以下為 Module 5 學到的觀念（錯誤處理與重試）。

**`requests` 不會因為 HTTP 錯誤而拋例外**
- 401、429、500 拿回來的**一樣是一個正常的 response 物件**，`r.json()` 照跑，程式一句話都不會說。
- 這是 requests 的設計立場：HTTP 錯誤代表「伺服器正常回答了你，只是答案是壞消息」，那不是 Python 層級的錯誤。**要不要把壞消息當成錯誤，是你的決定，不是它的。**
- 由此推出 Module 5 第一層要做的事：**必須自己去看 status code**，沒有人會替你看。

**目前這支程式對失敗完全沒有防護（實測）**
- 實驗：`per_page` 改成 `500` 觸發伺服器 500，單獨呼叫一次 `fetch_page`。
- 回傳值是 `{'error': ['系統有誤，請聯絡 CYBERBIZ']}`，型別 `dict`。
- 這個 dict 流回 generator 之後會發生的事，一步一步是：
  1. `if data:` → dict 非空 → **為真**（空 dict 才是假）
  2. `yield from data` → **對 dict 迭代交出的是 key**，所以呼叫端拿到的是字串 `'error'`
  3. `Order.from_api('error')` → `raw: dict` 這個標註 **runtime 什麼都不做**，不會在進門時擋下來
  4. 一路跑到 `raw['id']` 才炸成 `TypeError: string indices must be integers`
- **錯誤要跨過五層才第一次被發現**（`fetch_page` → generator → 呼叫端 → `from_api` → `raw['id']`），而訊息一個字都不會提到 500、`per_page` 或 Cyberbiz。
- 這就是「沒有偵測層」的代價，形狀跟 Module 4 記過的那條一模一樣：**錯誤現場離原因很遠。**

**例外機制：`raise` 之後發生什麼**
- `raise` 做兩件事：**立刻中止當前函式**（後面的程式碼一行都不會跑），然後把例外物件**交給呼叫我的人**。
- 例外沿著**呼叫堆疊**一路往外冒泡，直到有人接住；一路冒到最外層還沒人接，Python 中止整個程式並印出 traceback。
- **traceback 由下往上讀**：最下面是實際炸掉的那一行，往上每一層是「誰呼叫了它」。
- 接住用 `try` / `except`，而 **`except` 是用「型別」決定接不接的**——這是整個 Module 5 的樞紐。
- 這個機制 Module 3 已經見過一次：`for` 迴圈內部就是 `try` 包著 `next()`，`except StopIteration` 之後安靜結束。那個「安靜結束」不是 `for` 的特異功能，就是這套機制。

**例外的兩個「往上」是完全不同的東西（這一輪最重要的修正）**
- 犯過的錯：以為「例外往外傳的過程中會**經過** `CyberbizError`」。**錯的**，把兩件事疊成了一件：

  | | 「往上」是什麼意思 | 什麼時候發生 |
  |---|---|---|
  | **呼叫堆疊**（call stack） | `raw['id']` → `from_api` → 呼叫端 → … | **執行時**，例外真的在移動 |
  | **類別階層**（class hierarchy） | `AuthError` → `CyberbizError` → `Exception` | **寫在原始碼裡**，靜止不動 |

- 例外物件**只走第一種**。`CyberbizError` 不是路上的一站，**它不是一個地點**。
- 階層起作用的時機是**某個 `except` 那一行被檢查的瞬間**，Python 問的是一個純粹的型別問題：「這個物件的類別，是不是 `CyberbizError` 或它的後代？」是 → 接住；不是 → 繼續往上冒。
- 一句話：**階層決定的是「誰接得住誰」，不是「往哪裡走」。**

**共同父類別買到的是什麼**
- `except CyberbizError:` **一行就接住四個子類別**，不用把四種各寫一次。
- 而且接得住的**只有**這四種——`requests` 的 `ConnectionError`、Python 的 `KeyError` / `TypeError` 全都接不住，會照樣往外冒。
- 所以共同父類別同時給了兩件事：**一次接一整類**，以及**劃出「這是我們自己定義的錯」和「別人的錯」的界線**。

**只有繼承自 `BaseException` 的類別才能被 `raise`**
- 犯過的錯：在 `errors.py` 自己造了一個 `class Error: pass` 當根。直覺（「應該要有一個更廣泛的父類別標記所有錯誤」）是對的，但 **Python 已經有那棵樹了**，不需要自己種。
- 而且自己種的這棵**會直接壞掉**：沒有繼承任何東西的 class 預設繼承 `object`（LEARNINGS 前面〈什麼都是等於沒說什麼〉那個 `object`），跟例外系統毫無關係。
- ⬜ **待實測**：REPL 跑 `class Error: pass` → `raise Error()`，看錯誤訊息。
- ⬜ **待補的觀念**：`BaseException` 和 `Exception` 的差別，以及自訂例外該接哪一個。