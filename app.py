import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정 (웹 브라우저 탭에 표시될 이름)
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# 2. 데이터 로드 함수
@st.cache_data(ttl=5)
def load_excel_data():
    file_path = 'data.xlsx'
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            # 컬럼명 및 데이터 공백 제거 (오류 방지)
            df.columns = [str(col).strip() for col in df.columns]
            df = df.map(lambda x: str(x).strip() if isinstance(x, str) else x)
            return df
        except Exception as e:
            st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
            return None
    return None

# 3. PDF 표시 함수
def display_pdf(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            bytes_data = f.read()
        
        # 다운로드 버튼 (미리보기가 안 될 때를 대비한 가장 확실한 수단)
        st.download_button(
            label="📥 원본 PDF 다운로드 (클릭하여 보기)", 
            data=bytes_data, 
            file_name=os.path.basename(file_path),
            mime="application/pdf",
            key="pdf_download"
        )
        
        # 미리보기 시도 (보안 환경에 따라 차단될 수 있음)
        base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
        pdf_display = f'''
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 5px;">
                <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>
            </div>
        '''
        st.markdown(pdf_display, unsafe_allow_html=True)
        st.caption("⚠️ 미리보기가 나오지 않으면 위 '다운로드' 버튼을 눌러주세요.")
    else:
        st.warning("PDF 파일을 찾을 수 없습니다.")

# --- 메인 화면 시작 ---
st.title("🎓 2028 대학별 대입전형계획 아카이브")
st.write("대학을 선택하면 원본 문서와 전형 요약 분석을 확인할 수 있습니다.")

df_all = load_excel_data()
pdf_folder = "pdfs"

# PDF 폴더 확인 및 목록 가져오기
if os.path.exists(pdf_folder):
    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')])
    selected_file = st.selectbox("🔍 대학을 선택하세요", ["대학 선택하기"] + pdf_files)

    if selected_file != "대학 선택하기":
        # 화면을 좌우로 분할 (왼쪽 1.5 : 오른쪽 1)
        col1, col2 = st.columns([1.5, 1])
        
        # 엑셀 데이터 매칭
        info = None
        if df_all is not None:
            match = df_all[df_all['파일명'] == selected_file]
            if not match.empty:
                info = match.iloc[0]

        with col1:
            st.subheader("📄 원본 문서 미리보기")
            display_pdf(os.path.join(pdf_folder, selected_file))

        with col2:
            st.subheader("📊 핵심 전형 요약")
            if info is not None:
                st.success(f"✅ {selected_file} 분석 데이터")
                
                # 학생부교과
                st.markdown(f"### 📍 학생부교과\n**({info.get('교과_전형명', '-')})**")
                st.table(pd.DataFrame({
                    "구분": ["선발방법", "수능최저"],
                    "내용": [str(info.get('교과_방법', '-')), str(info.get('교과_최저', '-'))]
                }))

                # 학생부종합
                st.markdown(f"### 📍 학생부종합\n**({info.get('종합_전형명', '-')})**")
                st.table(pd.DataFrame({
                    "단계": ["1단계", "2단계", "수능최저"],
                    "내용": [str(info.get('종합_1단계', '-')), str(info.get('종합_2단계', '-')), str(info.get('종합_최저', '-'))]
                }))
                
                # 비고/전문가 분석
                st.info(f"💡 **전문가 분석 요약**\n\n{info.get('비고', '분석 데이터가 없습니다.')}")
            else:
                st.warning("⚠️ 엑셀 파일에 해당 대학의 분석 정보가 없습니다. 파일명이 엑셀의 '파일명' 칸과 일치하는지 확인해주세요.")
else:
    st.error("'pdfs' 폴더가 존재하지 않습니다. GitHub 저장소 구성을 확인해주세요.")
