import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# 2. 데이터 로드 함수 (최신 버전 호환)
@st.cache_data(ttl=5)
def load_excel_data():
    file_path = 'data.xlsx'
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            df.columns = [str(col).strip() for col in df.columns]
            try:
                df = df.map(lambda x: str(x).strip() if isinstance(x, str) else x)
            except AttributeError:
                df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)
            return df
        except Exception as e:
            st.error(f"엑셀 읽기 오류: {e}")
            return None
    return None

def display_pdf(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    
    # PDF를 웹에서 읽을 수 있도록 인코딩
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    
    # 1. 다운로드 버튼 (안전장치)
    st.download_button(
        label="📥 원본 PDF 다운로드", 
        data=bytes_data, 
        file_name=os.path.basename(file_path),
        mime="application/pdf"
    )

    # 2. [가장 중요] 원래 화면에서 바로 보여주는 태그 (iframe 대신 embed 사용)
    # 이 방식이 크롬에서 "차단된 콘텐츠" 메시지를 덜 띄웁니다.
    pdf_display = f'''
        <div style="border: 2px solid #eee; border-radius: 10px; overflow: hidden;">
            <embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf">
        </div>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)

# 메인 제목
st.title("🎓 2028 대학별 대입전형계획 아카이브")

df_all = load_excel_data()
pdf_folder = "pdfs"

if os.path.exists(pdf_folder):
    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')])
    selected_file = st.selectbox("🔍 대학을 선택하세요", ["대학 선택하기"] + pdf_files)

    if selected_file != "대학 선택하기":
        col1, col2 = st.columns([1.5, 1]) # 왼쪽 비율을 조금 더 키웠습니다.
        
        info = None
        if df_all is not None:
            match = df_all[df_all['파일명'] == selected_file]
            if not match.empty:
                info = match.iloc[0]

        with col1:
            st.subheader(f"📄 {selected_file} 원본")
            display_pdf(os.path.join(pdf_folder, selected_file))

        with col2:
            st.subheader("📊 전형 요약 분석")
            if info is not None:
                st.success("데이터를 성공적으로 불러왔습니다.")
                
                # 교과 전형 정보
                st.markdown(f"#### 📍 학생부교과 ({info.get('교과_전형명', '-')})")
                st.table(pd.DataFrame({"항목": ["선발방법", "수능최저"], "내용": [str(info.get('교과_방법', '-')), str(info.get('교과_최저', '-'))]}))

                # 종합 전형 정보
                st.markdown(f"#### 📍 학생부종합 ({info.get('종합_전형명', '-')})")
                st.table(pd.DataFrame({"항목": ["1단계", "2단계", "수능최저"], "내용": [str(info.get('종합_1단계', '-')), str(info.get('종합_2단계', '-')), str(info.get('종합_최저', '-'))]}))
                
                # 비고
                st.info(f"💡 **전문가 분석**\n\n{info.get('비고', '분석 내용이 없습니다.')}")
            else:
                st.error("엑셀 파일에 정보가 없습니다. 파일명이 일치하는지 확인해주세요.")
else:
    st.error("'pdfs' 폴더가 없습니다.")
