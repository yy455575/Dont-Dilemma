import json
import os
import sys
import time
import requests
import google.generativeai as genai

# --- 将拉取下来的 Spider_XHS 加入系统路径，以便直接调用其方法 ---
sys.path.append(os.path.join(os.getcwd(), "Spider_XHS"))
try:
    # 尝试导入 Spider_XHS 的请求工具 (根据其实际项目结构进行桥接)
    # 注意：若后续项目结构变更，此处导入路径需同步调整
    from xhs_utils.xhs_req import XhsReq
except ImportError:
    print("⚠️ 无法导入 Spider_XHS 核心模块，请检查代码拉取状态。")

# --- 环境配置 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
XHS_COOKIE = os.environ.get("XHS_COOKIE") 

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro') 

TARGET_BLOGGERS = ["69a5292900000000210079b7"] 
MENU_FILE = "menu_data.json"

def is_duplicate_name(new_name, existing_names):
    """4字查重算法"""
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

def fetch_xhs_notes_with_spider(blogger_id):
    """
    使用 cv-cat/Spider_XHS 引擎获取数据
    """
    if not XHS_COOKIE:
        print("❌ 未检测到 XHS_COOKIE 环境变量，退出抓取。")
        return []
        
    print(f"🕸️ 启动 Spider_XHS 引擎，正在分析博主 {blogger_id} 的主页...")
    
    # 初始化爬虫请求类 (此处为拟合 Spider_XHS 的通用调用逻辑)
    # 具体参数 x-s 会由其内部的 node 脚本自动计算
    req = XhsReq(cookie=XHS_COOKIE)
    
    api_url = f"https://edith.xiaohongshu.com/api/sns/web/v1/user_posted"
    params = {
        "num": 10,
        "cursor": "",
        "user_id": blogger_id,
        "image_formats": "jpg,webp,avif"
    }
    
    try:
        # Spider_XHS 封装的请求方法会自动处理签名
        res = req.get(api_url, params=params)
        data = res.json()
        
        if data.get("success"):
            notes = data["data"]["notes"]
            # 必须增加强制休眠，防止 GitHub Actions IP 被小红书拉黑
            print("⏳ 为防止触发风控，休眠 5 秒...")
            time.sleep(5) 
            return notes
        else:
            print(f"❌ 抓取失败，可能是 Cookie 失效或 IP 被封: {data}")
            return []
    except Exception as e:
        print(f"Spider_XHS 引擎运行异常: {e}")
        return []

def extract_recipe_with_gemini(note_data):
    """大模型图文转化引擎"""
    prompt = """
    你是一个专业的营养师。请分析这篇小红书减脂餐笔记内容，提取出符合以下 4 个类别的食材组合，并严格以 JSON 格式输出，不要输出任何多余的解释文字。
    
    需要的 JSON 字段：
    - tag: 菜系或风格（如"中式家常"）
    - carbs: 包含2个字符串的数组，提取优质碳水
    - dish_1: 包含2个字符串的数组，提取主菜/高蛋白肉类
    - dish_2: 包含2个字符串的数组，提取副菜/蔬菜类
    - dish_3: 包含2个字符串的数组，提取额外补充/水果饮品
    
    笔记内容：
    {text}
    """
    
    # 小红书原生的数据结构中提取标题和描述
    title = note_data.get("display_title", "")
    desc = note_data.get("desc", "")
    text_content = f"【标题】: {title}\n【正文】: {desc}"
    
    if not text_content.strip():
        return None
        
    try:
        response = model.generate_content(prompt.format(text=text_content))
        result_str = response.text.strip().removeprefix("```json").removesuffix("```")
        return json.loads(result_str)
    except Exception as e:
        print(f"Gemini 提取失败/格式错误: {e}")
        return None

def main():
    print("🚀 开始执行减脂餐更新流水线...")
    
    if os.path.exists(MENU_FILE) and os.path.getsize(MENU_FILE) > 0:
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            menu_data = json.load(f)
    else:
        menu_data = []

    existing_dishes = [dish for day in menu_data for dish in day.get("dish_1", []) + day.get("dish_2", [])]
    new_recipes_added = 0

    for blogger_id in TARGET_BLOGGERS:
        recent_notes = fetch_xhs_notes_with_spider(blogger_id)
        
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
                    print(f"❌ 触发去重机制，跳过内容: {note.get('display_title')}")

    if new_recipes_added > 0:
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(menu_data, f, ensure_ascii=False, indent=4)
        print(f"🎉 任务完成！成功利用 Spider_XHS 追加 {new_recipes_added} 个新食谱。")
    else:
        print("🤷 本周暂无符合条件的新食谱更新。")

if __name__ == "__main__":
    main()
