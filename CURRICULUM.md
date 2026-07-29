# 專案：從零手刻 Cyberbiz Extractor

## 這份文件是什麼

一份 13 個 Module 的 Python 練習課綱。目標**不是**做出一個能用的 pipeline（那個已經有了），而是透過重建的過程，讓自己有能力讀懂別人（或 agent）寫的 Python。

---

## 課程設計說明

每個 Module 的模式固定：

> 先用會痛的方式做出來 → 感受痛點 → 用語言特性解決 → 驗收

如果某個 Module 你覺得「這不是多此一舉嗎」，代表你還沒感受到痛點。回去把上一版的資料量放大、或把錯誤情境加進去，痛感自然會出現。

### 三條規則

1. **不准打開舊的 `extract.py`**，直到 Module 12 的驗收
2. 不用 agent 寫實作，但可以用 agent 問觀念、查文件
3. 每個 Module 結束時 commit 一次，訊息寫「這一版解決了什麼」

---

## Module 0：環境與最小可執行

**目標**：一個能跑的空專案。

- 建 `venv`（或 `uv`，如果想順便學新工具）
- 建立目錄結構，只要這樣就好，先不要過度設計：

```
cbz-extract/
  pyproject.toml
  src/cbz_extract/__init__.py
  src/cbz_extract/main.py
  .env.example
  .gitignore
```

- `pyproject.toml` 用 `[project]` 寫最基本的 metadata，然後 `pip install -e .`

**驗收**：在任何目錄下執行 `python -c "import cbz_extract"` 成功。

**學習重點**：套件 vs 模組、`__init__.py` 的角色、editable install 為什麼能讓 import 到處都通。這和 Docker image layering 是類似的心智模型——先搞清楚「Python 怎麼找到你的 code」。

**卡住的話**：先弄清楚 `sys.path` 是什麼。`python -c "import sys; print(sys.path)"` 印出來看。

---

## Module 1：最醜的可行版本

**目標**：一支 60 行以內的 script，成功抓到一頁訂單並 `print` 出來。

**刻意要做壞的地方**：

- API key 直接寫死在檔案裡（等下會拿掉，先體驗）
- 沒有函式，從上到下一路寫
- 沒有錯誤處理
- 只抓第一頁

**驗收**：終端機印出真實訂單資料。

**學習重點**：這一版存在的意義是當**基準線**。之後每個 Module 都是在改善它，你會清楚看到「多寫的那些結構到底換到了什麼」。很多人學不好架構，就是因為從沒體驗過沒有架構的樣子。

---

## Module 2：HTTP Signature 手刻

**目標**：不查舊 code，重新實作一次 HTTP Signature 認證。

- 讀 Cyberbiz 文件，確認簽章要涵蓋哪些欄位、順序如何
- 用 `hmac` + `hashlib` + `base64` 產生簽章
- `datetime` 產生符合規格的時間戳（注意 RFC 格式和時區）
- 把 `requests.Session` 引進來，理解為什麼比每次 `requests.get()` 好

**驗收**：把系統時間往前調 10 分鐘，請求應該被 API 拒絕。而且你要能解釋為什麼。

**學習重點**：`hmac.new()` 的三個參數各是什麼、`bytes` vs `str` 的轉換（`.encode()` 到底在幹嘛）、`hexdigest()` vs `digest()` 的差別。這裡是最容易「抄得動但不懂」的地方，值得慢慢來。

**延伸**：把簽章邏輯寫成一個 `requests.auth.AuthBase` 的子類別。你會第一次體會到「繼承一個框架的類別」是什麼感覺。

---

## Module 3：分頁與 generator ⭐

**目標**：抓完所有頁，但不要把全部資料塞進一個 list。

分兩步做，兩步都要寫，不要跳。

### Step A：list 版本

`while` 迴圈 + `all_orders.append(...)`，回傳完整 list。

### Step B：generator 版本

```python
def iter_orders(session, since):
    page = 1
    while True:
        data = fetch_page(session, since, page)
        if not data["orders"]:
            return
        yield from data["orders"]
        page += 1
```

**驗收**：兩個版本都跑一次，在函式裡加 `print` 觀察執行順序。你要能回答：

- Step B 裡的 `fetch_page` 是什麼時候被呼叫的？
- 如果呼叫端只取前 10 筆會怎樣？

**學習重點**：`yield` / `yield from`、lazy evaluation、generator 只能走一次（試著對同一個 generator 跑兩次 `for`，看會發生什麼）、`itertools.islice` 的用途。

