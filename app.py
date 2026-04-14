import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# 2. 데이터 로드 함수
@st.cache_data(ttl=5)
def load_excel_data():
    file_path = 'data.xlsx'
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            df.columns = [str(col).strip() for col in df.columns]
            # 최신 Pandas 버전 호환용 공백 제거
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
    
    # 파일명을 안전하게 인코딩
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    
    # 1. 다운로드 버튼
    st.download_button(
        label="📥 원본 PDF 다운로드", 
        data=bytes_data, 
        file_name=os.path.basename(file_path),
        mime="application/pdf"
    )

    # 2. [핵심] 새 탭에서 열기 버튼 (크롬 차단을 피하는 가장 확실한 방법)
    # 버튼처럼 보이기 위해 HTML/CSS를 살짝 섞었습니다.
    pdf_link = f'<a href="data:application/pdf;base64,{base64_pdf}" target="_blank" style="text-decoration: none;"><div style="background-color: #ff4b4b; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 20px;">🔍 새 탭에서 큰 화면으로 보기</div></a>'
    st.markdown(pdf_link, unsafe_allow_html=True)
    
    # 3. 미리보기 시도 (차단될 경우 위 버튼을 사용하게 됨)
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# 메인 실행부
st.title("🎓 2028 대학별 대입전형계획 아카이브")

df_all = load_excel_data()
pdf_folder = "pdfs"

if os.path.exists(pdf_folder):
    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')])
    selected_file = st.selectbox("🔍 대학을 선택하세요", ["대학 선택하기"] + pdf_files)

    if selected_file != "대학 선택하기":
        col1, col2 = st.columns([1.2, 1])
        
        info = None
        if df_all is not None:
            match = df_all[df_all['파일명'] == selected_file]
            if not match.empty:
                info = match.iloc[0]

        with col1:
            st.subheader("📄 원본 미리보기")
            display_pdf(os.path.join(pdf_folder, selected_file))

        with col2:
            st.subheader("📊 전형 요약 분석")
            if info is not None:
                st.success(f"✅ {selected_file} 데이터를 불러왔습니다.")
                
                # 교과 전형
                st.markdown(f"#### 📍 학생부교과 ({info.get('교과_전형명', '-')})")
                st.table(pd.DataFrame({"구분": ["선발방법", "수능최저"], "내용": [str(info.get('교과_방법', '-')), str(info.get('교과_최저', '-'))]}))

                # 종합 전형
                st.markdown(f"#### 📍 학생부종합 ({info.get('종합_전형명', '-')})")
                st.table(pd.DataFrame({"항목": ["1단계", "2단계", "수능최저"], "내용": [str(info.get('종합_1단계', '-')), str(info.get('종합_2단계', '-')), str(info.get('종합_최저', '-'))]}))
                
                # 전문가 분석
                st.info(f"💡 **전문가 분석**\n\n{info.get('비고', '분석 내용이 없습니다.')}")
            else:
                st.error("❌ 엑셀에서 정보를 찾을 수 없습니다. 파일명을 확인해주세요.")
else:
    st.error("'pdfs' 폴더를 찾을 수 없습니다.")
