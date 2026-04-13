import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정 (웹사이트 탭 이름과 넓은 화면 모드)
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# 2. PDF를 화면에 안전하게 띄우기 위한 함수
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    
    # [보안 대책] 브라우저가 미리보기를 차단할 경우를 대비해 다운로드 버튼을 항상 노출합니다.
    st.download_button(
        label="📥 원본 PDF 다운로드 (미리보기가 안 보일 때 클릭)",
        data=bytes_data,
        file_name=os.path.basename(file_path),
        mime="application/pdf"
    )

    # PDF 데이터를 웹 브라우저가 읽을 수 있는 형태로 변환
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    
    # iframe과 embed 방식을 혼합하여 브라우저 호환성을 높임
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# 3. 메인 화면 타이틀
st.title("🎓 2028 대학별 대입전형계획 아카이브 및 분석")
st.info("왼쪽 상단 메뉴에서 대학을 선택하세요. 원본 PDF와 핵심 요약표가 함께 나타납니다.")

# 4. 파일 목록 불러오기 (pdfs 폴더 기준)
pdf_folder = "pdfs"

if not os.path.exists(pdf_folder):
    st.error(f"⚠️ '{pdf_folder}' 폴더가 없습니다. 깃허브에 폴더를 만들고 PDF를 넣어주세요.")
else:
    # 폴더 내 PDF 파일들만 가져오기
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]

    if not pdf_files:
        st.warning("📂 pdfs 폴더 안에 PDF 파일이 없습니다.")
    else:
        # 대학 선택 드롭다운 메뉴
        selected_file = st.selectbox("🔍 분석할 대학교를 선택하세요", ["대학 선택하기"] + pdf_files)

        if selected_file != "대학 선택하기":
            # 화면을 왼쪽(원본)과 오른쪽(분석)으로 나눔
            col1, col2 = st.columns([1, 1.2])
            target_path = os.path.join(pdf_folder, selected_file)

            # --- 왼쪽: PDF 원본 보여주기 ---
            with col1:
                st.subheader(f"📄 {selected_file} 원본")
                display_pdf(target_path)

            # --- 오른쪽: 핵심 분석 정보 보여주기 ---
            with col2:
                st.subheader(f"🔍 {selected_file} 핵심 요약")
                
                # 가상의 분석 데이터 (실제 데이터로 나중에 수정 가능)
                st.markdown("#### ✅ [학생부교과전형]")
                df_subject = pd.DataFrame({
                    "구분": ["일반전형", "지역인재"],
                    "방법": ["교과 100%", "교과 80%+출결 20%"],
                    "수능최저": ["3합 7", "2합 6"]
                })
                st.table(df_subject)

                st.markdown("#### ✅ [학생부종합전형]")
                df_comprehensive = pd.DataFrame({
                    "구분": ["서류형", "면접형"],
                    "평가요소": ["서류 100%", "1단:서류 / 2단:면접"],
                    "최저기준": ["미적용", "일부 적용"]
                })
                st.table(df_comprehensive)

                # 전문가 코멘트 (Expander 사용)
                with st.expander("💡 2028 대입 전형 핵심 전략 코멘트"):
                    st.write(f"""
                    **[{selected_file} 분석 의견]**
                    1. 본 대학은 2028 대입 개편에 맞춰 통합수능 과목을 반영하므로 원본의 **'수능 반영 영역'**을 필히 확인하세요.
                    2. 내신 정량 평가 외에 **'진로선택과목'**의 반영 비중이 높으니 학생부 관리에 유의해야 합니다.
                    3. 자세한 상담은 원본 PDF의 34페이지(예시) 전형 요강을 참고하시기 바랍니다.
                    """)
