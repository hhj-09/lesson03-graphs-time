import streamlit as st
import pandas as pd
import plotly.express as px


# ==================================================
# 페이지 설정
# ==================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")

st.write(
    "1년치 일별 박스오피스 데이터를 이용해 "
    "영화의 관객 변화를 시간에 따라 살펴봅니다."
)


# ==================================================
# 데이터 불러오기
# ==================================================

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/"
    "modudata/main/data/kobis_daily.csv"
)

try:
    # CSV 파일을 인터넷에서 불러옵니다.
    df = pd.read_csv(DATA_URL)

except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.write(f"오류 내용: {e}")
    st.stop()


# ==================================================
# 데이터 전처리
# ==================================================

# 20250901처럼 되어 있는 날짜를
# 실제 날짜 자료형으로 변환합니다.
df["날짜"] = pd.to_datetime(
    df["날짜"].astype(str),
    format="%Y%m%d"
)

# 숫자로 사용할 열은 숫자형으로 변환합니다.
numeric_columns = [
    "순위",
    "영화코드",
    "일관객",
    "누적관객",
    "스크린수",
    "상영횟수"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

# 날짜순으로 정렬합니다.
df = df.sort_values("날짜")


# ==================================================
# 전체 데이터 정보
# ==================================================

st.info(
    f"📅 데이터 기간: "
    f"{df['날짜'].min().strftime('%Y년 %m월 %d일')} ~ "
    f"{df['날짜'].max().strftime('%Y년 %m월 %d일')} "
    f"| 총 {len(df):,}개의 기록"
)


# ==================================================
# 그래프 구역 1
# ==================================================

st.divider()

st.header("1. 시간에 따른 일관객 변화")

st.write(
    "영화를 하나 선택하면 해당 영화의 "
    "날짜별 일관객 변화를 볼 수 있습니다."
)

# 영화 목록을 가져옵니다.
movie_list = sorted(
    df["영화명"].dropna().unique()
)

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list
)

# 선택한 영화의 데이터만 가져옵니다.
movie_df = df[
    df["영화명"] == selected_movie
].copy()

movie_df = movie_df.sort_values("날짜")


# 첫 번째 그래프
fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie}의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)

fig.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "일관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig.update_layout(
    hovermode="x",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("**이 그래프로 알 수 있는 것**")

st.text_area(
    "첫 번째 그래프에서 발견한 점을 적어 보세요.",
    placeholder=(
        "예: 개봉 직후 관객수가 높고 이후 점차 감소하는 "
        "경향을 확인할 수 있다."
    ),
    height=100,
    key="graph1_note"
)


# ==================================================
# 그래프 구역 2
# ==================================================

st.divider()

st.header("2. 일관객 합계가 가장 큰 영화 5편의 변화")

st.write(
    "전체 기간 동안의 일관객 합계를 기준으로 "
    "관객수가 가장 많았던 5편의 날짜별 변화를 비교합니다."
)


# 영화별 전체 기간 일관객 합계
movie_total = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values(
        "일관객",
        ascending=False
    )
)

top5_movies = movie_total.head(5)["영화명"].tolist()


# 상위 5편의 데이터
top5_df = df[
    df["영화명"].isin(top5_movies)
].copy()

top5_df = top5_df.sort_values(
    ["날짜", "영화명"]
)


# 두 번째 그래프
fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 상위 5편의 날짜별 일관객",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    }
)

fig2.update_traces(
    hovertemplate=(
        "영화: %{fullData.name}<br>"
        "날짜: %{x|%Y-%m-%d}<br>"
        "일관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    hovermode="x unified",
    height=600,
    legend_title_text="영화"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown("**이 그래프로 알 수 있는 것**")

st.text_area(
    "두 번째 그래프에서 발견한 점을 적어 보세요.",
    placeholder=(
        "예: 영화마다 개봉 이후 관객수가 증가하고 감소하는 "
        "시점과 정도가 서로 다르다는 것을 알 수 있다."
    ),
    height=100,
    key="graph2_note"
)


# ==================================================
# 그래프 구역 3
# ==================================================

st.divider()

st.header("3. 날짜별 10위권 전체 일관객")

st.write(
    "각 날짜의 박스오피스 10위권 영화들의 일관객을 "
    "모두 합산하여 전체적인 영화 관람 규모의 변화를 살펴봅니다."
)


# 날짜별 10위권 일관객 합계
daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
)

daily_total = daily_total.sort_values("날짜")


# 일관객 합계가 가장 큰 3일
top3_days = (
    daily_total
    .nlargest(3, "일관객")
    .sort_values("날짜")
)


# 세 번째 그래프
fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 박스오피스 10위권 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계"
    }
)

fig3.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "10위권 일관객 합계: %{y:,}명"
        "<extra></extra>"
    )
)


# 합계가 가장 큰 3일을 그래프에 표시합니다.
for _, row in top3_days.iterrows():

    date_text = row["날짜"].strftime("%m/%d")

    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=(
            f"{date_text}<br>"
            f"{row['일관객']:,}명"
        ),
        showarrow=True,
        arrowhead=2,
        yshift=10
    )

