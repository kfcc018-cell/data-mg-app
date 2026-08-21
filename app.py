import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="업무지원요청 데이터 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

st.title("📊 업무지원요청 데이터 시각화 대시보드")
st.markdown("CSV 파일을 업로드하면 요청 현황 및 유형별 통계를 자동으로 시각화합니다.")

# 사이드바: 파일 업로드
st.sidebar.header("📂 파일 업로드")
uploaded_file = st.sidebar.file_uploader("CSV 파일을 선택하세요", type=["csv"])

if uploaded_file is not None:
    # 1. 데이터 로드 및 날짜 데이터 변환
    try:
        df = pd.read_csv(uploaded_file)
        if 'request_date' in df.columns:
            df['request_date'] = pd.to_datetime(df['request_date'])

        st.sidebar.success("파일 업로드 성공!")
        
        # 사이드바: 카테고리 필터
        categories = ["전체"] + list(df['category'].unique()) if 'category' in df.columns else ["전체"]
        selected_category = st.sidebar.selectbox("카테고리 필터", categories)
        
        filtered_df = df if selected_category == "전체" else df[df['category'] == selected_category]

        # 2. 주요 KPI 요약 지표
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 요청 건수", f"{len(filtered_df)}건")
        
        if 'status' in filtered_df.columns:
            completed_cnt = len(filtered_df[filtered_df['status'] == '완료'])
            col2.metric("처리 완료 건수", f"{completed_cnt}건")
            col3.metric("완료율", f"{(completed_cnt / len(filtered_df) * 100):.1f}%" if len(filtered_df) > 0 else "0%")
        
        if 'urgency' in filtered_df.columns:
            urgent_cnt = len(filtered_df[filtered_df['urgency'] == '상'])
            col4.metric("긴급(상) 건수", f"{urgent_cnt}건")

        st.divider()

        # 3. 차트 시각화 (2x2 레이아웃)
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            st.subheader("📌 카테고리별 요청 건수")
            if 'category' in filtered_df.columns:
                cat_counts = filtered_df['category'].value_counts().reset_index()
                cat_counts.columns = ['category', 'count']
                fig_cat = px.bar(cat_counts, x='category', y='count', 
                                 text_auto=True, color='category',
                                 labels={'category': '카테고리', 'count': '건수'})
                fig_cat.update_layout(showlegend=False)
                st.plotly_chart(fig_cat, use_container_width=True)

        with row1_col2:
            st.subheader("🚨 긴급도별 비중")
            if 'urgency' in filtered_df.columns:
                fig_urg = px.pie(filtered_df, names='urgency', hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig_urg, use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            st.subheader("🔄 처리 상태 분포")
            if 'status' in filtered_df.columns:
                fig_status = px.histogram(filtered_df, x='status', color='status', 
                                          text_auto=True)
                fig_status.update_layout(showlegend=False, xaxis_title="상태", yaxis_title="건수")
                st.plotly_chart(fig_status, use_container_width=True)

        with row2_col2:
            st.subheader("🤖 AI 대응 구분")
            if 'ai_handling' in filtered_df.columns:
                ai_counts = filtered_df['ai_handling'].value_counts().reset_index()
                ai_counts.columns = ['ai_handling', 'count']
                fig_ai = px.bar(ai_counts, x='count', y='ai_handling', orientation='h',
                                text_auto=True, color='ai_handling')
                fig_ai.update_layout(showlegend=False, xaxis_title="건수", yaxis_title="AI 처리 여부")
                st.plotly_chart(fig_ai, use_container_width=True)

        # 4. 상세 데이터 테이블 표시
        st.divider()
        st.subheader("📋 업무지원요청 상세 목록")
        st.dataframe(filtered_df, use_container_width=True)

    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")

else:
    st.info("👈 왼쪽 사이드바에서 CSV 파일을 업로드해주세요.")
