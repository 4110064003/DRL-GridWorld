# Grid World DRL Demos

本專案示範在離散網格環境中的兩種動態規劃 / 強化學習相關演算法：

- **HW1-2 – Fixed Policy Evaluation**：給定一個隨機固定策略，利用 Bellman 方程計算每個狀態的價值函數。
- **HW1-3 – Optimal Path Finding (Value Iteration)**：透過價值迭代 (Value Iteration) 計算最適價值函數與對應的最優策略，尋找從起點到終點的最佳路徑。

整合後的版本使用 `app_final.py` 與 `templates/index_final.html`，在**同一個網頁**中左右並排呈現兩個作業的互動介面。

---

## 專案結構

- `app1-3.py`：原本 HW1-3（Value Iteration）後端 Flask 程式。
- `templates/index1-3.html`：原本 HW1-3 前端單一頁面。
- `../HW1-2/templates/app1-2.py`：原本 HW1-2（Policy Evaluation）後端 Flask 程式。
- `templates/index1-2.html`：原本 HW1-2 前端單一頁面。
- `app_final.py`：整合後的 Flask 後端，同時提供 HW1-2 與 HW1-3 的 API。
- `templates/index_final.html`：整合後的前端頁面，左右各一個區塊呈現兩個作業。

> 注意：原本的 app 與 HTML 檔案都保留，方便對照與測試；實際 demo 建議使用 `app_final.py` + `index_final.html`。

---

## 環境需求

- Python 3.x
- 已安裝套件：
  - `flask`
  - `numpy`

若尚未安裝，可使用：

```bash
pip install flask numpy
```

---

## 執行方式

1. 進入 GridWorld 資料夾：

   ```bash
   cd GridWorld
   ```

2. 啟動整合後的 Flask 伺服器：

   ```bash
   python app_final.py
   ```

3. 在瀏覽器開啟：

   - http://127.0.0.1:5000/

你會看到一個頁面，左邊是 HW1-2：Fixed Policy Evaluation，右邊是 HW1-3：Optimal Path Finding (Value Iteration)。

---

## 介面說明（index_final.html）

### 左側：HW1-2 Grid World : Fixed Policy Evaluation

- 標題：`HW1-2 Grid World : Fixed Policy Evaluation`
- 功能：
  - 使用者設定：
    - Grid 大小 `n`（5–9）
    - START 位置
    - END 位置
    - `n-2` 個障礙物 (Obstacles)
  - 系統在每個非終點、非障礙物格子上隨機給一個方向（↑ ↓ ← →），作為**固定策略**。
  - 點擊 **Evaluate Policy & Animate**：
    - 前端送出 `POST /calculate_policy_evaluation`，呼叫 `policy_evaluation()`。
    - 後端依照獎勵機制與 Bellman 等式反覆更新 V(s)，直到收斂。
    - 前端在每個格子顯示 `V(s)` 值，並依固定策略進行動畫：
      - 撞牆或撞到障礙物時，動畫停止並顯示路徑被阻擋。

- 獎勵設計：
  - 成功抵達終點：+10
  - 碰到障礙物或邊界、留在原地：-5
  - 一般合法移動：-1
  - 終點與障礙物的狀態價值不更新（視為固定）。

### 右側：HW1-3 Grid World: Optimal Path Finding (Value Iteration)

- 標題：`HW1-3 Grid World: Optimal Path Finding (Value Iteration)`
- 功能：
  - 使用者設定：
    - Grid 大小 `n`（5–9）
    - START 位置
    - END 位置
    - `n-2` 個障礙物
  - 點擊 **Find Path & Animate**：
    - 前端送出 `POST /calculate_value_iteration`，呼叫 `value_iteration()`。
    - 後端對每個非終點、非障礙物的格子，對所有可能動作（↑ ↓ ← →）計算：
      - `Q(s, a) = R(s, a) + γ * V(s')`
      - 取最大值更新 V(s)，迭代直到收斂。
    - 再根據最終 V 推導最佳策略 π*(s)。
    - 前端以箭頭顯示最優策略方向，並顯示各格子的價值。
    - 動畫從 START 照著最優策略移動，直到到達 END 或步數超過上限。

- 獎勵設計同上：+10 / -5 / -1，終點與障礙物不更新價值。

---

## 後端 API（app_final.py）

- `GET /`
  - 作用：回傳整合後的頁面 `index_final.html`。

- `POST /calculate_value_iteration`
  - 用於 HW1-3。
  - Request JSON：
    - `n`: grid 大小 (int)
    - `start`: `[row, col]`
    - `end`: `[row, col]`
    - `obstacles`: `[[r1, c1], [r2, c2], ...]`
  - Response JSON：
    - `v_matrix`: 最終狀態價值函數 V(s)
    - `policy`: 對應每一格的最佳動作（↑ ↓ ← →、G、X）

- `POST /calculate_policy_evaluation`
  - 用於 HW1-2。
  - Request JSON：
    - `n`: grid 大小 (int)
    - `start`: `[row, col]`
    - `end`: `[row, col]`
    - `obstacles`: `[[r1, c1], [r2, c2], ...]`
    - `policy`: 大小為 n×n 的方向字元陣列（↑ ↓ ← →）
  - Response JSON：
    - `v_matrix`: 固定策略下的狀態價值函數 V(s)

---

## 備註

- `app1-3.py` + `templates/index1-3.html` 和 `app1-2.py` + `templates/index1-2.html` 仍可作為獨立版本使用或比對。
- 若要只跑其中一個作業，也可以直接使用原始 app 檔案自行調整 route / template 名稱。
- 整合版已將前端變數與元素 id 區分為 `*_vi` 與 `*_pe`，兩側互不干擾，可同時操作觀察差異。