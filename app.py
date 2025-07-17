import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="실시간 지진 대시보드", layout="wide")

st.title("🌍 실시간 전 세계 지진 데이터 대시보드")

url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_month.geojson"
response = requests.get(url)
data = response.json()

features = data["features"]
rows = []
for f in features:
    prop = f["properties"]
    geom = f["geometry"]
    rows.append({
        "place": prop["place"],
        "time": pd.to_datetime(prop["time"], unit="ms"),
        "magnitude": prop["mag"],  
        "latitude": geom["coordinates"][1],
        "longitude": geom["coordinates"][0],
        "depth": geom["coordinates"][2]
    })

df = pd.DataFrame(rows)

st.sidebar.header("필터 옵션")

min_mag = st.sidebar.slider("최소 지진 규모", 1.0, 10.0, 4.0)
region_filter = st.sidebar.text_input("지역 키워드 (예: Japan, California, Korea)")

filtered_df = df[df["magnitude"] >= min_mag]
if region_filter.strip():
    filtered_df = filtered_df[filtered_df["place"].str.contains(region_filter, case=False, na=False)]

st.markdown(f"#### ✅ 조건에 맞는 지진 개수: **{filtered_df.shape[0]}건**")
if filtered_df.shape[0] > 0:
    st.dataframe(filtered_df[["time", "place", "magnitude", "depth"]].sort_values("time", ascending=False), height=200)

    fig = px.scatter_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        color="magnitude",       
        size="magnitude",        
        hover_name="place",
        hover_data=["time", "depth"],
        zoom=1,
        height=600,
        mapbox_style="open-street-map",
        title="실시간 지진 위치 및 매그니튜드"
    )
    st.plotly_chart(fig)
else:
    st.warning("⚠ 조건에 맞는 지진 데이터가 없습니다.")

st.markdown("---")
st.subheader("깊이에 따른 지진의 분류와 특징")

depth_info = {
    "깊이 구간": ["0 ~ 70km", "70 ~ 300km", "300 ~ 700km 이상"],
    "분류": ["천발 지진 (얕은 지진)", "중발 지진", "심발 지진"],
    "특징": [
        "에너지가 지표 가까이 전달돼 피해가 큼",
        "흔들림은 있지만 피해는 상대적으로 적음",
        "깊어서 진동이 넓게 퍼지지만 피해는 작음"
    ]
}

depth_df = pd.DataFrame(depth_info)
st.table(depth_df)