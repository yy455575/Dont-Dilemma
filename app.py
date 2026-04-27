import streamlit as st
import pandas as pd
from datetime import date

# 设置页面配置
st.set_page_config(page_title="双人亚洲风味减脂计划", layout="wide", page_icon="🍚")

# --- 基础数据逻辑 ---
def calculate_bmr(gender, age, weight, height):
    """Mifflin-St Jeor Equation 计算静默代谢"""
    if gender == "男":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

# --- 30天亚洲风味减脂菜单数据 (已剔除苦瓜) ---
# 每个条目包含：主食、主菜、副菜、额外
menu_data = [
    {"carbs": "糙米饭 🍚", "dish_1": "板栗烧鸡 🍗", "dish_2": "手撕包菜 🥬", "dish_3": "紫菜蛋花汤 🥣", "tag": "中式炖煮"},
    {"carbs": "荞麦面 🍜", "dish_1": "蒜苔炒肉丝 🥩", "dish_2": "拍黄瓜 🥒", "dish_3": "水煮蛋 🥚", "tag": "家常快炒"},
    {"carbs": "蒸南瓜 🎃", "dish_1": "清蒸鲈鱼 🐟", "dish_2": "白灼菜心 🥦", "dish_3": "小番茄 🍅", "tag": "粤式清蒸"},
    {"carbs": "杂粮粥 🥣", "dish_1": "泰式打抛猪肉末 🌶️", "dish_2": "生菜包肉 🥬", "dish_3": "无糖豆浆 🥛", "tag": "东南亚风"},
    {"carbs": "糙米饭 🍚", "dish_1": "日式照烧三文鱼 🍣", "dish_2": "清炒秋葵 🥗", "dish_3": "味噌汤 🥣", "tag": "日式煎烤"},
    {"carbs": "土豆泥 🥔", "dish_1": "番茄牛腩 🍅", "dish_2": "白灼西兰花 🥦", "dish_3": "酸奶 🥛", "tag": "中式温补"},
    {"carbs": "黑米饭 🍙", "dish_1": "蚝油牛肉 🥩", "dish_2": "干煸芸豆 🥢", "dish_3": "苹果片 🍎", "tag": "高纤组合"},
    {"carbs": "全麦馒头 🍞", "dish_1": "五香卤牛腱 🐂", "dish_2": "凉拌菠菜 🥗", "dish_3": "无糖茶 🍵", "tag": "低脂冷餐"},
    {"carbs": "玉米 🌽", "dish_1": "韩式辣白菜豆腐汤 🥘", "dish_2": "清炒糊豆角 🥢", "dish_3": "煎豆腐 🧊", "tag": "韩式低卡"},
    {"carbs": "燕麦饭 🍚", "dish_1": "宫保鸡丁(少油) 🥜", "dish_2": "蒜泥生菜 🥗", "dish_3": "梨 🍐", "tag": "经典川味"},
    {"carbs": "红薯 🍠", "dish_1": "香煎虾仁 🍤", "dish_2": "清炒丝瓜 🥒", "dish_3": "菌菇汤 🍄", "tag": "鲜香组合"},
    {"carbs": "糙米饭 🍚", "dish_1": "酸菜鱼片 🐟", "dish_2": "白灼虾 🦐", "dish_3": "炒菜苔 🥬", "tag": "开胃酸爽"},
    {"carbs": "魔芋面 🍜", "dish_1": "麻辣拌(酱油醋调味) 🌶️", "dish_2": "海带结 🌊", "dish_3": "荷包蛋 🍳", "tag": "中式轻食"},
    {"carbs": "玉米 🌽", "dish_1": "胡萝卜炖排骨 🍖", "dish_2": "冬瓜片 🍈", "dish_3": "蓝莓 🫐", "tag": "清甜炖汤"},
    {"carbs": "黑米饭 🍙", "dish_1": "滑蛋虾仁 🍳", "dish_2": "荷兰豆炒腊肉(少量) 🥗", "dish_3": "海米紫菜 🥣", "tag": "清爽小炒"},
    {"carbs": "土豆 🥔", "dish_1": "低脂黄咖喱鸡 🍛", "dish_2": "洋葱炒蛋 🥚", "dish_3": "西柚 🍊", "tag": "南洋风味"},
    {"carbs": "山药 🥖", "dish_1": "木耳炒肉片 🥩", "dish_2": "清炒时蔬 🥬", "dish_3": "红枣茶 ☕", "tag": "滋补高纤"},
    {"carbs": "米纸卷 🌯", "dish_1": "鲜虾米纸卷 🦐", "dish_2": "蘸水豆花 🍶", "dish_3": "坚果 🥜", "tag": "越式清爽"},
    {"carbs": "糙米饭 🍚", "dish_1": "什锦蒸豆腐 🧊", "dish_2": "肉末茄子(少油) 🍆", "dish_3": "清汤 🥣", "tag": "软糯易消"},
    {"carbs": "全麦面 🍝", "dish_1": "黑椒牛肉粒 🥩", "dish_2": "杏鲍菇 🍄", "dish_3": "奇异果 🥝", "tag": "能量充沛"},
    {"carbs": "红薯 🍠", "dish_1": "清蒸大闸蟹/虾 🦀", "dish_2": "醋溜土豆丝 🥔", "dish_3": "姜茶 🍵", "tag": "时令鲜美"},
    {"carbs": "糙米饭 🍚", "dish_1": "柠檬煎鱼排 🐟", "dish_2": "烤南瓜块 🎃", "dish_3": "蔬菜沙拉 🥗", "tag": "清新融合"},
    {"carbs": "燕麦饭 🍚", "dish_1": "孜然羊肉(瘦) 🐑", "dish_2": "爆炒洋葱 🧅", "dish_3": "哈密瓜 🍈", "tag": "西北风味"},
    {"carbs": "玉米 🌽", "dish_1": "冬瓜海米炖鸡翅 🍗", "dish_2": "凉拌木耳 🍄", "dish_3": "鲜榨豆浆 🍶", "tag": "清火消肿"},
    {"carbs": "黑米饭 🍙", "dish_1": "蒜泥白肉(极瘦) 🥩", "dish_2": "白灼秋葵 🥗", "dish_3": "葡萄 🍇", "tag": "川式凉菜"},
    {"carbs": "糙米饭 🍚", "dish_1": "金汤肥牛(魔芋丝垫底) 🥘", "dish_2": "手撕包菜 🥬", "dish_3": "柠檬水 🍋", "tag": "浓郁低卡"},
    {"carbs": "荞麦面 🍜", "dish_1": "鸡肉豆腐狮子头 🧆", "dish_2": "炒上海青 🥬", "dish_3": "蛋花汤 🥣", "tag": "精致淮扬"},
    {"carbs": "南瓜 🎃", "dish_1": "蛤蜊蒸蛋 🥚", "dish_2": "清炒西兰花 🥦", "dish_3": "草莓 🍓", "tag": "高钙早餐"},
    {"carbs": "糙米饭 🍚", "dish_1": "葱油焖鸡 🍗", "dish_2": "凉拌腐竹 🥢", "dish_3": "绿豆汤 🥣", "tag": "香气十足"},
    {"carbs": "自由主食 🍚", "dish_1": "奖励餐(控制在BMR内) 🍱", "dish_2": "自选时蔬 🥬", "dish_3": "全果 🍎", "tag": "阶段总结"}
]

