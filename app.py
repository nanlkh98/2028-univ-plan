import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정 (웹 브라우저 탭 이름과 넓이 설정)
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# 2. 데이터 로드 함수 (엑셀 파일을 읽어오는 핵심 기능)
@st.cache_data(ttl=5)
def load_excel_data():
    file_path = 'data.xlsx'
    if os.path.exists(file_path):
        try:
            # 엑셀 읽기
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # 모든 열 이름의 공백 제거 (예: '파일명 ' -> '파일명')
            df.columns = [str(col).strip() for col in df.columns]
            
            # 데이터 내용의 공백 제거 (최신 버전과 구버전 모두 호환되도록 처리)
            try:
                df = df.map(lambda x: str(x).strip() if isinstance(x, str) else x)
            except AttributeError:
                df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)
                
            return df
        except Exception as e:
            st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
            return None
    else:
        st.warning("⚠️ 'data.xlsx' 파일이 폴더에 없습니다.")
        return None

# 데이터 불러오기 실행
df_all = load_excel_data()

# 3. PDF 화면 출력 함수
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    
    # 다운로드 버튼
    st.download_button(
        label="📥 원본 PDF 다운로드", 
        data=bytes_data, 
        file_name=os.path.basename(file_path),
        mime="application/pdf"
    )
    
    # PDF 미리보기 화면 생성
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# 4. 메인 화면 구성
st.title("🎓 2028 대학별 대입전형계획 아카이브")

pdf_folder = "pdfs"
if os.path.exists(pdf_folder):
    # pdfs 폴더 내의 파일 목록 가져오기
    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')])
    selected_file = st.selectbox("🔍 대학을 선택하세요", ["대학 선택하기"] + pdf_files)

    if selected_file != "대학 선택하기":
        # 화면을 왼쪽(미리보기)과 오른쪽(분석표)으로 나눔
        col1, col2 = st.columns([1.2, 1])
        
        info = None
        if df_all is not None:
            # 선택한 파일명과 엑셀의 '파일명' 열을 비교해서 해당 줄 찾기
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
                
                # 학생부교과 표
                st.markdown(f"#### 📍 학생부교과 ({info.get('교과_전형명', '-')})")
                교과_df = pd.DataFrame({
                    "구분": ["선발방법", "수능최저"],
                    "내용": [str(info.get('교과_방법', '-')), str(info.get('교과_최저', '-'))]
                })
                st.table(교과_df)

                # 학생부종합 표
                st.markdown(f"#### 📍 학생부종합 ({info.get('종합_전형명', '-')})")
                종합_df = pd.DataFrame({
                    "항목": ["1단계", "2단계", "수능최저"],
                    "내용": [str(info.get('종합_1단계', '-')), str(info.get('종합_2단계', '-')), str(info.get('종합_최저', '-'))]
                })
                st.table(종합_df)
                
                # 비고/전문가 분석
                st.info(f"💡 **전문가 분석**\n\n{info.get('비고', '분석 내용이 없습니다.')}")
            else:
                st.error(f"❌ 엑셀 파일에서 '{selected_file}'과 일치하는 행을 찾을 수 없습니다.")
                st.write("💡 **해결 방법:** 엑셀 파일의 '파일명' 칸에 확장자(.pdf)까지 포함된 전체 이름이 있는지 확인하세요.")
else:
    st.error("⚠️ 'pdfs' 폴더가 존재하지 않습니다.")
