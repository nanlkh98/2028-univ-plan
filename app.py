import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# --- 💡 [구글 시트 연동 설정] ---
SHEET_ID = '1UvZhUkQNGp2PNMkqt17OCC1JBZ7K_5RDEe2yvrMfYBA' 
# tqx=out:csv 뒤에 임의의 숫자를 붙여 구글이 캐시된 데이터를 주지 못하게 방해합니다.
import time
timestamp = int(time.time())
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&cache_bust={timestamp}'

@st.cache_data(ttl=5) # 5초마다 새로 확인 (매우 짧게 설정)
def load_gsheet_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # 중요: 열 이름과 데이터에서 눈에 안 보이는 공백을 싹 제거합니다.
        df.columns = [str(col).strip() for col in df.columns]
        df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"구글 시트를 읽지 못했습니다: {e}")
        return None

df_all = load_gsheet_data()

# (display_pdf 함수는 동일하므로 생략하거나 그대로 두시면 됩니다)
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
            # 선택한 파일명과 시트의 '파일명' 칸을 공백 없이 정밀 비교합니다.
            match = df_all[df_all['파일명'] == selected_file.strip()]
            if not match.empty:
                info = match.iloc[0]

        with col1:
            st.subheader(f"📄 원본 미리보기")
            display_pdf(os.path.join(pdf_folder, selected_file))

        with col2:
            st.subheader(f"📊 전형 요약 분석")
            
            if info is not None:
                # 데이터가 있을 때만 표 출력
                st.markdown(f"#### 📍 학생부교과 ({info.get('교과_전형명', '-')})")
                st.table(pd.DataFrame({"구분": ["방법", "최저"], "내용": [str(info.get('교과_방법', '-')), str(info.get('교과_최저', '-'))]}))

                st.markdown(f"#### 📍 학생부종합 ({info.get('종합_전형명', '-')})")
                st.table(pd.DataFrame({"항목": ["1단계", "2단계", "최저"], "내용": [str(info.get('종합_1단계', '-')), str(info.get('종합_2단계', '-')), str(info.get('종합_최저', '-'))]}))
                st.info(f"💡 **전문가 분석**\n\n{info.get('비고', '-')}")
            else:
                # 만약 데이터를 못 찾으면 시트에 있는 파일명들을 다 보여줍니다.
                st.warning(f"⚠️ '{selected_file}' 정보를 시트에서 찾을 수 없습니다.")
                if df_all is not None:
                    st.write("**현재 시트에 입력된 파일명 목록 (확인용):**")
                    st.write(df_all['파일명'].tolist())
