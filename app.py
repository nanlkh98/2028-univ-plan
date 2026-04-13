import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# --- 💡 [데이터 센터] 대학별 요약 수치를 여기에 입력하세요 ---
univ_db = {
    "인하대학교_2028_전형계획.pdf": {
        "교과_전형명": "지역균형 (교과)",
        "교과_방법": "교과 100%",
        "교과_최저": "2합 6 (탐구1)",
        "종합_전형명": "인하미래인재 (종합)",
        "종합_1단계": "서류 100% (3.5배수 선발)",
        "종합_2단계": "1단계 성적 60% + 면접 40%",
        "종합_최저": "미적용 (의예 등 일부 제외)",
        "비고": "면접 비중이 40%로 매우 높음. 1단계 통과 시 면접 변별력 큼."
    },
    "서울대학교_2028_전형계획.pdf": {
        "교과_전형명": "지역균형",
        "교과_방법": "교과 80% + 서류 20%",
        "교과_최저": "3합 7",
        "종합_전형명": "일반전형",
        "종합_1단계": "서류 100% (2배수)",
        "종합_2단계": "1단계 50% + 면접 50%",
        "종합_최저": "미적용",
        "비고": "면접 및 구술고사가 당락을 결정함."
    }
}

# 2. PDF를 화면에 띄우는 함수
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    
    # 다운로드 버튼
    st.download_button(
        label="📥 원본 PDF 다운로드하기",
        data=bytes_data,
        file_name=os.path.basename(file_path),
        mime="application/pdf",
        key=f"dl_{os.path.basename(file_path)}"
    )

    # PDF 미리보기 (Base64)
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# 메인 화면
st.title("🎓 2028 대학별 대입전형계획 아카이브")

pdf_folder = "pdfs"
if os.path.exists(pdf_folder):
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    selected_file = st.selectbox("🔍 대학을 선택하세요", ["대학 선택하기"] + pdf_files)

    if selected_file != "대학 선택하기":
        # 화면 분할: 왼쪽(PDF 미리보기), 오른쪽(핵심 요약)
        col1, col2 = st.columns([1.2, 1]) 
        
        # 데이터 가져오기
        info = univ_db.get(selected_file, {
            "교과_전형명": "데이터 없음", "교과_방법": "업데이트 예정", "교과_최저": "확인 중",
            "종합_전형명": "데이터 없음", "종합_1단계": "업데이트 예정", "종합_2단계": "확인 중", 
            "종합_최저": "확인 중", "비고": "정보가 등록되지 않은 대학입니다."
        })

        with col1:
            st.subheader(f"📄 {selected_file} 원본")
            display_pdf(os.path.join(pdf_folder, selected_file))

        with col2:
            st.subheader(f"📊 {selected_file.split('.')[0]} 핵심 요약")
            
            # 교과전형 표
            st.markdown(f"#### 📍 학생부교과 ({info['교과_전형명']})")
            df_k = pd.DataFrame({"구분": ["선발방법", "수능최저"], "내용": [info['교과_방법'], info['교과_최저']]})
            st.table(df_k)

            # 종합전형 표 (선생님이 요청하신 단계별 상세 비중!)
            st.markdown(f"#### 📍 학생부종합 ({info['종합_전형명']})")
            df_j = pd.DataFrame({
                "단계/항목": ["1단계 (서류)", "2단계 (최종)", "수능최저"],
                "상세 비중 및 내용": [info['종합_1단계'], info['종합_2단계'], info['종합_최저']]
            })
            st.table(df_j)

            # 전문가 의견
            st.info(f"💡 **전문가 분석**\n\n{info['비고']}")
            
            # PDF가 안 보일 때를 위한 안내
            st.warning("⚠️ 만약 왼쪽 화면에 PDF가 보이지 않는다면, 상단의 '다운로드' 버튼을 눌러주세요. (브라우저 보안 설정에 따라 미리보기가 제한될 수 있습니다.)")
