import json
import os
import requests
import google.generativeai as genai

# 获取 GitHub 密钥配置
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
XHS_API_KEY = os.environ.get("XHS_API_KEY") 

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro') 

# 目标博主 ID 与数据文件
TARGET_BLOGGERS = ["69a5292900000000210079b7"] 
MENU_FILE = "menu_data.json"

def is_duplicate_name(new_name, existing_names):
    """查重核心算法：连续 4 个字相同即判定为重复"""
    clean_new = new_name.replace("减脂", "").replace("版", "")
    for old_name in existing_names:
        clean_old = old_name.replace("减脂", "").replace("版", "")
        if len(clean_new) < 4:
            if clean_new in clean_old or clean_old in clean_new:
                return True
        else:
            for i in range(len(clean_new) - 3):
                if clean_new[i:i+4] in clean_old:
                    return True
    return False

def fetch_xhs_notes(blogger_id):
    """
    通过第三方 API 获取小红书笔记
    注意：购买第三方 API 后，请将这里的 url 替换为服务商提供的真实地址
    """
    # 示例 API 调用逻辑
    api_url = f"https://api.thirdparty.com/xhs/notes" # 替换为真实 API 域名
    params = {
        "user_id": blogger_id,
        "apikey": XHS_API_KEY,
        "limit": 5 # 提取最近 5 篇
    }
    
    print(f"正在获取博主 {blogger_id} 的近期更新...")
    try:
        response = requests.get(api_url, params=params, timeout=30)
        if response.status_code == 200:
            # 这里的具体字段名（如 'data'）请根据你购买的 API 文档进行微调
            return response.json().get("data", [])
        return []
    except Exception as e:
        print(f"获取笔记失败: {e}")
        return []

def extract_recipe_with_gemini(note_data):
    """调用 Gemini 分析图文并输出规范化的 JSON 菜单"""
    prompt = """
    你是一个专业的营养师。请分析这篇小红书减脂餐笔记内容，提取出符合以下 4 个类别的食材组合，并严格以 JSON 格式输出，不要输出任何多余的解释文字。
    
    需要严格遵循的 JSON 字段：
    - tag: 菜系或风格（如"中式家常"）
    - carbs: 包含2个字符串的数组，提取优质碳水（如 ["糙米饭 🍚", "红薯 🍠"]）
    - dish_1: 包含2个字符串的数组，提取主菜/高蛋白肉类（如 ["清蒸鱼 🐟", "炒鸡胸 🍗"]）
    - dish_2: 包含2个字符串的数组，提取副菜/蔬菜类
    - dish_3: 包含2个字符串的数组，提取额外补充/水果饮品
    
    笔记内容：
    {text}
    """
    
    text_content = note_data.get("title", "") + "\n" + note_data.get("desc", "")
    if not text_content.strip():
        return None
        
    try:
        response = model.generate_content(prompt.format(text=text_content))
        result_str = response.text.strip().removeprefix("```json").removesuffix("```")
        return json.loads(result_str)
    except Exception as e:
        print(f"解析内容格式异常，跳过此条: {e}")
        return None

def main():
    print("🚀 开始执行减脂餐更新流水线...")
    
    if os.path.exists(MENU_FILE) and os.path.getsize(MENU_FILE) > 0:
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            menu_data = json.load(f)
    else:
        menu_data = []

    existing_dishes = []
    for day in menu_data:
        existing_dishes.extend(day.get("dish_1", []))
        existing_dishes.extend(day.get("dish_2", []))

    new_recipes_added = 0

    for blogger_id in TARGET_BLOGGERS:
        recent_notes = fetch_xhs_notes(blogger_id)
        
        for note in recent_notes:
            recipe_json = extract_recipe_with_gemini(note)
            
            if recipe_json:
                all_new_dishes = recipe_json.get("dish_1", []) + recipe_json.get("dish_2", [])
                is_duplicate = any(is_duplicate_name(dish, existing_dishes) for dish in all_new_dishes)
                
                if not is_duplicate:
                    recipe_json["day"] = len(menu_data) + 1
                    menu_data.append(recipe_json)
                    existing_dishes.extend(all_new_dishes)
                    new_recipes_added += 1
                    print(f"✅ 成功录入新菜谱：{recipe_json.get('tag')}")
                else:
                    print("❌ 触发去重机制，菜品已存在")

    if new_recipes_added > 0:
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(menu_data, f, ensure_ascii=False, indent=4)
        print(f"🎉 任务完成！数据库成功追加 {new_recipes_added} 个新食谱组合。")
    else:
        print("🤷 本周暂无符合条件的新食谱更新。")

if __name__ == "__main__":
    main()
