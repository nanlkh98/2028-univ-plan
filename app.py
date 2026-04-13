import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# --- 💡 [구글 시트 연동 섹션] ---
# 선생님의 구글 시트 주소에서 ID 부분을 여기에 붙여넣으세요
SHEET_ID = 'https://docs.google.com/spreadsheets/d/1UvZhUkQNGp2PNMkqtl7OCC1JBZ7K_5RDEe2yvrMfYBA/edit?gid=0#gid=0' 
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

@st.cache_data(ttl=600) # 10분마다 데이터를 새로고침합니다
def load_gsheet_data():
    try:
        return pd.read_csv(SHEET_URL)
    except Exception as e:
        st.error(f"구글 시트를 불러오지 못했습니다: {e}")
        return None

df_all = load_gsheet_data()
# -----------------------------

def display_pdf(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    st.download_button(label="📥 원본 PDF 다운로드", data=bytes_data, file_name=os.path.basename(file_path), mime="application/pdf")
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.title("🎓 2028 대입전형 아카이브 (구글시트 실시간 연동)")

pdf_folder = "pdfs"
if os.path.exists(pdf_folder):
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    selected_file = st.selectbox("🔍 대학을 선택하세요", ["대학 선택하기"] + pdf_files)

    if selected_file != "대학 선택하기":
        col1, col2 = st.columns([1.2, 1])
        
        info = None
        if df_all is not None:
            # 시트의 '파일명' 열과 실제 선택한 파일명이 일치하는 행 찾기
            row = df_all[df_all['파일명'] == selected_file]
            if not row.empty:
                info = row.iloc[0]

        with col1:
            st.subheader(f"📄 {selected_file} 원본")
            display_pdf(os.path.join(pdf_folder, selected_file))

        with col2:
            st.subheader(f"📊 핵심 요약 (구글시트 기반)")
            
            if info is not None:
                st.markdown(f"#### 📍 학생부교과 ({info['교과_전형명']})")
                st.table(pd.DataFrame({"구분": ["방법", "최저"], "내용": [str(info['교과_방법']), str(info['교과_최저'])]}))

                st.markdown(f"#### 📍 학생부종합 ({info['종합_전형명']})")
                st.table(pd.DataFrame({
                    "항목": ["1단계", "2단계", "최저"],
                    "내용": [str(info['종합_1단계']), str(info['종합_2단계']), str(info['종합_최저'])]
                }))
                st.info(f"💡 **전문가 분석**\n\n{info['비고']}")
            else:
                st.warning("⚠️ 이 대학의 정보는 아직 구글 시트에 입력되지 않았습니다.")