fig3.update_layout(
    hovermode="x",
    height=600
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.markdown("**이 그래프로 알 수 있는 것**")

st.text_area(
    "세 번째 그래프에서 발견한 점을 적어 보세요.",
    placeholder=(
        "예: 특정 날짜에 10위권 영화의 관객수가 "
        "전체적으로 크게 증가한 것을 확인할 수 있다."
    ),
    height=100,
    key="graph3_note"
)


# ==================================================
# 그래프 구역 4
# ==================================================

st.divider()

st.header("4. 기간 전체 일관객 TOP 10")

st.write(
    "이 기간 동안 일관객의 합계가 가장 큰 영화 10편을 "
    "비교합니다."
)


# --------------------------------------------------
# 영화별 일관객 합계 계산
# --------------------------------------------------

movie_summary = (
    df.groupby("영화명")
    .agg(
        일관객합계=("일관객", "sum"),
        기간내_10위권_일수=("영화명", "size")
    )
    .reset_index()
)


# 일관객 합계가 큰 순서대로 정렬하고 TOP 10을 선택합니다.
top10_movies = (
    movie_summary
    .sort_values(
        "일관객합계",
        ascending=False
    )
    .head(10)
    .copy()
)


# 그래프에서 위쪽에 관객이 많은 영화가 오도록
# 순서를 뒤집습니다.
top10_movies = top10_movies.sort_values(
    "일관객합계",
    ascending=True
)


# --------------------------------------------------
# 네 번째 그래프
# --------------------------------------------------

fig4 = px.bar(
    top10_movies,
    x="일관객합계",
    y="영화명",
    orientation="h",
    title="기간 전체 일관객 TOP 10",
    labels={
        "일관객합계": "기간 전체 일관객 합계",
        "영화명": "영화"
    },
    custom_data=["기간내_10위권_일수"]
)


# 마우스를 올리면 일관객 합계와
# 10위권에 든 날수를 함께 보여 줍니다.
fig4.update_traces(
    hovertemplate=(
        "영화: %{y}<br>"
        "일관객 합계: %{x:,}명<br>"
        "10위권에 든 날: %{customdata[0]}일"
        "<extra></extra>"
    )
)

fig4.update_layout(
    height=600
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.markdown("**이 그래프로 알 수 있는 것**")

st.text_area(
    "네 번째 그래프에서 발견한 점을 적어 보세요.",
    placeholder=(
        "예: 기간 전체 관객수가 많은 영화와 "
        "10위권에 오래 머문 영화의 관계를 살펴볼 수 있다."
    ),
    height=100,
    key="graph4_note"
)


# ==================================================
# 그래프 구역 5
# ==================================================

st.divider()

st.header("5. 월 × 요일별 일관객 합계")

st.write(
    "날짜에서 월과 요일을 뽑아, "
    "각 월의 각 요일에 발생한 일관객 합계를 비교합니다."
)


# --------------------------------------------------
# 월과 요일 정보 만들기
# --------------------------------------------------

# 월을 숫자로 저장합니다.
df["월"] = df["날짜"].dt.month

# 요일 번호를 가져옵니다.
# 월요일=0, 화요일=1, ... 일요일=6입니다.
df["요일번호"] = df["날짜"].dt.dayofweek

# 히트맵에 표시할 한글 요일 이름입니다.
weekday_names = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

df["요일"] = df["요일번호"].map(
    dict(enumerate(weekday_names))
)


# --------------------------------------------------
# 월 × 요일별 일관객 합계 계산
# --------------------------------------------------

heatmap_data = (
    df.groupby(
        ["월", "요일번호", "요일"],
        as_index=False
    )["일관객"]
    .sum()
)


# --------------------------------------------------
# 히트맵용 표 만들기
# --------------------------------------------------

heatmap_pivot = heatmap_data.pivot(
    index="월",
    columns="요일",
    values="일관객"
)


# 요일 순서를 월요일 → 일요일로 고정합니다.
heatmap_pivot = heatmap_pivot.reindex(
    columns=weekday_names
)


# 월 순서도 1월 → 12월로 정렬합니다.
heatmap_pivot = heatmap_pivot.sort_index()


# --------------------------------------------------
# 다섯 번째 그래프
# --------------------------------------------------

fig5 = px.imshow(
    heatmap_pivot,
    labels={
        "x": "요일",
        "y": "월",
        "color": "일관객 합계"
    },
    x=weekday_names,
    y=heatmap_pivot.index,
    text_auto=".2s",
    aspect="auto",
    title="월 × 요일별 10위권 일관객 합계",
    color_continuous_scale="Blues"
)


# 마우스를 올렸을 때 자세한 값을 표시합니다.
fig5.update_traces(
    hovertemplate=(
        "%{y}월 %{x}<br>"
        "일관객 합계: %{z:,}명"
        "<extra></extra>"
    )
)


fig5.update_layout(
    height=600,
    xaxis_title="요일",
    yaxis_title="월"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)


# --------------------------------------------------
# 다섯 번째 그래프 해석 공간
# --------------------------------------------------

st.markdown("**이 그래프로 알 수 있는 것**")

st.text_area(
    "다섯 번째 그래프에서 발견한 점을 적어 보세요.",
    placeholder=(
        "예: 특정 월의 주말에 10위권 전체 관객수가 "
        "높게 나타나는 경향을 확인할 수 있다."
    ),
    height=100,
    key="graph5_note"
)


# ==================================================
# 앞으로 그래프를 추가할 공간
# ==================================================

st.divider()

st.header("6. 다음 그래프")

st.info(
    "새로운 데이터 분석 그래프를 추가할 공간입니다."
)

st.markdown("**이 그래프로 알 수 있는 것**")

st.text_area(
    "여섯 번째 그래프에서 발견한 점을 적어 보세요.",
    placeholder="새로운 그래프를 추가한 뒤 내용을 적어 보세요.",
    height=100,
    key="graph6_note"
)


# ==================================================
# 데이터 출처
# ==================================================

st.divider()

st.caption(
    "데이터 출처: 영화관입장권통합전산망(KOBIS) "
    "일일 박스오피스 데이터"
)
