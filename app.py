from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Spoonacular API 密钥（）
SPOONACULAR_API_KEY = "94ebf2701fbe442da18dcd4857d9a308"

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/get_recipes', methods=['POST'])
def get_recipes():
    """处理获取菜谱的 POST 请求"""
    # 获取用户输入的食材，并清理格式
    ingredients = request.form.get('ingredients', '').strip().replace('，', ',')  # 替换中文逗号为英文逗号
    if not ingredients:
        return jsonify({"error": "请输入至少一种食材"}), 400

    processed_recipes = []  # 初始化空列表

    # 调用 Spoonacular API 获取菜谱
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ingredients,
        "number": 5,  # 返回的菜谱数量
        "ranking": 1,
        "apiKey": SPOONACULAR_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        print("API 请求状态码:", response.status_code)
        print("API 返回数据:", response.text)

        if response.status_code != 200:
            return jsonify({"error": "无法获取菜谱数据"}), 500

        recipes = response.json()
        print("API 返回的菜谱:", recipes)

        # 处理每个菜谱，提取所需字段
        for recipe in recipes:
            recipe_id = recipe.get("id")
            steps = []

            # 调用 API 获取该菜谱的详细步骤
            if recipe_id:
                instructions_url = f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions"
                instructions_response = requests.get(instructions_url, params={"apiKey": SPOONACULAR_API_KEY})
                if instructions_response.status_code == 200:
                    instructions = instructions_response.json()
                    for instruction in instructions:
                        for step in instruction.get("steps", []):
                            steps.append(step.get("step"))

            # 将菜谱信息添加到列表中
            processed_recipes.append({
                "title": recipe.get("title"),
                "image": recipe.get("image"),
                "usedIngredients": [i["name"] for i in recipe.get("usedIngredients", [])],
                "missedIngredients": [i["name"] for i in recipe.get("missedIngredients", [])],
                "steps": steps
            })

        # 如果没有找到相关菜谱，返回提示信息
        if not processed_recipes:
            return jsonify({"message": "未找到相关菜谱，请尝试使用其他食材"}), 200

        print("处理后的菜谱数据:", processed_recipes)
        return jsonify(processed_recipes)

    except Exception as e:
        print("发生错误:", str(e))
        return jsonify({"error": "服务器内部错误，请稍后重试"}), 500

if __name__ == '__main__':
    app.run(debug=True)