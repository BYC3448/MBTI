import streamlit as st
import pandas as pd
import plotly.express as px

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
    # 1. 전 세계 MBTI 평균 비율 (도넛 차트 - 시각적 재미)
    st.header("1. 전 세계 MBTI 분포 🍩")
    st.write("전 세계적으로 어떤 유형이 가장 많을까요? 마우스를 올려 확인해보세요.")
    
    mbti_columns = [col for col in df.columns if col != 'Country']
    avg_mbti = df[mbti_columns].mean().sort_values(ascending=False).reset_index()
    avg_mbti.columns = ['MBTI', 'Percentage']

    # 도넛 차트 (hole 옵션 사용)
    fig1 = px.pie(avg_mbti, values='Percentage', names='MBTI',
                 hole=0.4, # 가운데 구멍 크기 (0~1)
                 color_discrete_sequence=px.colors.qualitative.Pastel, # 부드러운 파스텔 톤
                 title="전 세계 평균 MBTI 구성 비율")
    
    # 텍스트 정보 설정 (퍼센트만 표시하여 깔끔하게)
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # 2. MBTI 유형별 높은 국가 Top 10 (가로형 막대 차트)
    st.header("2. MBTI 유형별 비율이 높은 국가 Top 10 🏆")
    
    col_sel, col_chart = st.columns([1, 3])
    with col_sel:
        selected_mbti = st.selectbox("궁금한 MBTI 유형을 선택하세요:", mbti_columns)
        st.info(f"전 세계에서 {selected_mbti} 유형이 가장 많은 나라는?")

    if selected_mbti:
        top_10 = df[['Country', selected_mbti]].sort_values(by=selected_mbti, ascending=True).tail(10)
        
        fig2 = px.bar(top_10, x=selected_mbti, y='Country',
                     orientation='h',
                     color=selected_mbti,
                     color_continuous_scale='Teal',
                     text_auto='.1f',
                     title=f"{selected_mbti} 비율 상위 10개국")
        fig2.update_layout(xaxis_title="비율(%)", yaxis_title=None)
        
        with col_chart:
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # 3. 한국 vs 다른 국가 비교 (묶음 막대 그래프 - 정확한 비교)
    st.header("3. 한국 vs 다른 국가 성향 비교 🇰🇷")
    st.write("두 나라의 MBTI 비율 차이를 막대 높이로 비교해보세요.")

    country_list = df['Country'].tolist()
    korea_name = 'South Korea'
    
    col_opt, col_view = st.columns([1, 3])
    
    with col_opt:
        default_idx = 0
        if "United States" in country_list:
            default_idx = country_list.index("United States")
        target_country = st.selectbox("비교 대상 국가 선택:", country_list, index=default_idx)

    if korea_name in country_list:
        comp_df = df[df['Country'].isin([korea_name, target_country])].copy()
        comp_long = comp_df.melt(id_vars='Country', value_vars=mbti_columns, 
                                var_name='MBTI', value_name='Percentage')
        
        # 묶음 막대 그래프
        fig3 = px.bar(comp_long, x='MBTI', y='Percentage',
                     color='Country',
                     barmode='group',
                     text_auto='.1f',
                     color_discrete_map={korea_name: '#0052A4', target_country: '#FF5F00'}, # 한국색(파랑) vs 대비색(주황)
                     title=f"{korea_name} vs {target_country} 1:1 정밀 비교")
        
        fig3.update_layout(xaxis_title=None, yaxis_title="비율(%)", legend_title_text='국가')
        
        st.plotly_chart(fig3, use_container_width=True)
