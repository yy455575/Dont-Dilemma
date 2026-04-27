import streamlit as st
import pandas as pd
from datetime import date
import json
import os

st.set_page_config(page_title="双人亚洲风味减脂计划 v2", layout="wide", page_icon="🍱")

def calculate_bmr(gender, age, weight, height):
    if gender == "男":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

@st.cache_data
def load_menu_data():
    if not os.path.exists("menu_data.json"):
        st.error("⚠️ 找不到 menu_data.json 数据文件。")
        return []
    
    if os.path.getsize("menu_data.json") == 0:
        st.warning("⚠️ 菜单数据初始化中，等待自动化脚本写入新食谱...")
        return []
        
    try:
        with open("menu_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        st.error("⚠️ 数据文件格式存在异常，请检查 JSON 结构。")
        return []
    except Exception as e:
        st.error(f"读取数据出现未知错误: {e}")
        return []

menu_data = load_menu_data()

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

st.title("🍱 双人减脂计划 (自动扩充版)")
st.markdown("💡 **男士**：公司午餐 + 家庭晚餐 | **女士**：家庭晚餐 + 次日打包午餐")

if not menu_data:
    st.stop()

selected_date = st.date_input("📅 点击日历选择日期", value=date.today())
total_days = len(menu_data)
day_index = (selected_date - date(2024, 1, 1)).days % total_days
meal = menu_data[day_index]

st.markdown(f"### 🗓️ 计划第 **{meal.get('day', day_index + 1)}** 天风格：`{meal.get('tag', '未分类')}`")
st.markdown("#### 🍱 今日双选清单 (每类可任选其一组合)")

cols = st.columns(4)
categories = [
    ("优质碳水", meal.get('carbs', ["-", "-"])),
    ("主菜 (肉蛋)", meal.get('dish_1', ["-", "-"])),
    ("副菜 (蔬果)", meal.get('dish_2', ["-", "-"])),
    ("额外补充", meal.get('dish_3', ["-", "-"]))
]

for col, (name, options) in zip(cols, categories):
    with col:
        st.markdown(f"**{name}**")
        st.info(f"方案 A: {options[0] if len(options)>0 else '-'}")
        st.warning(f"方案 B: {options[1] if len(options)>1 else '-'}")

st.markdown("---")

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
            <li><b>打包策略</b>：煮好后先拨出一半放入饭盒密封，防止晚餐吃超标。</li>
            <li><b>额外项</b>：如果是汤类，建议晚餐喝；如果是水果，建议带去公司吃。</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with st.expander(f"📊 查看当前数据库完整菜单预览 (共 {total_days} 天)"):
    display_list = []
    for m in menu_data:
        display_list.append({
            "第X天": m.get('day', '-'),
            "风格": m.get('tag', '-'),
            "碳水 (A/B)": f"{m.get('carbs', ['-','-'])[0]} / {m.get('carbs', ['-','-'])[1]}",
            "主菜 (A/B)": f"{m.get('dish_1', ['-','-'])[0]} / {m.get('dish_1', ['-','-'])[1]}",
            "副菜 (A/B)": f"{m.get('dish_2', ['-','-'])[0]} / {m.get('dish_2', ['-','-'])[1]}",
            "补充 (A/B)": f"{m.get('dish_3', ['-','-'])[0]} / {m.get('dish_3', ['-','-'])[1]}"
        })
    st.dataframe(pd.DataFrame(display_list), use_container_width=True)

st.caption("🚫 忌口：苦瓜。💡 烹饪提醒：即使是方案B，也请坚持少油少盐原则。")
