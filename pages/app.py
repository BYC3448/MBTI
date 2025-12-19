import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="국가별 MBTI 성향 분석", layout="wide")

st.title("국가별 MBTI 성향 분석 대시보드")

# 데이터 로드 함수
@st.cache_data
def load_data():
    # 같은 폴더에 있는 mbti_data.csv 파일을 읽어옵니다.
    # 파일이 없을 경우를 대비해 예외 처리를 합니다.
    try:
        df = pd.read_csv('mbti_data.csv')
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("데이터 파일을 찾을 수 없습니다. 같은 폴더에 'mbti_data.csv' 파일이 있는지 확인해주세요.")
else:
    # 데이터가 정상적으로 로드되었을 때 실행되는 영역입니다.
    
    # 1. 전체 국가의 MBTI 평균 비율 분석
    st.header("1. 전 세계 MBTI 평균 비율")
    st.write("전체 국가 데이터를 바탕으로 산출한 각 MBTI 유형별 평균 비율입니다.")

    # 숫자 데이터만 추출하여 평균 계산 (국가명 컬럼 제외)
    # Country 컬럼이 있으면 제외하고 나머지(MBTI 유형)만 선택
    if 'Country' in df.columns:
        mbti_columns = [col for col in df.columns if col != 'Country']
        # 평균 계산 후 내림차순 정렬
        avg_mbti = df[mbti_columns].mean().sort_values(ascending=False)
        
        # 막대 그래프로 시각화
        st.bar_chart(avg_mbti)
        
        # 상위 3개 유형 텍스트로 안내
        top_3 = avg_mbti.index[:3].tolist()
        st.write(f"전 세계적으로 가장 비율이 높은 유형 Top 3는 {', '.join(top_3)} 입니다.")

    st.divider()

    # 2. MBTI 유형별 높은 국가 Top 10
    st.header("2. MBTI 유형별 비율이 높은 국가 Top 10")
    
    # 분석할 MBTI 유형 선택 박스
    selected_mbti = st.selectbox("분석하고 싶은 MBTI 유형을 선택하세요:", mbti_columns)

    if selected_mbti:
        # 선택한 유형 기준으로 내림차순 정렬 후 상위 10개 추출
        top_10_countries = df[['Country', selected_mbti]].sort_values(by=selected_mbti, ascending=False).head(10)
        
        # 인덱스 재설정 (순위 보기 좋게 1위부터 시작하도록)
        top_10_countries = top_10_countries.reset_index(drop=True)
        top_10_countries.index = top_10_countries.index + 1
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(top_10_countries)
        
        with col2:
            # 시각화를 위해 국가명을 인덱스로 설정
            chart_data = top_10_countries.set_index('Country')
            st.bar_chart(chart_data)

    st.divider()

    # 3. 한국과 다른 국가 비교 분석
    st.header("3. 한국 vs 다른 국가 MBTI 비교")

    # 국가 리스트 생성
    country_list = df['Country'].tolist()

    # 한국이 데이터에 있는지 확인하고 기본값