# --- 侧边栏：身体参数计算 ---
st.sidebar.header("⚖️ 个人基础数据")
with st.sidebar:
    st.markdown("### 男士 (27岁)")
    m_weight = st.number_input("男士体重 (kg)", value=75, key="m_w")
    m_height = st.number_input("男士身高 (cm)", value=175, key="m_h")
    m_bmr = calculate_bmr("男", 27, m_weight, m_height)
    st.success(f"BMR: **{m_bmr:.0f} kcal/日**")

    st.markdown("---")
    st.markdown("### 女士 (29岁)")
    w_weight = st.number_input("女士体重 (kg)", value=55, key="w_w")
    w_height = st.number_input("女士身高 (cm)", value=160, key="w_h")
    w_bmr = calculate_bmr("女", 29, w_weight, w_height)
    st.success(f"BMR: **{w_bmr:.0f} kcal/日**")
    
    st.markdown("---")
    st.caption("注：计算结果为静默状态下的卡路里消耗，实际减脂摄入建议在此基础上调整。")

# --- 主界面 ---
st.title("🍱 双人减脂 30 天计划 (亚洲胃版)")
st.markdown("💡 **男士**：全天一顿(OMAD) | **女士**：晚餐 + 次日打包午餐")

# 日历选择逻辑
selected_date = st.date_input("📅 点击选择日期查看食谱", value=date.today())
# 计算相对于 30 天周期的索引 (取模运算实现循环)
day_index = (selected_date - date(2024, 1, 1)).days % 30
meal = menu_data[day_index]