這個 Module 是整套裡對「看懂 agent code」幫助最大的之一。`yield` 出現時控制流會反轉，不熟的話讀起來會非常混亂。

---

## Module 4：資料模型與型別

**目標**：不要再讓 `dict` 到處流竄。

- 用 `dataclass` 定義 `Order`，欄位加上型別標註
- 寫一個 `from_api(cls, raw: dict) -> "Order"` 的 classmethod
- 全專案的函式簽章補上型別標註
- 裝 `mypy` 跑一次，把錯誤修掉

**驗收**：`mypy src/` 沒有錯誤。以及——刻意在某處把 `order.total` 打成 `order.totl`，確認 mypy 抓得到（`dict["totl"]` 抓不到，這就是重點）。

**學習重點**：`dataclass` 的 `field(default_factory=...)`（為什麼不能直接寫 `= []`，這個坑很經典）、`Optional[X]` 的意義、`TypedDict` 和 `dataclass` 分別適合什麼場景。

**思考題**：raw API response 該用 `TypedDict`，還是也用 `dataclass`？兩者的邊界在哪？

---

## Module 5：錯誤處理與重試 ⭐

**目標**：讓失敗變成可控的。

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

**驗收**：用一個假的 local server（`http.server` 就夠）模擬 429 和 401，確認前者會重試、後者立刻拋出。

**學習重點**：exception 繼承、`raise ... from e` 保留原始 traceback、`finally` 的執行時機、decorator 怎麼改變一個函式的行為。

---

## Module 6：設定與祕密

**目標**：拿掉所有寫死的值。

- 一個 `Config` dataclass，欄位有預設值
- 讀取優先序：CLI 參數 > 環境變數 > `.env` > 預設值
- 用 `python-dotenv` 或 `pydantic-settings`（後者順便學 validation）
- Secret Manager 的讀取包成一個函式，**但要能用環境變數繞過**，這樣本機開發不用連 GCP

**驗收**：同一份 code，切換一個環境變數就能在「本機用 `.env`」和「Cloud Run 用 Secret Manager」之間切換。

**學習重點**：`os.environ` vs `os.getenv` 的差別、為什麼設定要集中在一個地方（提示：跟 Module 0 的 import 副作用是同一個問題）。

---

## Module 7：輸出層與 contextmanager ⭐

**目標**：把資料寫出去，並且讓「寫到哪」是可替換的。

- NDJSON 序列化，注意 `ensure_ascii=False`，以及 `datetime` 不能直接 `json.dumps`（要處理 `default=`）
- 先寫本機檔案，再加 GCS
- 用 `contextlib.contextmanager` 寫一個 writer：

```python
with ndjson_writer(path) as w:
    for order in iter_orders(...):
        w.write(order)
```

- 定義一個 `Writer` 的 `Protocol`，讓 `LocalWriter` 和 `GCSWriter` 都符合

**驗收**：把 `LocalWriter` 換成 `GCSWriter`，主流程一行都不用改。

**學習重點**：`with` 到底做了什麼（`__enter__` / `__exit__`）、`yield` 在 contextmanager 裡的角色（跟 Module 3 是同一個關鍵字、不同用途，這個對照很有價值）、`Protocol` 的鴨子型別 vs 抽象基底類別。

---

## Module 8：增量與時間

**目標**：只抓新資料，而且不會漏。

- 決定 watermark 存哪（GCS 上一個小 json？BQ 一張表？）
- 處理**重疊區間**：為什麼要抓 `last_run - 5min` 而不是剛好 `last_run`
- 時區：Cyberbiz 回的是什麼時區？用 `zoneinfo`，全程存 UTC，只在顯示時轉換
- 冪等：同一區間跑兩次，結果要一樣

**驗收**：連跑兩次同一區間，最終資料筆數不變。以及能說清楚你的 watermark 是「開區間還是閉區間」。

**學習重點**：`datetime` 的 naive vs aware（`tzinfo is None` 的那個）、`zoneinfo.ZoneInfo("Asia/Taipei")`、ISO 8601 的解析。時間是資料工程最常見的 bug 來源，值得單獨花一個 Module。

---

## Module 9：PII 處理

**目標**：敏感欄位分流。

- Hash 前的正規化規則（小寫、去空白、電話統一格式）——這步驟決定了 join 率
- HMAC-SHA256，key 從 Secret Manager 來
- 輸出分成兩份：一般欄位 → `cyberbiz_raw`，含 hashed ID → `cyberbiz_raw_pii`
- 加一個「檢查」：確認一般欄位那份裡真的沒有明文 email / phone

