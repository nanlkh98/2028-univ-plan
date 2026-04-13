import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# 2. PDF를 다운로드 버튼과 함께 화면에 띄우는 함수
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    
    # [기능 1] 원본 파일 다운로드 버튼 (누르면 바로 저장됨)
    st.download_button(
        label="📥 이 PDF 파일 다운로드하기",
        data=bytes_data,
        file_name=os.path.basename(file_path),
        mime="application/pdf",
        key=f"download_{os.path.basename(file_path)}"
    )

    # [기능 2] PDF 바로 보기 (화면에서 스크롤하며 보기)
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    # 브라우저 보안 정책에 따라 보이지 않을 수도 있으나, 최대한 시도하는 코드입니다.
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="900" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# 메인 화면 구성
st.title("🎓 2028 대학별 대입전형계획 아카이브")
st.write("대학을 선택하면 아래에서 바로 확인하거나 다운로드할 수 있습니다.")

pdf_folder = "pdfs"

if os.path.exists(pdf_folder):
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    
    if pdf_files:
        selected_file = st.selectbox("🔍 대학을 선택하세요", ["선택하세요"] + pdf_files)
        
        if selected_file != "선택하세요":
            st.divider() # 구분선
            target_path = os.path.join(pdf_folder, selected_file)
            
            # 왼쪽과 오른쪽으로 나누어 보기 (왼쪽은 PDF, 오른쪽은 안내)
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"📄 {selected_file} 미리보기")
                display_pdf(target_path)
            
            with col2:
                st.info("💡 **이용 안내**\n\n왼쪽의 미리보기가 보이지 않는 경우, 상단의 '다운로드' 버튼을 눌러 파일을 확인해 주세요.")
    else:
        st.warning("pdfs 폴더에 PDF 파일이 없습니다.")
else:
    st.error("pdfs 폴더를 찾을 수 없습니다.")
