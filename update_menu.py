import json
import os
import requests
import google.generativeai as genai

# --- 环境配置 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
XHS_API_KEY = os.environ.get("XHS_API_KEY") 

genai.configure(api_key=GEMINI_API_KEY)
# 使用 1.5 Pro 处理复杂图文和结构化输出能力最强
model = genai.GenerativeModel('gemini-1.5-pro') 

# 配置关注的博主和数据文件路径
TARGET_BLOGGERS = ["此处填写小红书博主ID_1", "此处填写小红书博主ID_2"] 
MENU_FILE = "menu_data.json"

def is_duplicate_name(new_name, existing_names):
    """查重：连续4个字相同则视为重复"""
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
    通过第三方 API 获取小红书笔记（此处需替换为你购买/申请的实际第三方接口地址）
    """
    # 示例 API 请求结构
    # url = f"https://api.thirdparty.com/xhs/user/notes?user_id={blogger_id}&apikey={XHS_API_KEY}"
    # response = requests.get(url).json()
    # return response.get("data", [])
    print(f"正在模拟获取博主 {blogger_id} 的近期更新...")
    return [] 

def extract_recipe_with_gemini(note_data):
    """调用 Gemini API 分析图文并强制输出 JSON"""
    prompt = """
    你是一个专业的营养师。请分析这篇小红书减脂餐笔记内容，提取出符合以下 4 个类别的食材组合，并严格以 JSON 格式输出，不要输出任何其他多余的解释文字。
    
    需要的 JSON 字段：
    - tag: 菜系或风格（如"中式家常"）
    - carbs: 包含2个字符串的数组，提取优质碳水（如 ["糙米饭 🍚", "红薯 🍠"]）
    - dish_1: 包含2个字符串的数组，提取主菜/高蛋白肉类（如 ["清蒸鱼 🐟", "炒鸡胸 🍗"]）
    - dish_2: 包含2个字符串的数组，提取副菜/蔬菜类
    - dish_3: 包含2个字符串的数组，提取额外补充/水果饮品
    
    笔记内容：
    {text}
    """
    
    # 提取笔记标题和正文 (如果有图片URL，也可以作为多模态输入传给Gemini)
    text_content = note_data.get("title", "") + "\n" + note_data.get("content", "")
    
    try:
        response = model.generate_content(prompt.format(text=text_content))
        result_str = response.text.strip().removeprefix("```json").removesuffix("```")
        return json.loads(result_str)
    except Exception as e:
        print(f"Gemini 提取失败/格式错误: {e}")
        return None

def main():
    print("🚀 开始执行减脂餐更新流水线...")
    
    # 1. 加载本地数据库
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            menu_data = json.load(f)
    else:
        menu_data = []

    existing_dishes = []
    for day in menu_data:
        existing_dishes.extend(day.get("dish_1", []))
        existing_dishes.extend(day.get("dish_2", []))

    new_recipes_added = 0

    # 2. 抓取与分析
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
                    print("❌ 触发去重机制，跳过该食谱")

    # 3. 保存更新
    if new_recipes_added > 0:
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(menu_data, f, ensure_ascii=False, indent=4)
        print(f"🎉 任务完成！数据库成功追加 {new_recipes_added} 个新食谱组合。")
    else:
        print("🤷 本周没有符合条件的新食谱更新。")

if __name__ == "__main__":
    main()
