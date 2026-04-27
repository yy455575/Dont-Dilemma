import streamlit as st
import pandas as pd
from datetime import date
import json # 新增：用于读取动态数据文件

# 设置页面配置
st.set_page_config(page_title="双人亚洲风味减脂计划 v2", layout="wide", page_icon="🍱")

# --- 基础数据逻辑 ---
def calculate_bmr(gender, age, weight, height):
    # ... 此处代码保持不变 ...
    pass

# --- 读取动态菜单数据 ---
# 彻底替换掉原来的 menu_data = [...] 静态长列表
@st.cache_data # 使用 Streamlit 缓存机制，避免页面每次刷新都重新读取文件
def load_menu_data():
    try:
        with open("menu_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("找不到菜单数据文件，请确保 menu_data.json 存在。")
        return []

menu_data = load_menu_data()

# ---------------------------------------------------------
# 后续的侧边栏、日历选择、主界面布局和 UI 逻辑完全不需要变动
# ---------------------------------------------------------
