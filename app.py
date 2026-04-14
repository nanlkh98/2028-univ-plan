import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정 (넓게 보기)
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# 2. 데이터 로드 함수
@st.cache_data(ttl=5)
def load_excel_data():
    file_path = 'data.xlsx'
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            df.columns = [str(col).strip() for col in df.columns]
            df = df.map(lambda x: str(x).strip() if isinstance(x, str) else x)
            return df
        except Exception as e:
            st.error(f"엑셀 로드 오류: {e}")
            return None
    return None

def display_pdf(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    
    # PDF 미리보기 (가장 표준적인 iframe 방식)
    # 만약 여기서 안 보인다면 브라우저 자물쇠 설정이 필요합니다.
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="900" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 메인 화면 ---
st.title("🎓 2028 대학별 대입전형계획 아카이브")

df_all = load_excel_data()
pdf_folder = "pdfs"

if os.path.exists(pdf_folder):
    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')])
    selected_file = st.selectbox("🔍 분석할 대학을 선택하세요", ["대학 선택하기"] + pdf_files)

    if selected_file != "대학 선택하기":
        # 정확히 왼쪽(미리보기)과 오른쪽(분석)으로 나눕니다.
        col1, col2 = st.columns([1.6, 1]) 
        
        info = None
        if df_all is not None:
            match = df_all[df_all['파일명'] == selected_file]
            if not match.empty:
                info = match.iloc[0]

        with col1:
            st.subheader("📄 원본 문서 (미리보기)")
            display_pdf(os.path.join(pdf_folder, selected_file))

        with col2:
            st.subheader("📊 핵심 전형 요약")
            if info is not None:
                st.success(f"✅ {selected_file}")
                
                # 분석 데이터 표로 깔끔하게 정리
                st.markdown("#### **[학생부교과]**")
                st.table(pd.DataFrame({
                    "항목": ["전형명", "선발방법", "수능최저"],
                    "내용": [str(info.get('교과_전형명', '-')), str(info.get('교과_방법', '-')), str(info.get('교과_최저', '-'))]
                }))

                st.markdown("#### **[학생부종합]**")
                st.table(pd.DataFrame({
                    "항목": ["전형명", "1단계", "2단계", "수능최저"],
                    "내용": [str(info.get('종합_전형명', '-')), str(info.get('종합_1단계', '-')), str(info.get('종합_2단계', '-')), str(info.get('종합_최저', '-'))]
                }))
                
                st.info(f"💡 **전문가 한줄 평**\n\n{info.get('비고', '내용 없음')}")
            else:
                st.warning("엑셀에서 분석 데이터를 찾을 수 없습니다.")
else:
    st.error("'pdfs' 폴더가 없습니다.")
