import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# --- 💡 [구글 시트 연동 설정] ---
SHEET_ID = '1UvZhUkQNGp2PNMkqt17OCC1JBZ7K_5RDEe2yvrMfYBA' 
# export?format=csv 뒤에 시트 이름을 명시하지 않아도 되지만, 확실히 하기 위해 형식을 고정합니다.
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv'

@st.cache_data(ttl=10) # 테스트를 위해 새로고침 간격을 10초로 줄였습니다.
def load_gsheet_data():
    try:
        # 데이터 로드 시 제목 줄이 섞이지 않도록 명시적 로드
        df = pd.read_csv(SHEET_URL)
        # 모든 열 이름의 앞뒤 공백 제거 및 문자열 변환
        df.columns = [str(col).strip() for col in df.columns]
        # 모든 데이터 내용의 앞뒤 공백 제거
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"구글 시트를 불러오지 못했습니다. 공유 설정을 확인하세요: {e}")
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
        
        # 데이터 매칭 로직 강화
        info = None
        if df_all is not None:
            # 파일명 열에서 선택된 파일과 일치하는 행 찾기 (대소문자 및 공백 무시)
            match = df_all[df_all['파일명'].astype(str) == selected_file]
            if not match.empty:
                info = match.iloc[0]

        with col1:
            st.subheader(f"📄 원본 미리보기")
            display_pdf(os.path.join(pdf_folder, selected_file))

        with col2:
            st.subheader(f"📊 전형 요약 분석")
            
            if info is not None:
                # 표 출력을 위해 데이터를 사전 형태로 재구성
                try:
                    st.markdown(f"#### 📍 학생부교과 ({info.get('교과_전형명', '정보없음')})")
                    st.table(pd.DataFrame({
                        "구분": ["선발 방법", "수능 최저"],
                        "내용": [str(info.get('교과_방법', '-')), str(info.get('교과_최저', '-'))]
                    }))

                    st.markdown(f"#### 📍 학생부종합 ({info.get('종합_전형명', '정보없음')})")
                    st.table(pd.DataFrame({
                        "단계": ["1단계 (서류)", "2단계 (면접)", "수능 최저"],
                        "내용": [str(info.get('종합_1단계', '-')), str(info.get('종합_2단계', '-')), str(info.get('종합_최저', '-'))]
                    }))
                    
                    st.info(f"💡 **전문가 분석**\n\n{info.get('비고', '분석 내용이 없습니다.')}")
                except Exception as table_err:
                    st.error(f"표를 생성하는 중 오류가 발생했습니다: {table_err}")
            else:
                st.warning(f"⚠️ 구글 시트에 '{selected_file}' 정보가 없습니다.")
                st.info("💡 **파일명이 일치하는지 확인하세요:**")
                if df_all is not None:
                    st.write("현재 시트에 등록된 파일명들:", df_all['파일명'].tolist())
