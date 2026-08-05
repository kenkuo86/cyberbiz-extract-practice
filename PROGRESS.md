# 進度

## 目前：Module 3（分頁與 generator）⭐

CURRICULUM 標記的三個關鍵節點之一（3 generator / 5 decorator+exception / 7 context manager）。

- ✅ **Step A（list 版本）通過**：`fetch_page(session, page_num)` 抓單頁、`fetch_all_orders()` 用 `while True` 翻完所有頁並**回傳完整 list**，實跑 3366 筆。
- ⬜ **Step B（generator 版本）**：還沒開始。

Step B 要做的事：
1. 用 `yield` / `yield from` 改寫，讓呼叫端一筆一筆拿到訂單
2. print 要放**三個地方**才看得出東西：`fetch_page` 裡、generator 的迴圈裡、**呼叫端的 for 迴圈裡**（第三個最關鍵，要看的是三種 print **交錯的順序**）
3. 實驗一：呼叫端只取前 10 筆就 `break`，看 `fetch_page` 被呼叫幾次
4. 實驗二：對**同一個** generator 物件跑兩次 `for`，看第二次發生什麼

**Module 3 的驗收條件**（CURRICULUM 原文）：兩個版本都跑一次，在函式裡加 `print` 觀察執行順序，並回答——
- Step B 裡的 `fetch_page` 是什麼時候被呼叫的？
- 如果呼叫端只取前 10 筆會怎樣？

⚠️ CURRICULUM 給的 Step B 骨架寫 `data["orders"]`，但 Cyberbiz 實際回傳的是**裸 list**，照抄會爆。

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
- **為什麼含 query 和不含 query 的 request-line 兩種簽法都能通過？** 目前最合理的解釋是「伺服器不只用一種形式比對」，但這是推論不是實證。詳見 LEARNINGS.md「Cyberbiz 簽章實際涵蓋的範圍」。
- **`/v1/orders` 的資料排序方向、以及 `offset` 實際怎麼運作**（Module 3 刻意跳過，因為只用 `page` + `per_page` 不受影響）。實測數據留在 LEARNINGS.md「分頁參數的實測結果」，之後要查再回去看。
- **分頁期間如果有新訂單插入怎麼辦？** 排序若是「新的在前」，抓第 1 頁時進來一張新訂單，會把所有資料往後推一格，導致**漏抓或重複抓，而且不會報錯**。這是所有 page/offset 分頁的通病，不是 Cyberbiz 的問題。Module 8 的「重疊區間」就是在解這個。
- **文件寫的「每個請求上限 2 MB（apidemo 為 2 KB）」到底指什麼？** 不可能是 response 大小——實測 `per_page=50` 拿得到完整 50 筆訂單，遠超過 2 KB。