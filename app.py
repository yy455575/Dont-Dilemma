import streamlit as st
import pandas as pd

# 设置页面配置
st.set_page_config(page_title="双人减脂食谱工具", layout="wide", page_icon="🥗")

# --- 基础数据逻辑 ---
def calculate_bmr(gender, age, weight, height):
    """Mifflin-St Jeor Equation"""
    if gender == "男":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

# --- 30天亚洲风味减脂菜单数据 ---
# 注意：女士晚餐需预留次日午餐，故女士份量实际需烹饪2份，表中展示为单顿热量
menu_data = [
    {"day": 1, "title": "板栗烧鸡配手撕包菜", "desc": "中式炖煮。板栗替代部分主食，包菜低卡饱腹。", "tag": "中式", "img_key": "braised-chicken"},
    {"day": 2, "title": "蒜苔炒肉丝配荞麦面", "desc": "经典家常菜。瘦肉丝提供蛋白，荞麦面低GI。", "tag": "中式", "img_key": "stir-fry-pork"},
    {"day": 3, "title": "清蒸鲈鱼配白灼菜心", "desc": "优质白肉。鱼肉鲜美且脂肪极低。", "tag": "粤式", "img_key": "steamed-fish"},
    {"day": 4, "title": "泰式打抛猪肉末(瘦)配生菜", "desc": "用生菜包肉末，低碳水且风味十足。", "tag": "泰式", "img_key": "thai-pork"},
    {"day": 5, "title": "日式照烧三文鱼配秋葵", "desc": "Omega-3丰富。照烧汁少量使用，配糙米饭。", "tag": "日式", "img_key": "teriyaki-salmon"},
    {"day": 6, "title": "番茄牛腩煲配冬瓜", "desc": "冬瓜吸油且利尿，牛腩补充铁质。", "tag": "中式", "img_key": "tomato-beef"},
    {"day": 7, "title": "蚝油牛肉炒西兰花", "desc": "健身房经典，但加入蚝油更符合中式口味。", "tag": "中式", "img_key": "broccoli-beef"},
    {"day": 8, "title": "五香卤牛腱配拌黄瓜", "desc": "凉拌清爽。牛腱肉极低脂，适合大量备餐。", "tag": "中式", "img_key": "braised-beef"},
    {"day": 9, "title": "韩式辣白菜豆腐汤", "desc": "热量极低。加入大量豆腐和菌菇补充蛋白。", "tag": "韩式", "img_key": "tofu-stew"},
    {"day": 10, "title": "干煸芸豆鸡肉丁", "desc": "少油版。芸豆提供丰富植物纤维。", "tag": "中式", "img_key": "chicken-green-beans"},
    {"day": 11, "title": "香烤鱿鱼圈配芦笋", "desc": "海鲜低卡高蛋白。芦笋利尿消肿。", "tag": "海鲜", "img_key": "grilled-squid"},
    {"day": 12, "title": "酸菜鱼(龙利鱼/黑鱼)", "desc": "酸爽开胃。鱼片丝滑，热量集中在汤底（少喝汤）。", "tag": "川式", "img_key": "fish-soup"},
    {"day": 13, "title": "麻辣拌(无麻酱版)配魔芋", "desc": "各种时蔬+虾仁，用生抽/陈醋/辣椒粉调味。", "tag": "中式", "img_key": "mala-ban"},
    {"day": 14, "title": "胡萝卜玉米炖排骨", "desc": "排骨选小排，汤头清甜。排骨肉量需控制。", "tag": "中式", "img_key": "pork-rib-soup"},
    {"day": 15, "title": "滑蛋虾仁配炒素杂菜", "desc": "口感柔和。杂菜包含玉米粒、豌豆、胡萝卜。", "tag": "中式", "img_key": "shrimp-egg"},
    {"day": 16, "title": "咖喱时蔬炒鸡丁", "desc": "低脂咖喱粉，不加椰浆。多放洋葱和青椒。", "tag": "东南亚", "img_key": "curry-chicken"},
    {"day": 17, "title": "清炒山药木耳肉片", "desc": "山药替代部分米饭，木耳清理肠道。", "tag": "中式", "img_key": "yam-pork"},
    {"day": 18, "title": "越式鲜虾米纸卷", "desc": "包裹大量蔬菜。清脆爽口，热量极低。", "tag": "越式", "img_key": "spring-rolls"},
    {"day": 19, "title": "什锦蒸豆腐(虾仁/肉末)", "desc": "优质蛋白。饱腹感强，油脂极少。", "tag": "中式", "img_key": "steamed-tofu"},
    {"day": 20, "title": "宫保鸡丁(低油版)", "desc": "去掉油炸花生，用黄瓜丁和少量腰果代替。", "tag": "川式", "img_key": "kung-pao-chicken"},
    {"day": 21, "title": "彩椒腰果炒虾仁", "desc": "补充优质油脂。虾仁Q弹。", "tag": "中式", "img_key": "shrimp-cashew"},
    {"day": 22, "title": "香煎龙利鱼配烤南瓜", "desc": "南瓜软糯。龙利鱼无刺，适合打包午餐。", "tag": "融合", "img_key": "basa-fish"},
    {"day": 23, "title": "黑椒杏鲍菇牛肉粒", "desc": "菌菇口感像肉，能减少实际肉类热量。", "tag": "中式", "img_key": "black-pepper-beef"},
    {"day": 24, "title": "冬瓜海米汤配蒸鸡翅", "desc": "鸡翅去皮减少一半脂肪。冬瓜汤清火。", "tag": "中式", "img_key": "winter-melon-soup"},
    {"day": 25, "title": "孜然炒羊肉(瘦)配洋葱", "desc": "洋葱解腻。羊肉提高代谢（热性）。", "tag": "西北风味", "img_key": "cumin-lamb"},
    {"day": 26, "title": "蒜泥白肉(选极瘦)配黄瓜片", "desc": "蘸水少油。肉片薄切，配大量黄瓜。", "tag": "川式", "img_key": "garlic-pork"},
    {"day": 27, "title": "金汤肥牛(魔芋丝垫底)", "desc": "南瓜泥调色。魔芋丝吸收汤汁，零负担。", "tag": "中式", "img_key": "golden-beef"},
    {"day": 28, "title": "红烧狮子头(鸡肉豆腐版)", "desc": "鸡肉泥混入嫩豆腐，软糯且低脂。", "tag": "中式", "img_key": "chicken-meatball"},
    {"day": 29, "title": "蛤蜊蒸蛋配炒时蔬", "desc": "鲜味十足。鸡蛋是性价比最高的蛋白。", "tag": "中式", "img_key": "steamed-egg"},
    {"day": 30, "title": "自由餐(奖励日)", "desc": "自选火锅或烤肉，但建议维持在BMR范围内。", "tag": "奖励", "img_key": "cheat-meal"}
]