**驗收**：寫一個 script 掃過輸出檔案，用 regex 找 email pattern，應該是零筆。

**學習重點**：`re` 模組、為什麼正規化必須在 hash 之前（雪崩效應——這裡會實際遇到）。

---

## Module 10：logging 與可觀測性

**目標**：把所有 `print` 換掉。

- `logging.getLogger(__name__)` 的慣例，理解 logger 的階層命名
- 在 `main()` 裡做唯一一次 `basicConfig`，函式庫層級絕不設定 handler
- 結構化輸出：Cloud Logging 吃 JSON，一行一個 log entry
- 關鍵指標打進 log：抓了幾筆、花多久、retry 幾次

**驗收**：`LOG_LEVEL=DEBUG` 和 `INFO` 切換，輸出量明顯不同，且 code 不用改。

**學習重點**：logger / handler / formatter 三者的關係、propagate 機制、為什麼 `logging.info()` 直接呼叫是壞習慣。

---

## Module 11：CLI 化

**目標**：從「執行一支檔案」變成「一個工具」。

- `argparse`（先用標準庫，理解原理）或 `typer`
- 支援 `--since`、`--until`、`--dry-run`、`--limit`
- `--dry-run` 特別重要：跑完整流程但不寫任何東西
- 加 `[project.scripts]` entry point，讓 `cbz-extract --since 2026-07-01` 直接可用

**驗收**：`cbz-extract --help` 印出清楚的說明。`--dry-run --limit 5` 能在 10 秒內跑完。

**學習重點**：`if __name__ == "__main__"` 的真正用途、`python -m package` 和 `__main__.py`、entry point 的機制。

---

## Module 12：容器化與部署

**目標**：跑上 Cloud Run Jobs。

- 寫 Dockerfile（multi-stage，把 build 依賴留在第一層）
- 明確用**版本化 tag** 推 Artifact Registry，不要 `:latest`
- 建 Cloud Run Job，設定 Scheduler，記得 `roles/run.invoker`
- 跑一次，確認 log 進得去 Cloud Logging

**驗收**：Scheduler 觸發成功，BQ 裡出現資料。

**學習重點**：這個 Module 你已經很熟，重點不是學新東西，而是驗證「從零寫的 code 能走完全程」。

### 然後——現在才可以打開舊的 `extract.py`

拿新舊兩版並排比較，逐一問自己：

- 哪些地方新版比較好？為什麼？
- 哪些地方舊版有做、新版漏掉？那是我當初沒想到，還是實際不需要？
- 哪些是「agent 當初寫了但我其實不知道在幹嘛」，現在懂了嗎？

這個對照是整個專案價值最高的 30 分鐘。建議寫成一份筆記。

---

## Module 13（選配）：併發

**目標**：搞懂 Python 併發的取捨。

- 先量測：現在的瓶頸是網路等待（I/O bound），還是 CPU？用 `time.perf_counter` 量
- `ThreadPoolExecutor` 版本，觀察加速比
- `asyncio` + `httpx` 版本
- 理解 GIL 為什麼不影響 I/O bound，以及 rate limit 才是真正的天花板

**驗收**：能說清楚「為什麼我的 pipeline 用 thread 就夠，不需要 async」——或反過來。

**學習重點**：GIL、`async`/`await` 的傳染性（一個 async 函式會逼上層全部 async）、`asyncio.Semaphore` 控制併發數。

---

## 節奏建議

| 階段 | Module | 大約 |
|---|---|---|
| 打底 | 0–2 | 一個週末 |
| 核心語言特性 | 3–5 | 最花時間，值得慢 |
| 工程結構 | 6–8 | 中等 |
| 收尾 | 9–12 | 較快，多是熟悉的領域 |

標 ⭐ 的三個 Module（3、5、7）是關鍵節點：generator、decorator/exception、context manager。這三個吃透了，agent 產出的 Python 大概八成都讀得動。

如果時間有限，寧可在這三個 Module 多待幾天，也不要為了跑完進度趕過去。

---

## 進度追蹤

每個 Module 完成後，更新 `PROGRESS.md`：

- 做到哪
- 卡在哪
- 學到什麼觀念

對話會斷、context 會被壓縮，但檔案不會。`PROGRESS.md` 才是真正的專案記錄。
