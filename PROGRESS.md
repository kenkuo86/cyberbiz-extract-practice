# 進度

## 目前：Module 1

## 已完成
- Module 0：建立 venv、src layout 專案結構、pyproject.toml（`[build-system]` 用 hatchling）、`pip install -e .` 成功、確認同一個 venv 下任何目錄都能 import

## 卡住的地方
（尚無，Module 0 遇到的卡點都已解決，整理進下方觀念）

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