# --- 侧边栏：计算器 ---
st.sidebar.header("📊 身体指数计算 (BMR)")
with st.sidebar:
    st.markdown("### 男士 (27岁)")
    m_weight = st.number_input("男士体重 (kg)", value=75, key="m_w")
    m_height = st.number_input("男士身高 (cm)", value=175, key="m_h")
    m_bmr = calculate_bmr("男", 27, m_weight, m_height)
    st.info(f"男士静默消耗: **{m_bmr:.0f} kcal/日**")

    st.markdown("---")
    st.markdown("### 女士 (29岁)")
    w_weight = st.number_input("女士体重 (kg)", value=55, key="w_w")
    w_height = st.number_input("女士身高 (cm)", value=160, key="w_h")
    w_bmr = calculate_bmr("女", 29, w_weight, w_height)
    st.info(f"女士静默消耗: **{w_bmr:.0f} kcal/日**")
    
    st.write("💡 *静默代谢即为您躺平不动时身体维持基本生命体征所需的能量。*")

# --- 主界面 ---
st.title("🍚 双人减脂 30 天计划 (亚洲风味版)")
st.markdown("男士：**OMAD模式** (全天仅晚餐一顿) | 女士：**Meal Prep** (当晚+次日午餐)")

# 选择日期
day_selected = st.slider("选择计划天数", 1, 30, 1)
meal = menu_data[day_selected-1]

# 展示今日菜单
col_text, col_img = st.columns([2, 1])

with col_text:
    st.subheader(f"📅 第 {day_selected} 天：{meal['title']}")
    st.markdown(f"**风格**: `{meal['tag']}`")
    st.write(meal['desc'])
    
    # 卡路里详情
    m_target = m_bmr * 0.6  # 男士一餐摄入约静默代谢的60%，预留缺口
    w_target = w_bmr * 0.35 # 女士每顿摄入约35%，两顿共70%
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div style="background-color:#e1f5fe; padding:15px; border-radius:15px; border-left:5px solid #0288d1">
            <h4 style="color:#0288d1; margin-top:0">男士 (晚餐)</h4>
            <p style="font-size:24px; font-weight:bold; margin-bottom:0">{int(m_target)} kcal</p>
            <p style="font-size:12px; color:#546e7a">约占BMR 60%，专注高蛋白</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div style="background-color:#fce4ec; padding:15px; border-radius:15px; border-left:5px solid #d81b60">
            <h4 style="color:#d81b60; margin-top:0">女士 (晚餐+午餐)</h4>
            <p style="font-size:24px; font-weight:bold; margin-bottom:0">{int(w_target)} kcal / 顿</p>
            <p style="font-size:12px; color:#880e4f">两顿合计: {int(w_target*2)} kcal</p>
        </div>
        """, unsafe_allow_html=True)

with col_img:
    # 模拟图片展示
    img_url = f"https://source.unsplash.com/400x300/?healthy-food,{meal['img_key']}"
    st.image(img_url, caption=meal['title'], use_column_width=True)

# 详细食材清单
st.markdown("### 🛒 采购与准备指南")
t1, t2 = st.tabs(["男士分量", "女士分量 (2顿)"])

with t1:
    st.write(f"**建议食材**: 主料(肉/鱼)约 300g，粗粮主食约 150g，蔬菜不限量。")
    st.checkbox("男士：今晚完成力量训练后进食")

with t2:
    st.write(f"**建议食材**: 主料(肉/鱼)约 250g，粗粮主食约 120g，蔬菜不限量。")
    st.warning("⚠️ **提醒**：请在烹饪完成后，立即将一半份量装入饭盒密封，冷藏作为明日午餐。")

# 底部全局统计
st.markdown("---")
st.markdown("### 📈 30天周期表预览")
df_menu = pd.DataFrame(menu_data)[["day", "title", "tag"]]
st.dataframe(df_menu, use_container_width=True, hide_index=True)

st.caption("注：图片为动态生成，仅供参考。菜单会根据季节热点持续更新。")
