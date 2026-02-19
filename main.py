import streamlit as st
import pandas as pd
from con_db import fetch_data

st.set_page_config(layout="wide")

st.markdown("""
<style>
section[data-testid="stSidebar"] { width: 260px !important; }
section[data-testid="stSidebar"] > div { width: 260px !important; }
.block-container { padding-top: 3rem; padding-left: 2rem; padding-right: 2rem; }
</style>
""", unsafe_allow_html=True)

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "all"

if "selected_volume_view" not in st.session_state:
    st.session_state.selected_volume_view = None

df = pd.DataFrame(fetch_data())
def extract_brand(name):
    if pd.isna(name):
        return ""
    return name.split()[0]

df["brand"] = df["name"].apply(extract_brand)

with st.sidebar:
    st.header("🔎 ตัวกรองสินค้า")

    category_list = ["ทั้งหมด"] + sorted(df["category"].dropna().unique())
    selected_category = st.selectbox("หมวดหมู่", category_list)

    search = st.text_input("ค้นหาสินค้า")

    brand_list = sorted(df["brand"].dropna().unique())
    selected_brands = st.multiselect("เลือกแบรนด์", brand_list)

    volume_options = ["ทั้งหมด"] + sorted(df["std_volume"].dropna().unique())
    selected_volume = st.selectbox("ปริมาตร", volume_options)

def show_same_volume(volume):
    st.session_state.view_mode = "volume"
    st.session_state.selected_volume_view = volume

filtered_df = df.copy()

if st.session_state.view_mode == "volume":
    filtered_df = filtered_df[
        filtered_df["std_volume"] == st.session_state.selected_volume_view
    ]
    st.info(f"แสดงสินค้าปริมาตร: {st.session_state.selected_volume_view}")

else:
    if selected_category != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]

    if search:
        keywords = search.lower().split()
        filtered_df = filtered_df[
            filtered_df["name"].str.lower().apply(
                lambda name: all(word in name for word in keywords)
            )
        ]

    if selected_brands:
        filtered_df = filtered_df[
            filtered_df["brand"].isin(selected_brands)
        ]
    if selected_volume != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df["std_volume"] == selected_volume]

filtered_df = filtered_df.sort_values(by="price_per_unit", ascending=True)
st.title("🛒 เปรียบเทียบราคาต่อหน่วย")
st.write(f"พบสินค้า {len(filtered_df)} รายการ")

if st.session_state.view_mode == "volume":
    if st.button("⬅️ กลับไปหน้าหลัก"):
        st.session_state.view_mode = "all"

NUM_COLUMNS = 8

rows = [filtered_df[i:i+NUM_COLUMNS] for i in range(0, len(filtered_df), NUM_COLUMNS)]

for row_items in rows:
    cols = st.columns(len(row_items))

    for col, (_, item) in zip(cols, row_items.iterrows()):
        with col:
            st.image(item["url_image"], use_container_width=True)
            st.caption(item["name"])
            st.write(f"💰 {item['price_per_unit']:.3f} บาท/หน่วย")
            st.write(f"⚖️ {item['std_volume']}")
            st.write(f"📦 {item['category']}")
            if st.button("ดูขนาดเดียวกัน", key=f"vol_{item['id']}"):
                show_same_volume(item["std_volume"])
