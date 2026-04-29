import json
import os
import sys
import time
import requests
import inspect
from zhipuai import ZhipuAI  # 🌟 引入智谱 SDK

# --- 将拉取下来的 Spider_XHS 加入系统路径 ---
sys.path.append(os.path.join(os.getcwd(), "Spider_XHS"))

ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY")
XHS_COOKIE = os.environ.get("XHS_COOKIE") 

# 🌟 初始化智谱客户端
if not ZHIPU_API_KEY:
    print("⚠️ 警告: 未检测到 ZHIPU_API_KEY 环境变量！")
client = ZhipuAI(api_key=ZHIPU_API_KEY)

TARGET_BLOGGERS = [
    "69a5292900000000210079b7",
    "5bf511b0576d7b0001dd4373", 
    "66fa9e53000000001d02293c"
] 
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
            available_methods = [m for m in dir(pc_api) if callable(getattr(pc_api, m)) and not m.startswith('_')]
            print(f"⚠️ 找不到目标抓取方法！当前 XHS_Apis 支持的方法有：\n{available_methods}")
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
                print(f"⚠️ 翻页传参异常: {e}")
                break

            if success:
                current_page_notes = data.get("notes", []) if isinstance(data, dict) else data
                all_notes.extend(current_page_notes)
                print(f"   -> 本页获取到 {len(current_page_notes)} 篇笔记。")

                if isinstance(data, dict):
                    has_more = data.get("has_more", False)
                    current_cursor = data.get("cursor", "")
                    if not has_more or not current_cursor:
                        print("   -> 博主内容已到底，停止翻页。")
                        break
                else:
                    break 

                time.sleep(5) 
            else:
                print(f"❌ 接口请求失败 (大概率是 Cookie 失效或 IP 风控): {msg}")
                break
        
        print(f"🎉 翻页结束！共计提取该博主 {len(all_notes)} 篇近期笔记准备送交 AI 分析...")
        return all_notes
            
    except Exception as e:
        print(f"Spider_XHS 引擎运行异常: {e}")
        return []
    finally:
        os.chdir(original_cwd)

def extract_recipe_with_glm(note_data):
    """使用智谱 GLM 模型提取图文数据"""
    system_prompt = """
    你是一个专业的营养师。请分析小红书减脂餐笔记内容，提取出符合以下 4 个类别的食材组合，并严格以 JSON 格式输出，不要输出任何多余的解释文字。

    【核心备餐要求】
    1. 份量与搭配需能同时满足：一份男士晚餐 + 一份女士晚餐及次日午餐。
    2. 绝对不能包含“苦瓜”！如果原笔记中有苦瓜，请替换为其他蔬菜或直接剔除。
    
    需要的 JSON 字段：
    - tag: 菜系或风格（如"中式家常"）
    - carbs: 包含2个字符串的数组，提取优质碳水
    - dish_1: 包含2个字符串的数组，提取主菜/高蛋白肉类
    - dish_2: 包含2个字符串的数组，提取副菜/蔬菜类
    - dish_3: 包含2个字符串的数组，提取额外补充/水果饮品
    """
    
    title = note_data.get("display_title", "")
    desc = note_data.get("desc", "")
    text_content = f"【标题】: {title}\n【正文】: {desc}"
    
    if not text_content.strip():
        return None
        
    try:
        # 🌟 调用智谱 GLM 接口
        response = client.chat.completions.create(
            model="glm-4-flash",  # 推荐使用 flash 模型处理结构化提取，速度快
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_content}
            ],
            temperature=0.1 # 调低温度值，保证 JSON 格式更稳定
        )
        
        result_str = response.choices[0].message.content.strip()
        # 清理可能带有的 markdown 标记
        result_str = result_str.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(result_str)
        
    except Exception as e:
        print(f"GLM 提取失败/格式错误: {e}")
        return None

def main():
    print("🚀 开始执行减脂餐更新流水线 (GLM 引擎版)...")
    
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
            recipe_json = extract_recipe_with_glm(note)
            
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
                    print(f"❌ 触发去重机制，跳过内容: {note.get('display_title', '未命名')}")

    if new_recipes_added > 0:
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(menu_data, f, ensure_ascii=False, indent=4)
        print(f"🎉 任务完成！成功利用 Spider_XHS 追加 {new_recipes_added} 个新食谱。")
    else:
        print("🤷 本周暂无符合条件的新食谱更新。")

if __name__ == "__main__":
    main()
