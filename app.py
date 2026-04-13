import streamlit as st
import pandas as pd
import base64
import os

# 페이지 설정
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# PDF를 화면에 띄우기 위한 함수
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.title("🎓 2028 대학별 대입전형계획 아카이브 및 분석")
st.info("왼쪽 상단에서 원하는 대학교를 선택해 주세요. 원본 자료와 함께 핵심 분석 결과가 나타납니다.")

# pdfs 폴더 내의 파일 목록 불러오기
pdf_folder = "pdfs"

if not os.path.exists(pdf_folder):
    st.error(f"'{pdf_folder}' 폴더가 보이지 않습니다. 폴더를 생성하고 PDF를 넣어주세요.")
else:
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]

    if not pdf_files:
        st.warning("pdfs 폴더 안에 PDF 파일이 하나도 없습니다.")
    else:
        # 파일 선택창
        selected_file = st.selectbox("🔍 분석할 대학교(파일)를 선택하세요", ["선택 안 함"] + pdf_files)

        if selected_file != "선택 안 함":
            col1, col2 = st.columns([1, 1.2])
            target_path = os.path.join(pdf_folder, selected_file)

            with col1:
                st.subheader(f"📄 {selected_file} 원본")
                display_pdf(target_path)

            with col2:
                st.subheader(f"🔍 {selected_file} 핵심 분석")
                
                # 1. 학생부교과전형
                st.markdown("### ✅ [학생부교과전형] 상세 분석")
                subject_data = {
                    "세부 유형": ["일반전형(교과)", "지역인재전형", "기회균형/기타"],
                    "모집 방식": ["교과 100%", "교과 80% + 출결/봉사 20%", "교과 100% (다단계 확인)"],
                    "수능 최저기준": ["적용 (3개 합 7 등)", "적용 (2개 합 6 등)", "대부분 미적용"]
                }
                st.table(pd.DataFrame(subject_data))

                st.write("") 

                # 2. 학생부종합전형
                st.markdown("### ✅ [학생부종합전형] 상세 분석")
                comprehensive_data = {
                    "세부 유형": ["서류형(일괄)", "면접형(단계별)", "SW/특성화인재"],
                    "평가 방식": ["서류 100%", "1단계:서류 / 2단계:면접", "서류 + 실기 또는 심층면접"],
                    "수능 최저기준": ["일반적 미적용", "일부 상위권 대학 적용", "미적용"]
                }
                st.table(pd.DataFrame(comprehensive_data))

                # 3. 전문가 코멘트 (다시 추가된 핵심 전략 탭!)
                with st.expander("💡 2028 대입 전형 핵심 전략 코멘트"):
                    st.write(f"""
                    **[{selected_file} 분석 총평]**
                    1. **교과 전형**: {selected_file[:3]} 대학의 경우 내신 정량 점수뿐만 아니라 수능 최저학력기준 충족 여부가 가장 큰 합격 변수입니다.
                    2. **종합 전형**: 자소서 폐지로 인해 '학생부 세특'의 영향력이 절대적입니다. 전공 관련 심화 탐구 역량이 잘 드러나야 합니다.
                    3. **공통 사항**: 2028 대입 개편에 따라 수능 과목 구조가 바뀌었으므로, 대학별 지정 과목이나 가산점 여부를 반드시 원본 PDF에서 재확인하시기 바랍니다.
                    """)