st.markdown(f"### 🗓️ 计划第 **{day_index + 1}** 天风格：`{meal['tag']}`")

# 菜品详情展示区
st.markdown("#### 🍱 今日详细菜单")
col_c, col_d1, col_d2, col_d3 = st.columns(4)

with col_c:
    st.info("**优质碳水**")
    st.subheader(meal['carbs'])

with col_d1:
    st.info("**主食肉/蛋**")
    st.subheader(meal['dish_1'])

with col_d2:
    st.info("**高纤副菜**")
    st.subheader(meal['dish_2'])

with col_d3:
    st.info("**额外补充**")
    st.subheader(meal['dish_3'])

st.markdown("---")

# 卡路里与分量建议
col_man, col_woman = st.columns(2)

with col_man:
    m_target = m_bmr * 0.7  # 男士一餐吃饱，取BMR的70%左右
    st.markdown(f"""
    <div style="background-color:#e3f2fd; padding:20px; border-radius:15px; border-left:10px solid #1e88e5">
        <h3 style="color:#1e88e5; margin-top:0">🙋‍♂️ 男士进食指南</h3>
        <p style="font-size:18px">建议单餐摄入: <b>{int(m_target)} kcal</b></p>
        <ul>
            <li><b>主食</b>：约 2 碗 (熟重约300g)</li>
            <li><b>主菜</b>：约 300g 肉类</li>
            <li><b>蔬菜</b>：不限量，吃到饱为止</li>
        </ul>
        <p style="font-size:12px; color:#1e88e5"><i>* 仅此一顿，请务必吃够蛋白质，避免掉肌肉。</i></p>
    </div>
    """, unsafe_allow_html=True)

with col_woman:
    w_target = w_bmr * 0.4  # 女士单顿取40%
    st.markdown(f"""
    <div style="background-color:#fce4ec; padding:20px; border-radius:15px; border-left:10px solid #d81b60">
        <h3 style="color:#d81b60; margin-top:0">🙋‍♀️ 女士进食指南</h3>
        <p style="font-size:18px">建议单餐摄入: <b>{int(w_target)} kcal</b></p>
        <ul>
            <li><b>主食</b>：约 0.8 碗 (熟重约120g)</li>
            <li><b>主菜</b>：约 150g 肉类</li>
            <li><b>准备</b>：烹饪时按 <b>2倍</b> 分量制作，一半带入次日午餐</li>
        </ul>
        <p style="font-size:12px; color:#d81b60"><i>* 记得准备一个高质量的密封饭盒。</i></p>
    </div>
    """, unsafe_allow_html=True)

# 底部全局统计预览
with st.expander("📊 查看 30 天完整菜单预览"):
    df_preview = pd.DataFrame(menu_data)
    df_preview.index = df_preview.index + 1
    df_preview.columns = ["主食", "主菜", "副菜", "补充/汤", "风格标签"]
    st.table(df_preview)

st.caption("🚫 本计划已严格过滤：苦瓜。建议烹饪时采用：蒸、煮、快炒、空气炸，控盐控油。")
