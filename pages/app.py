import streamlit as st
import pandas as pd
import altair as alt

# 페이지 기본 설정
st.set_page_config(page_title="국가별 MBTI 성향 분석", layout="wide")

st.title("🌏 국가별 MBTI 성향 분석 대시보드")
st.markdown("---")

# 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('countries.csv')
        
        mbti_types = [
            'ESTJ', 'ESFJ', 'INFP', 'ENFP', 'ISFJ', 'ENFJ', 'ESTP', 'ISTJ',
            'INTP', 'INFJ', 'ISFP', 'ENTJ', 'ESFP', 'ENTP', 'INTJ', 'ISTP'
        ]
        
        df_processed = df[['Country']].copy()
        
        for mbti in mbti_types:
            col_a = f"{mbti}-A"
            col_t = f"{mbti}-T"
            
            if col_a in df.columns and col_t in df.columns:
                df_processed[mbti] = (df[col_a] + df[col_t]) * 100
        
        return df_processed
        
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        return None

df = load_data()

if df is None:
    st.error("데이터 파일을 찾을 수 없습니다. 같은 폴더에 'countries.csv' 파일이 있는지 확인해주세요.")
else:
    # 1. 전 세계 MBTI 평균 비율 (도넛 차트 - Altair 사용)
    st.header("1. 전 세계 MBTI 분포 🍩")
    st.write("전 세계적으로 가장 흔한 MBTI 유형 비율입니다.")
    
    mbti_columns = [col for col in df.columns if col != 'Country']
    avg_mbti = df[mbti_columns].mean().sort_values(ascending=False).reset_index()
    avg_mbti.columns = ['MBTI', 'Percentage']

    # Altair로 도넛 차트 구현
    base = alt.Chart(avg_mbti).encode(
        theta=alt.Theta("Percentage", stack=True)
    )
    
    pie = base.mark_arc(innerRadius=60).encode(
        color=alt.Color("MBTI", scale=alt.Scale(scheme="category20"), legend=None),
        order=alt.Order("Percentage", sort="descending"),
        tooltip=["MBTI", alt.Tooltip("Percentage", format=".1f")]
    )
    
    text = base.mark_text(radius=140).encode(
        text=alt.Text("Percentage", format=".1f"),
        order=alt.Order("Percentage", sort="descending"),
        color=alt.value("black")  
    )
    
    st.altair_chart(pie + text, use_container_width=True)
    
    # 범례 별도 표시
    top_3 = avg_mbti.iloc[:3]['MBTI'].tolist()
    st.info(f"💡 가장 많은 유형 Top 3: {', '.join(top_3)}")

    st.divider()

    # 2. MBTI 유형별 높은 국가 Top 10
    st.header("2. MBTI 유형별 비율이 높은 국가 Top 10 🏆")
    
    col_sel, col_chart = st.columns([1, 3])
    with col_sel:
        selected_mbti = st.selectbox("MBTI 유형 선택:", mbti_columns)

    if selected_mbti:
        top_10 = df[['Country', selected_mbti]].sort_values(by=selected_mbti, ascending=True).tail(10)
        
        # 가로 막대 차트
        chart = alt.Chart(top_10).mark_bar().encode(
            x=alt.X(f"{selected_mbti}:Q", title="비율(%)"),
            y=alt.Y("Country:N", sort="-x", title=None),
            color=alt.Color(f"{selected_mbti}:Q", scale=alt.Scale(scheme="tealblues"), legend=None),
            tooltip=["Country", alt.Tooltip(f"{selected_mbti}", format=".1f")]
        ).properties(
            title=f"{selected_mbti} 비율 상위 10개국"
        )
        
        with col_chart:
            st.altair_chart(chart, use_container_width=True)

    st.divider()

    # 3. 한국 vs 다른 국가 비교 (묶음 막대)
    st.header("3. 한국 vs 다른 국가 성향 비교 🇰🇷")
    
    country_list = df['Country'].tolist()
    korea_name = 'South Korea'
    
    col_opt, col_view = st.columns([1, 3])
    
    with col_opt:
        default_idx = 0
        if "United States" in country_list:
            default_idx = country_list.index("United States")
        target_country = st.selectbox("비교 대상 국가:", country_list, index=default_idx)

    if korea_name in country_list:
        comp_df = df[df['Country'].isin([korea_name, target_country])].copy()
        # Altair에서 그룹 막대를 그리기 위한 데이터 변환
        comp_long = comp_df.melt(id_vars='Country', value_vars=mbti_columns, 
                                var_name='MBTI', value_name='Percentage')
        
        # 그룹 막대 차트 (xOffset 활용)
        chart_compare = alt.Chart(comp_long).mark_bar().encode(
            x=alt.X('MBTI:N', axis=alt.Axis(title=None, labelAngle=0)),
            y=alt.Y('Percentage:Q', title='비율(%)'),
            color=alt.Color('Country:N', scale=alt.Scale(domain=[korea_name, target_country], range=['#1f77b4', '#ff7f0e'])),
            xOffset=alt.XOffset('Country:N'), # 막대를 겹치지 않고 나란히 배치
            tooltip=['Country', 'MBTI', alt.Tooltip('Percentage', format='.1f')]
        ).properties(
            title=f"{korea_name} vs {target_country} 1:1 비교"
        ).configure_legend(
            title=None, orient='top'
        )
        
        st.altair_chart(chart_compare, use_container_width=True)
