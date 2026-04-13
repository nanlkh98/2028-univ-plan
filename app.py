import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# --- 💡 [구글 시트 연동 설정] ---
# 선생님의 시트 ID를 따옴표 안에 정확히 넣어주세요.
SHEET_ID = '1UvZhUkQNGp2PNMkqt17OCC1JBZ7K_5RDEe2yvrMfYBA' 
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

@st.cache_data(ttl=60) # 60초마다 시트 데이터를 새로 확인합니다.
def load_gsheet_data():
    try:
        # 시트를 읽어오고 제목(헤더)의 앞뒤 공백을 제거합니다.
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"구글 시트를 불러오지 못했습니다. 공유 설정을 확인하세요: {e}")
        return None

df_all = load_gsheet_data()

# PDF 미리보기 함수
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    st.download_button(label="📥 원본 PDF 다운로드", data=bytes_data, file_name=os.path.basename(file_path), mime="application/pdf")
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# 메인 화면
st.title("🎓 2028 대학별 대입전형계획 아카이브")

pdf_folder = "pdfs"
if os.path.exists(pdf_folder):
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    selected_file = st.selectbox("🔍 대학을 선택하세요", ["대학 선택하기"] + pdf_files)

    if selected_file != "대학 선택하기":
        col1, col2 = st.columns([1.2, 1])
        
        # 선택한 대학의 행 찾기
        info = None
        if df_all is not None:
            # 시트의 '파일명' 열과 실제 파일명을 매칭합니다.
            row = df_all[df_all['파일명'] == selected_file]
            if not row.empty:
                info = row.iloc[0]

        with col1:
            st.subheader(f"📄 {selected_file} 원본")
            display_pdf(os.path.join(pdf_folder, selected_file))

        with col2:
            st.subheader(f"📊 핵심 요약 분석")
            
            if info is not None:
                # 1. 학생부교과 표
                st.markdown(f"#### 📍 학생부교과 ({info['교과_전형명']})")
                df_k = pd.DataFrame({
                    "구분": ["선발 방법", "수능 최저"],
                    "상세 내용": [str(info['교과_방법']), str(info['교과_최저'])]
                })
                st.table(df_k)

                # 2. 학생부종합 표
                st.markdown(f"#### 📍 학생부종합 ({info['종합_전형명']})")
                df_j = pd.DataFrame({
                    "단계": ["1단계 (서류)", "2단계 (면접 등)", "수능 최저"],
                    "상세 비중": [str(info['종합_1단계']), str(info['종합_2단계']), str(info['종합_최저'])]
                })
                st.table(df_j)
                
                # 3. 비고란
                st.info(f"💡 **전문가 분석 및 전략**\n\n{info['비고']}")
            else:
                st.warning(f"⚠️ 구글 시트에 '{selected_file}'에 대한 정보가 없습니다. 파일명이 시트와 일치하는지 확인해 주세요.")
                st.write("---")
                st.write("**[참고] 현재 시트의 파일명 목록:**")
                st.write(df_all['파일명'].tolist() if df_all is not None else "데이터 없음")
