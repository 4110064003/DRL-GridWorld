from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__, template_folder='templates')


def value_iteration(grid_size, start, end, obstacles, gamma=0.9, threshold=1e-4):
    """
    價值迭代 (Value Iteration) 求最佳路徑。
    獎勵機制：
      1. 成功抵達終點: +10
      2. 碰到障礙物或邊界 (留在原地): -5
      3. 一般移動: -1
      4. 終點與障礙物價值不更新 (固定為 0)
    """
    V = np.zeros((grid_size, grid_size))
    actions_map = {'↑': (-1, 0), '↓': (1, 0), '←': (0, -1), '→': (0, 1)}

    # 價值迭代主迴圈
    while True:
        delta = 0
        new_V = np.copy(V)
        for r in range(grid_size):
            for c in range(grid_size):
                # 終點與障礙物格子本身不更新價值
                if [r, c] == end or [r, c] in obstacles:
                    continue

                v_list = []
                for a_char, (dr, dc) in actions_map.items():
                    nr, nc = r + dr, c + dc

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

                    v_list.append(reward + gamma * V[target_r, target_c])

                max_v = max(v_list)
                new_V[r, c] = max_v
                delta = max(delta, abs(max_v - V[r, c]))

        V = new_V
        if delta < threshold:
            break

    # 根據最終價值函數推導最佳策略
    best_policy = [['' for _ in range(grid_size)] for _ in range(grid_size)]
    for r in range(grid_size):
        for c in range(grid_size):
            if [r, c] == end:
                best_policy[r][c] = 'G'  # Goal
                continue
            if [r, c] in obstacles:
                best_policy[r][c] = 'X'  # Obstacle
                continue

            best_val = -float('inf')
            best_act = '↑'
            for a_char, (dr, dc) in actions_map.items():
                nr, nc = r + dr, c + dc

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


def policy_evaluation(grid_size, start, end, obstacles, policy, gamma=0.9, threshold=1e-4):
    """策略評估 (Policy Evaluation) 計算固定策略的價值函數。"""
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

                is_out_of_bounds = not (0 <= nr < grid_size and 0 <= nc < grid_size)
                is_hit_obstacle = [nr, nc] in obstacles if not is_out_of_bounds else False

                if is_out_of_bounds or is_hit_obstacle:
                    target_r, target_c = r, c
                    reward = -5.0
                elif [nr, nc] == end:
                    target_r, target_c = nr, nc
                    reward = 10.0
                else:
                    target_r, target_c = nr, nc
                    reward = -1.0

                v_new = reward + gamma * V[target_r, target_c]
                new_V[r, c] = v_new
                delta = max(delta, abs(v_new - V[r, c]))

        V = new_V
        if delta < threshold:
            break

    return V.tolist()


@app.route('/')
def index():
    return render_template('index_final.html')


@app.route('/calculate_value_iteration', methods=['POST'])
def calculate_value_iteration():
    data = request.json
    v_matrix, best_policy = value_iteration(
        data['n'], data['start'], data['end'], data['obstacles']
    )
    return jsonify({'v_matrix': v_matrix, 'policy': best_policy})


@app.route('/calculate_policy_evaluation', methods=['POST'])
def calculate_policy_evaluation():
    data = request.json
    v_matrix = policy_evaluation(
        data['n'], data['start'], data['end'], data['obstacles'], data['policy']
    )
    return jsonify({'v_matrix': v_matrix})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
