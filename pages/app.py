import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="국가별 MBTI 성향 분석", layout="wide")

st.title("국가별 MBTI 성향 분석 대시보드")

# 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    try:
        # 1. 파일 읽기 (countries.csv)
        df = pd.read_csv('countries.csv')
        
        # 2. 데이터 전처리: -A와 -T로 나뉜 32개 유형을 16개 표준 MBTI로 통합
        mbti_types = [
            'ESTJ', 'ESFJ', 'INFP', 'ENFP', 'ISFJ', 'ENFJ', 'ESTP', 'ISTJ',
            'INTP', 'INFJ', 'ISFP', 'ENTJ', 'ESFP', 'ENTP', 'INTJ', 'ISTP'
        ]
        
        # 결과를 담을 새로운 데이터프레임 생성 (국가명 포함)
        df_processed = df[['Country']].copy()
        
        # 16개 유형별로 -A와 -T 컬럼을 더해서 합산
        for mbti in mbti_types:
            col_a = f"{mbti}-A"
            col_t = f"{mbti}-T"
            
            # 해당 컬럼들이 데이터에 있는지 확인 후 더하기
            if col_a in df.columns and col_t in df.columns:
                # 소수점 데이터(예: 0.12)를 퍼센트(예: 12.0)로 변환하기 위해 100을 곱함
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
    # 1. 전체 국가의 MBTI 평균 비율 분석
    st.header("1. 전 세계 MBTI 평균 비율")
    st.write("전 세계 국가들의 MBTI 데이터를 종합하여 산출한 평균 비율입니다.")

    # MBTI 컬럼만 선택 (Country 제외)
    mbti_columns = [col for col in df.columns if col != 'Country']
    
    # 평균 계산 후 내림차순 정렬
    avg_mbti = df[mbti_columns].mean().sort_values(ascending=False)
    
    # 막대 그래프로 시각화
    st.bar_chart(avg_mbti)
    
    # 상위 3개 유형 텍스트로 안내
    top_3 = avg_mbti.index[:3].tolist()
    st.write(f"전 세계적으로 가장 흔한 유형 Top 3는 **{', '.join(top_3)}** 입니다.")

    st.divider()

    # 2. MBTI 유형별 높은 국가 Top 10
    st.header("2. MBTI 유형별 비율이 높은 국가 Top 10")
    
    selected_mbti = st.selectbox("순위를 보고 싶은 MBTI 유형을 선택하세요:", mbti_columns)

    if selected_mbti:
        # 선택한 유형 기준으로 내림차순 정렬 후 상위 10개 추출
        top_10_countries = df[['Country', selected_mbti]].sort_values(by=selected_mbti, ascending=False).head(10)
        
        # 순위 보기 좋게 인덱스 조정 (1위부터 시작)
        top_10_countries = top_10_countries.reset_index(drop=True)
        top_10_countries.index = top_10_countries.index + 1
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write(f"**{selected_mbti} 비율 상위 10개국**")
            # 퍼센트 포맷 적용
            st.dataframe(top_10_countries.style.format({selected_mbti: "{:.2f}%"}))
        
        with col2:
            chart_data = top_10_countries.set_index('Country')
            st.bar_chart(chart_data)

    st.divider()

    # 3. 한국과 다른 국가 비교 분석
    st.header("3. 한국 vs 다른 국가 MBTI 비교")

    country_list = df['Country'].tolist()
    korea_name = 'South Korea' # 파일에 있는 한국 영문명

    # 비교할 국가 선택 (기본값 설정: 미국)
    default_idx = 0
    if "United States" in country_list:
        default_idx = country_list.index("United States")
        
    target_country = st.selectbox("한국과 비교할 국가를 선택하세요:", country_list, index=default_idx)

    if korea_name not in country_list:
        st.warning(f"데이터에서 '{korea_name}'를 찾을 수 없습니다.")
    else:
        # 데이터 추출 (전치행렬 T 사용)
        korea_data = df[df['Country'] == korea_name][mbti_columns].T
        target_data = df[df['Country'] == target_country][mbti_columns].T
        
        # 비교용 데이터프레임 생성
        comparison_df = pd.DataFrame({
            korea_name: korea_data.iloc[:, 0],
            target_country: target_data.iloc[:, 0]
        })

        st.write(f"**{korea_name}**와 **{target_country}**의 성향 비교")
        
        # 선 그래프로 비교
        st.line_chart(comparison_df)
        
        with st.expander("상세 수치 데이터 표 보기"):
            # 여기가 오류가 났던 부분입니다. 괄호를 확실히 닫았습니다.
            st.dataframe(comparison_df.style.format("{:.2f}%"))
