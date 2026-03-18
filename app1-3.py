from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

def value_iteration(grid_size, start, end, obstacles, gamma=0.9, threshold=1e-4):
    """
    執行價值迭代 (Value Iteration) 以找到最佳路徑。
    獎勵機制修正：
    1. 成功抵達終點: +10
    2. 碰到障礙物或邊界 (留在原地): -5
    3. 一般移動: -1
    4. 終點與障礙物價值不更新 (固定為 0)
    """
    V = np.zeros((grid_size, grid_size))
    actions_map = {'↑': (-1, 0), '↓': (1, 0), '←': (0, -1), '→': (0, 1)}
    
    # --- 1. 價值迭代主迴圈 ---
    while True:
        delta = 0
        new_V = np.copy(V)
        for r in range(grid_size):
            for c in range(grid_size):
                # 根據要求：終點與障礙物格子本身不更新價值
                if [r, c] == end or [r, c] in obstacles:
                    continue

                v_list = []
                for a_char, (dr, dc) in actions_map.items():
                    nr, nc = r + dr, c + dc
                    
                    # 判定下一個狀態與對應獎勵
                    # 情況 A: 撞牆或撞到障礙物
                    if not (0 <= nr < grid_size and 0 <= nc < grid_size) or [nr, nc] in obstacles:
                        target_r, target_c = r, c
                        reward = -5.0
                    # 情況 B: 成功移向終點
                    elif [nr, nc] == end:
                        target_r, target_c = nr, nc
                        reward = 10.0
                    # 情況 C: 一般合法移動
                    else:
                        target_r, target_c = nr, nc
                        reward = -1.0
                    
                    # Bellman 方程更新：Q(s,a) = R + γ * V(s')
                    v_list.append(reward + gamma * V[target_r, target_c])
                
                # 更新該狀態的最大價值
                max_v = max(v_list)
                new_V[r, c] = max_v
                delta = max(delta, abs(max_v - V[r, c]))
        
        V = new_V
        # 當價值函數變動極小時停止迭代
        if delta < threshold:
            break

    # --- 2. 根據最終價值函數推導最佳策略 ---
    best_policy = [['' for _ in range(grid_size)] for _ in range(grid_size)]
    for r in range(grid_size):
        for c in range(grid_size):
            if [r, c] == end:
                best_policy[r][c] = 'G' # Goal
                continue
            if [r, c] in obstacles:
                best_policy[r][c] = 'X' # Obstacle
                continue
            
            best_val = -float('inf')
            best_act = '↑'
            for a_char, (dr, dc) in actions_map.items():
                nr, nc = r + dr, c + dc
                
                # 策略推導的邏輯必須與訓練時完全一致
                if not (0 <= nr < grid_size and 0 <= nc < grid_size) or [nr, nc] in obstacles:
                    target_r, target_c = r, c
                    reward = -5.0
                elif [nr, nc] == end:
                    target_r, target_c = nr, nc
                    reward = 10.0
                else:
                    target_r, target_c = nr, nc
                    reward = -1.0
                
                q_value = reward + gamma * V[target_r, target_c]
                if q_value > best_val:
                    best_val = q_value
                    best_act = a_char
            
            best_policy[r][c] = best_act

    return V.tolist(), best_policy

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    v_matrix, best_policy = value_iteration(
        data['n'], data['start'], data['end'], data['obstacles']
    )
    return jsonify({'v_matrix': v_matrix, 'policy': best_policy})

if __name__ == '__main__':
    # 啟動 Flask 伺服器
    app.run(debug=True, port=5000)