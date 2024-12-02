import sqlite3
import requests
from flask import Flask, render_template, request

# 初始化 Flask 应用
app = Flask(__name__)

# 设置 API 配置信息
API_URL = "https://api.x.ai/v1/chat/completions"
API_KEY = "xai-U0NqCaMqoZzokJaqtQDY5MyC9R6NfjtlGdjjfE4xmbyaUL9Y35YbF3GFO5DC5to3DP1xp2uFE9RtHlrQ"

# 函数：调用外部 API 解析用户需求
def parse_user_input(user_input):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "messages": [
            {"role": "system", "content": "You are a smart assistant helping users find laptops."},
            {"role": "user", "content": user_input}
        ],
        "model": "grok-beta",
        "stream": False,
        "temperature": 0
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return "Error"

# 首页路由：显示输入表单
@app.route('/')
def home():
    return render_template('index.html')

# 推荐路由：处理用户输入并返回推荐结果
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # 获取用户输入
        description = request.form.get('description')
        budget = request.form.get('budget')

        # 调用外部 API 解析用户输入
        profession = parse_user_input(description)
        print(f"Parsed profession: {profession}")

        # 连接 SQLite 数据库
        conn = sqlite3.connect('laptop_recommendations_2.db')
        cursor = conn.cursor()

        # 查询符合用户需求和预算的笔记本
        query = '''
        SELECT model, price, gpu, ram, weight, link, tags
        FROM laptops
        WHERE CAST(price AS INTEGER) <= ? AND tags LIKE ?
        ORDER BY price ASC
        '''
        cursor.execute(query, (budget, f"%{profession}%"))
        results = cursor.fetchall()

        conn.close()

        # 构造推荐结果
        recommendations = []
        for row in results:
            recommendations.append({
                'model': row[0],
                'price': row[1],
                'gpu': row[2],
                'ram': row[3],
                'weight': row[4],
                'link': row[5],
                'tags': row[6],
            })

        return render_template('result.html', profession=profession, budget=budget, recommendations=recommendations)

    except Exception as e:
        print(f"Error in recommend route: {e}")
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
