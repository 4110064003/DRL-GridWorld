from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

def policy_evaluation(grid_size, start, end, obstacles, policy, gamma=0.9, threshold=1e-4):
    V = np.zeros((grid_size, grid_size))
    actions_map = {'↑': (-1, 0), '↓': (1, 0), '←': (0, -1), '→': (0, 1)}

    while True:
        delta = 0
        new_V = np.copy(V)
        for r in range(grid_size):
            for c in range(grid_size):
                # 終點與障礙物格子本身不更新價值
                if [r, c] == end or [r, c] in obstacles:
                    continue

                action_char = policy[r][c]
                dr, dc = actions_map.get(action_char, (0, 0))
                nr, nc = r + dr, c + dc
                
                # 1. 檢查是否撞牆或撞障礙物
                is_out_of_bounds = not (0 <= nr < grid_size and 0 <= nc < grid_size)
                is_hit_obstacle = [nr, nc] in obstacles if not is_out_of_bounds else False
                
                if is_out_of_bounds or is_hit_obstacle:
                    # 碰到障礙物或邊界，留在原地並扣 5 分
                    target_r, target_c = r, c
                    reward = -5.0
                elif [nr, nc] == end:
                    # 成功抵達終點，加 10 分
                    target_r, target_c = nr, nc
                    reward = 10.0
                else:
                    # 一般移動，扣 1 分
                    target_r, target_c = nr, nc
                    reward = -1.0
                
                # 貝爾曼等式計算
                v_new = reward + gamma * V[target_r, target_c]
                new_V[r, c] = v_new
                delta = max(delta, abs(v_new - V[r, c]))
        
        V = new_V
        if delta < threshold:
            break
            
    return V.tolist()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    # 接收前端傳來的隨機固定策略進行評估
    v_matrix = policy_evaluation(
        data['n'], data['start'], data['end'], data['obstacles'], data['policy']
    )
    return jsonify({'v_matrix': v_matrix})

if __name__ == '__main__':
    app.run(debug=True, port=5000)