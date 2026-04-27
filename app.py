import streamlit as st
import pandas as pd
from datetime import date

# 设置页面配置
st.set_page_config(page_title="双人亚洲风味减脂计划 v2", layout="wide", page_icon="🍱")

# --- 基础数据逻辑 ---
def calculate_bmr(gender, age, weight, height):
    """Mifflin-St Jeor Equation 计算静默代谢"""
    if gender == "男":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

# --- 30天不重复亚洲风味减脂菜单数据 (双选项版) ---
# 已严格剔除苦瓜，确保每天菜式唯一
menu_data = [
    {
        "day": 1, "tag": "中式经典",
        "carbs": ["糙米饭 🍚", "蒸玉米 🌽"],
        "dish_1": ["板栗烧鸡 🍗", "蚝油牛肉 🥩"],
        "dish_2": ["手撕包菜 🥬", "蒜泥西兰花 🥦"],
        "dish_3": ["紫菜蛋花汤 🥣", "无糖豆浆 🥛"]
    },
    {
        "day": 2, "tag": "面食风情",
        "carbs": ["荞麦面 🍜", "全麦馒头 🍞"],
        "dish_1": ["蒜苔炒肉丝 🥩", "香煎鸡胸肉 🍗"],
        "dish_2": ["拍黄瓜 🥒", "白灼菜心 🥬"],
        "dish_3": ["水煮蛋 🥚", "小番茄 🍅"]
    },
    {
        "day": 3, "tag": "鲜香清蒸",
        "carbs": ["蒸南瓜 🎃", "红薯 🍠"],
        "dish_1": ["清蒸鲈鱼 🐟", "白灼大虾 🦐"],
        "dish_2": ["白灼菜心 🥦", "清炒素什锦 🥗"],
        "dish_3": ["苹果 🍎", "低脂酸奶 🥛"]
    },
    {
        "day": 4, "tag": "泰式风味",
        "carbs": ["杂粮粥 🥣", "糙米饭 🍚"],
        "dish_1": ["泰式打抛猪 🌶️", "香烤鱿鱼 🦑"],
        "dish_2": ["生菜包肉 🥬", "凉拌木耳 🍄"],
        "dish_3": ["柠檬水 🍋", "椰子水 🥥"]
    },
    {
        "day": 5, "tag": "日式煎烤",
        "carbs": ["糙米饭 🍚", "土豆泥 🥔"],
        "dish_1": ["照烧三文鱼 🍣", "盐烤鲭鱼 🐟"],
        "dish_2": ["清炒秋葵 🥗", "蒸蛋羹 🥚"],
        "dish_3": ["味噌汤 🥣", "无糖麦茶 🍵"]
    },
    {
        "day": 6, "tag": "暖心煲汤",
        "carbs": ["山药 🥖", "芋头 🍠"],
        "dish_1": ["番茄牛腩 🍅", "萝卜炖排骨 🍖"],
        "dish_2": ["冬瓜片 🍈", "拌海带丝 🌊"],
        "dish_3": ["梨 🍐", "红枣水 ☕"]
    },
    {
        "day": 7, "tag": "低脂快炒",
        "carbs": ["黑米饭 🍙", "荞麦面 🍜"],
        "dish_1": ["干煸芸豆鸡丁 🥢", "彩椒炒虾仁 🍤"],
        "dish_2": ["蒜泥白肉(极瘦) 🥩", "凉拌豆芽 🥗"],
        "dish_3": ["奇异果 🥝", "普洱茶 🍵"]
    },
    {
        "day": 8, "tag": "西北风情",
        "carbs": ["全麦馕 🫓", "燕麦饭 🥣"],
        "dish_1": ["孜然炒羊肉 🐑", "卤牛腱子 🐂"],
        "dish_2": ["洋葱炒蛋 🧅", "醋溜土豆丝 🥔"],
        "dish_3": ["哈密瓜 🍈", "红茶 🍵"]
    },
    {
        "day": 9, "tag": "韩式轻食",
        "carbs": ["紫米饭 🍙", "玉米 🌽"],
        "dish_1": ["韩式辣白菜豆腐汤 🍲", "香煎黄鱼 🐟"],
        "dish_2": ["韩式拌豆芽 🥢", "芝麻拌菠菜 🥗"],
        "dish_3": ["煎豆腐 🧊", "大麦茶 🍵"]
    },
    {
        "day": 10, "tag": "川味减脂",
        "carbs": ["红薯 🍠", "糙米饭 🍚"],
        "dish_1": ["宫保鸡丁(低油) 🥜", "水煮鱼片(清汤版) 🐟"],
        "dish_2": ["干煸包菜 🥬", "凉拌黄瓜 🥒"],
        "dish_3": ["橘子 🍊", "柠檬水 🍋"]
    },
    {
        "day": 11, "tag": "东南亚风",
        "carbs": ["土豆泥 🥔", "糙米饭 🍚"],
        "dish_1": ["越式鲜虾卷 🌯", "香草烤鸡腿 🍗"],
        "dish_2": ["青木瓜丝沙拉 🥗", "蒜泥空心菜 🥬"],
        "dish_3": ["香蕉 🍌", "黑咖啡 ☕"]
    },
    {
        "day": 12, "tag": "潮汕清爽",
        "carbs": ["杂粮粥 🥣", "蒸山药 🥖"],
        "dish_1": ["蛤蜊蒸蛋 🥚", "清蒸排骨 🍖"],
        "dish_2": ["白灼芥兰 🥦", "炒黑木耳 🍄"],
        "dish_3": ["火龙果 🌵", "大红袍茶 🍵"]
    },
    {
        "day": 13, "tag": "家常温补",
        "carbs": ["小米饭 🍚", "南瓜饼(无糖) 🎃"],
        "dish_1": ["胡萝卜炖牛腩 🥩", "香菇蒸鸡 🍄"],
        "dish_2": ["清炒丝瓜 🥒", "西红柿炒蛋 🍅"],
        "dish_3": ["蓝莓 🫐", "无糖豆奶 🥛"]
    },
    {
        "day": 14, "tag": "海鲜盛宴",
        "carbs": ["意粉(全麦) 🍝", "糙米饭 🍚"],
        "dish_1": ["蒜蓉粉丝蒸扇贝 🐚", "辣炒蛏子 🌶️"],
        "dish_2": ["白灼芦笋 🥗", "上汤娃娃菜 🥬"],
        "dish_3": ["葡萄 🍇", "柠檬茶 🍋"]
    },
    {
        "day": 15, "tag": "快手便餐",
        "carbs": ["全麦卷饼 🌯", "荞麦面 🍜"],
        "dish_1": ["低脂午餐肉(自制) 🥩", "金枪鱼罐头(水浸) 🐟"],
        "dish_2": ["生菜叶 🥬", "凉拌魔芋丝 🥢"],
        "dish_3": ["圣女果 🍅", "低脂奶 🥛"]
    },
    {
        "day": 16, "tag": "沪式本帮",
        "carbs": ["红米饭 🍚", "蒸百合 🌸"],
        "dish_1": ["清炒虾仁 🍤", "响油鳝丝(少油) 🐍"],
        "dish_2": ["草头圈子(减脂版) 🥗", "四喜烤麸 🍄"],
        "dish_3": ["桃子 🍑", "菊花茶 🍵"]
    },
    {
        "day": 17, "tag": "日式暖锅",
        "carbs": ["乌冬面 🍜", "糙米饭 🍚"],
        "dish_1": ["关东煮(选肉类) 🍢", "牛肉寿喜锅 🍲"],
        "dish_2": ["魔芋丝 🥢", "香菇菜心 🥬"],
        "dish_3": ["橙子 🍊", "玄米茶 🍵"]
    },
    {
        "day": 18, "tag": "闽南风味",
        "carbs": ["地瓜粥 🥣", "面线糊(全麦) 🍜"],
        "dish_1": ["姜母鸭(去皮) 🦆", "清蒸海蛎 🦪"],
        "dish_2": ["白灼虾 🦐", "蒜炒通菜 🥬"],
        "dish_3": ["杨桃 ⭐️", "铁观音 🍵"]
    },
    {
        "day": 19, "tag": "京城味道",
        "carbs": ["二米饭 🍚", "杂粮煎饼 🌯"],
        "dish_1": ["酱牛肉 🐂", "京酱肉丝(瘦肉) 🥩"],
        "dish_2": ["拌三丝 🥕", "葱爆羊肉 🐑"],
        "dish_3": ["山楂水 🍒", "酸奶 🥛"]
    },
    {
        "day": 20, "tag": "南洋风情",
        "carbs": ["椰子饭(少椰浆) 🍚", "土豆 🥔"],
        "dish_1": ["新加坡海南鸡 🍗", "咖喱鱼片 🍛"],
        "dish_2": ["凉拌秋葵 🥗", "炒绿豆芽 🌱"],
        "dish_3": ["芒果片 🥭", "柠檬草茶 🍵"]
    },
    {
        "day": 21, "tag": "精致豆腐",
        "carbs": ["黑米饭 🍙", "玉米 🌽"],
        "dish_1": ["肉末蒸豆腐 🧊", "砂锅豆腐鱼 🍲"],
        "dish_2": ["荷兰豆炒肉片 🥗", "干椒扁豆 🥢"],
        "dish_3": ["火龙果 🌵", "黑豆浆 🥛"]
    },
    {
        "day": 22, "tag": "烤箱料理",
        "carbs": ["烤南瓜 🎃", "烤薯角 🥔"],
        "dish_1": ["柠檬烤鸡翅 🍗", "纸包鱼 🐟"],
        "dish_2": ["烤杂菜 🥕", "迷迭香蘑菇 🍄"],
        "dish_3": ["草莓 🍓", "苏打水 🥤"]
    },
    {
        "day": 23, "tag": "港式茶餐",
        "carbs": ["出前一丁(荞麦版) 🍜", "通粉 🍝"],
        "dish_1": ["滑蛋牛柳 🍳", "玫瑰油鸡(去皮) 🍗"],
        "dish_2": ["白灼生菜 🥬", "腐乳菜心 🥬"],
        "dish_3": ["西柚 🍊", "鸳鸯奶茶(无糖) ☕"]
    },
    {
        "day": 24, "tag": "农家风味",
        "carbs": ["窝窝头 🥯", "糙米饭 🍚"],
        "dish_1": ["小鸡炖蘑菇 🍄", "辣椒炒肉(里脊) 🥩"],
        "dish_2": ["蒸茄子 🍆", "大葱蘸酱 🧅"],
        "dish_3": ["甜瓜 🍈", "金银花茶 🍵"]
    },
    {
        "day": 25, "tag": "深海料理",
        "carbs": ["全麦面包 🍞", "红薯 🍠"],
        "dish_1": ["煎银鳕鱼 🐟", "香煎带鱼 🐟"],
        "dish_2": ["白灼海带 🌊", "蒜泥冬瓜 🍈"],
        "dish_3": ["猕猴桃 🥝", "蜂蜜水 🍯"]
    },
    {
        "day": 26, "tag": "菇类盛宴",
        "carbs": ["糙米饭 🍚", "燕麦饭 🥣"],
        "dish_1": ["双菇炒鸡片 🍄", "黑椒杏鲍菇牛肉粒 🥩"],
        "dish_2": ["蚝油生菜 🥬", "凉拌金针菇 🥢"],
        "dish_3": ["樱桃 🍒", "普洱茶 🍵"]
    },
    {
        "day": 27, "tag": "夏日清凉",
        "carbs": ["凉拌荞麦面 🍜", "冰镇红薯 🍠"],
        "dish_1": ["白斩鸡 🍗", "蒜泥肘子(去脂) 🍖"],
        "dish_2": ["凉拌粉丝 🥢", "生拌菜丝 🥗"],
        "dish_3": ["西瓜 🍉", "绿茶 🍵"]
    },
    {
        "day": 28, "tag": "冬日暖心",
        "carbs": ["羊肉萝卜汤饭 🍚", "杂粮馒头 🍞"],
        "dish_1": ["清炖羊肉 🐑", "萝卜煨猪蹄(去油) 🍖"],
        "dish_2": ["炒大白菜 🥬", "醋溜豆芽 🌱"],
        "dish_3": ["柿子 🍅", "姜茶 ☕"]
    },
    {
        "day": 29, "tag": "徽式风味",
        "carbs": ["糙米饭 🍚", "土豆 🥔"],
        "dish_1": ["臭鳜鱼(减脂版) 🐟", "笋干烧肉 🥩"],
        "dish_2": ["清炒毛豆 🫘", "蒜香苋菜 🥬"],
        "dish_3": ["枇杷 🍑", "铁观音 🍵"]
    },
    {
        "day": 30, "tag": "自由庆功",
        "carbs": ["自选优质碳水 🍚", "寿司 🍣"],
        "dish_1": ["海鲜火锅(清汤) 🍲", "烤肉(瘦肉类) 🍖"],
        "dish_2": ["时蔬拼盘 🥗", "菌菇拼盘 🍄"],
        "dish_3": ["全果拼盘 🍇", "香槟/无糖饮料 🥂"]
    }
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
    st.caption("注：男士中午在公司食堂，此处仅建议晚餐摄入量。")

# --- 主界面 ---
st.title("🍱 双人减脂 30 天计划 (双选版)")
st.markdown("💡 **男士**：公司午餐 + 家庭晚餐 | **女士**：家庭晚餐 + 次日打包午餐")

# 日历选择
selected_date = st.date_input("📅 点击日历选择日期", value=date.today())
# 计算相对于 30 天周期的索引
day_index = (selected_date - date(2024, 1, 1)).days % 30
meal = menu_data[day_index]

st.markdown(f"### 🗓️ 计划第 **{day_index + 1}** 天风格：`{meal['tag']}`")

# 选项展示
st.markdown("#### 🍱 今日双选清单 (每类可任选其一组合)")

# 布局：四个分类
cols = st.columns(4)
categories = [
    ("优质碳水", meal['carbs']),
    ("主菜 (肉蛋)", meal['dish_1']),
    ("副菜 (蔬果)", meal['dish_2']),
    ("额外补充", meal['dish_3'])
 category]

for col, (name, options) in zip(cols, categories):
    with col:
        st.markdown(f"**{name}**")
        st.info(f"方案 A: {options[0]}")
        st.warning(f"方案 B: {options[1]}")

st.markdown("---")

# 针对性建议
col_man, col_woman = st.columns(2)

with col_man:
    m_target = m_bmr * 0.45 
    st.markdown(f"""
    <div style="background-color:#e3f2fd; padding:20px; border-radius:15px; border-left:10px solid #1e88e5">
        <h3 style="color:#1e88e5; margin-top:0">🙋‍♂️ 男士晚餐指南</h3>
        <p style="font-size:18px">建议本餐摄入: <b>{int(m_target)} kcal</b></p>
        <p><b>执行细节：</b></p>
        <ul>
            <li><b>食堂提醒</b>：午餐尽量选瘦肉和青菜，少打勾芡菜。</li>
            <li><b>本餐配比</b>：选 1 种碳水 + 1 种主菜 + 1 种副菜。</li>
            <li><b>蛋白质</b>：确保主菜吃够 250g-300g。</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_woman:
    w_target = w_bmr * 0.4
    st.markdown(f"""
    <div style="background-color:#fce4ec; padding:20px; border-radius:15px; border-left:10px solid #d81b60">
        <h3 style="color:#d81b60; margin-top:0">🙋‍♀️ 女士(晚+午)指南</h3>
        <p style="font-size:18px">建议单顿摄入: <b>{int(w_target)} kcal</b></p>
        <p><b>执行细节：</b></p>
        <ul>
            <li><b>烹饪建议</b>：按 2 倍分量制作您选中的组合。</li>
            <li><b>打包策略</b>：煮好后先拨出一一半放入饭盒密封，防止晚餐吃超标。</li>
            <li><b>额外项</b>：如果是汤类，建议晚餐喝；如果是水果，建议带去公司吃。</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# 底部全局统计预览
with st.expander("📊 查看 30 天双选项完整菜单预览"):
    display_list = []
    for m in menu_data:
        display_list.append({
            "第X天": m['day'],
            "风格": m['tag'],
            "碳水 (A/B)": f"{m['carbs'][0]} / {m['carbs'][1]}",
            "主菜 (A/B)": f"{m['dish_1'][0]} / {m['dish_1'][1]}",
            "副菜 (A/B)": f"{m['dish_2'][0]} / {m['dish_2'][1]}",
            "补充 (A/B)": f"{m['dish_3'][0]} / {m['dish_3'][1]}"
        })
    df_preview = pd.DataFrame(display_list)
    st.table(df_preview)

st.caption("🚫 忌口：苦瓜。💡 烹饪提醒：即使是方案B，也请坚持少油少盐原则。")
