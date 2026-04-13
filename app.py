import streamlit as st
import pandas as pd
import base64
import os
import time

# 1. 페이지 설정
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# --- 💡 [구글 시트 연동 설정] ---
SHEET_ID = '1UvZhUkQNGp2PNMkqt17OCC1JBZ7K_5RDEe2yvrMfYBA' 
# 캐시 방지를 위한 타임스탬프 추가
timestamp = int(time.time())
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&cache_bust={timestamp}'

@st.cache_data(ttl=5)
def load_gsheet_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # 중요: 모든 열 이름에서 공백을 완전히 제거하고 깨끗하게 만듭니다.
        df.columns = [str(col).strip() for col in df.columns]
        # 데이터 내용에서도 앞뒤 공백을 제거합니다.
        df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"구글 시트를 불러오지 못했습니다. (에러내용: {e})")
        return None

df_all = load_gsheet_data()

def display_pdf(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    st.download_button(label="📥 원본 PDF 다운로드", data=bytes_data, file_name=os.path.basename(file_path), mime="application/pdf")
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.title("🎓 2028 대학별 대입전형계획 아카이브")

pdf_folder = "pdfs"
if os.path.exists(pdf_folder):
    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')])
    selected_file = st.selectbox("🔍 대학을 선택하세요", ["대학 선택하기"] + pdf_files)

    if selected_file != "대학 선택하기":
        col1, col2 = st.columns([1.2, 1])
        
        info = None
        if df_all is not None:
            # 💡 [핵심 수정] '파일명' 열을 찾을 때 더 유연하게 매칭합니다.
            col_name = '파일명'
            if col_name in df_all.columns:
                match = df_all[df_all[col_name] == selected_file.strip()]
                if not match.empty:
                    info = match.iloc[0]

        with col1:
            st.subheader(f"📄 원본 미리보기")
            display_pdf(os.path.join(pdf_folder, selected_file))

        with col2:
            st.subheader(f"📊 전형 요약 분석")
            
            if info is not None:
                # 데이터 표시 (오류 방지를 위해 get 사용)
                st.markdown(f"#### 📍 학생부교과 ({info.get('교과_전형명', '-')})")
                st.table(pd.DataFrame({
                    "구분": ["선발 방법", "수능 최저"],
                    "내용": [str(info.get('교과_방법', '-')), str(info.get('교과_최저', '-'))]
                }))

                st.markdown(f"#### 📍 학생부종합 ({info.get('종합_전형명', '-')})")
                st.table(pd.DataFrame({
                    "항목": ["1단계", "2단계", "최저"],
                    "내용": [str(info.get('종합_1단계', '-')), str(info.get('종합_2단계', '-')), str(info.get('종합_최저', '-'))]
                }))
                st.info(f"💡 **전문가 분석**\n\n{info.get('비고', '-')}")
            else:
                st.warning(f"⚠️ '{selected_file}' 정보를 시트에서 찾을 수 없습니다.")
                if df_all is not None:
                    st.write("**현재 시트에서 인식된 항목(제목) 목록:**")
                    st.write(list(df_all.columns))
                    st.write("**현재 시트에 입력된 파일명 목록:**")
                    st.write(df_all.iloc[:, 0].tolist()) # 첫 번째 열의 데이터를 보여줌
