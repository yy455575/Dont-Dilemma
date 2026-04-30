import json
import os
import sys
import time
import requests
import inspect
from zhipuai import ZhipuAI

# --- 环境初始化 ---
sys.path.append(os.path.join(os.getcwd(), "Spider_XHS"))

ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY")
XHS_COOKIE = os.environ.get("XHS_COOKIE") 

if not ZHIPU_API_KEY:
    print("⚠️ 警告: 未检测到 ZHIPU_API_KEY 环境变量！")
client = ZhipuAI(api_key=ZHIPU_API_KEY)

# 目标博主列表
TARGET_BLOGGERS = [
    "69a5292900000000210079b7",
    "5bf511b0576d7b0001dd4373", 
    "66fa9e53000000001d02293c"
] 
MENU_FILE = "menu_data.json"

def is_duplicate_name(new_name, existing_names):
    """
    优化后的去重算法：
    1. 剔除常用干扰词
    2. 只有连续 6 个及以上的字完全相同才视为重复（超过5个字）
    3. 短菜名采取严格匹配模式
    """
    # 预处理：去掉干扰词并转为纯净字符
    noise_words = ["减脂", "版", "做法", "教程", "自制", "低脂", "低卡"]
    clean_new = new_name
    for word in noise_words:
        clean_new = clean_new.replace(word, "")
    clean_new = clean_new.strip()

    for old_name in existing_names:
        clean_old = old_name
        for word in noise_words:
            clean_old = clean_old.replace(word, "")
        clean_old = clean_old.strip()

        # 场景 A：新菜名很短（不足6字），只有完全一样才算重复
        if len(clean_new) < 6:
            if clean_new == clean_old:
                return True
        # 场景 B：新菜名较长，检查是否有连续 6 个字的重合
        else:
            for i in range(len(clean_new) - 5):
                overlap_segment = clean_new[i:i+6]
                if overlap_segment in clean_old:
                    return True
    return False

def fetch_xhs_notes_with_spider(blogger_id):
    if not XHS_COOKIE:
        print("❌ 未检测到 XHS_COOKIE 环境变量，退出抓取。")
        return []
        
    print(f"🕸️ 启动 Spider_XHS 引擎，正在分析博主 {blogger_id} 的主页...")
    
    original_cwd = os.getcwd()
    spider_path = os.path.join(original_cwd, "Spider_XHS")
    
    try:
        os.chdir(spider_path)
        from apis.xhs_pc_apis import XHS_Apis
        pc_api = XHS_Apis()

        target_methods = ['get_user_all_notes', 'get_user_notes', 'get_user_posted_notes']
        method_to_call = None
        for m in target_methods:
            if hasattr(pc_api, m):
                method_to_call = getattr(pc_api, m)
                print(f"✅ 成功匹配到底层抓取方法: {m}")
                break
                
        if not method_to_call:
            return []

        sig = inspect.signature(method_to_call)
        all_notes = []
        current_cursor = ""  
        max_pages = 3        

        for page in range(max_pages):
            print(f"📄 正在抓取第 {page + 1} 页数据...")
            try:
                if 'cursor' in sig.parameters:
                    success, msg, data = method_to_call(user_id=blogger_id, cursor=current_cursor, cookies_str=XHS_COOKIE)
                elif 'user_id' in sig.parameters:
                    success, msg, data = method_to_call(user_id=blogger_id, cookies_str=XHS_COOKIE)
                else:
                    success, msg, data = method_to_call(blogger_id, XHS_COOKIE)
            except Exception as e:
                break

            if success:
                current_page_notes = data.get("notes", []) if isinstance(data, dict) else data
                all_notes.extend(current_page_notes)
                print(f"   -> 本页获取到 {len(current_page_notes)} 篇笔记。")

                if isinstance(data, dict):
                    has_more = data.get("has_more", False)
                    current_cursor = data.get("cursor", "")
                    if not has_more or not current_cursor:
                        break
                else:
                    break 

                time.sleep(5) 
            else:
                break
        
        return all_notes
            
    except Exception:
        return []
    finally:
        os.chdir(original_cwd)

def extract_recipe_with_glm(note_data):
    system_prompt = """
    你是一个专业的营养师。请分析小红书减脂餐笔记内容，提取出符合以下 4 个类别的食材组合，并严格以 JSON 格式输出。

    【核心备餐要求】
    1. 份量需满足：一份男士晚餐 + 一份女士晚餐及次日午餐。
    2. 绝对禁止使用“苦瓜”！
    
    格式：
    {
      "tag": "菜系风格",
      "carbs": ["优质碳水1", "2"],
      "dish_1": ["蛋白质1", "2"],
      "dish_2": ["蔬菜1", "2"],
      "dish_3": ["补充1", "2"]
    }
    """
    
    title = note_data.get("display_title", "")
    desc = note_data.get("desc", "")
    text_content = f"【标题】: {title}\n【正文】: {desc}"
    
    if not text_content.strip():
        return None
        
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_content}
            ],
            temperature=0.1 
        )
        
        result_str = response.choices[0].message.content.strip()
        result_str = result_str.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed_data = json.loads(result_str)
        
        if isinstance(parsed_data, list) and len(parsed_data) > 0:
            parsed_data = parsed_data[0]
        return parsed_data if isinstance(parsed_data, dict) else None
    except Exception:
        return None

def main():
    print("🚀 启动数据更新任务（放宽去重阈值版）...")
    
    if os.path.exists(MENU_FILE) and os.path.getsize(MENU_FILE) > 0:
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            menu_data = json.load(f)
    else:
        menu_data = []

    # 汇总库中已有的所有菜名
    existing_dishes = []
    for day in menu_data:
        existing_dishes.extend(day.get("dish_1", []) + day.get("dish_2", []))

    new_recipes_added = 0

    for blogger_id in TARGET_BLOGGERS:
        recent_notes = fetch_xhs_notes_with_spider(blogger_id)
        
        for note in recent_notes:
            recipe_json = extract_recipe_with_glm(note)
            
            if recipe_json and isinstance(recipe_json, dict):
                # 提取新笔记中的核心菜名进行比对
                new_dishes = recipe_json.get("dish_1", []) + recipe_json.get("dish_2", [])
                
                # 只有当新菜谱中的所有主菜都不是重复的，才录入
                is_duplicate = any(is_duplicate_name(d, existing_dishes) for d in new_dishes)
                
                if not is_duplicate:
                    recipe_json["day"] = len(menu_data) + 1
                    menu_data.append(recipe_json)
                    existing_dishes.extend(new_dishes)
                    new_recipes_added += 1
                    print(f"✅ 成功录入：{recipe_json.get('tag')} - {new_dishes[0] if new_dishes else ''}")
                else:
                    print(f"❌ 相似度过高（超过5字重复），跳过: {note.get('display_title', '未命名')}")

    if new_recipes_added > 0:
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(menu_data, f, ensure_ascii=False, indent=4)
        print(f"🎉 任务完成！共追加 {new_recipes_added} 个新食谱。")
    else:
        print("🤷 库中已涵盖本次抓取的所有菜色。")

if __name__ == "__main__":
    main()
