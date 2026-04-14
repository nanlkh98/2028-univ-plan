import streamlit as st
import pandas as pd
import base64
import os

# 1. 페이지 설정
st.set_page_config(page_title="2028 대입전형 아카이브", layout="wide")

# 2. 데이터 로드
@st.cache_data(ttl=5)
def load_excel_data():
    file_path = 'data.xlsx'
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            df.columns = [str(col).strip() for col in df.columns]
            df = df.map(lambda x: str(x).strip() if isinstance(x, str) else x)
            return df
        except: return None
    return None

# 3. 메인 화면
st.title("🎓 2028 대학별 대입전형계획 아카이브")

df_all = load_excel_data()
pdf_folder = "pdfs"

if os.path.exists(pdf_folder):
    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')])
    selected_file = st.selectbox("🔍 대학을 선택하세요", ["대학 선택하기"] + pdf_files)

    if selected_file != "대학 선택하기":
        # 화면을 반반으로 나눕니다.
        col1, col2 = st.columns(2)
        
        file_path = os.path.join(pdf_folder, selected_file)
        with open(file_path, "rb") as f:
            bytes_data = f.read()
        
        with col1:
            st.subheader("📄 원본 문서 확인")
            st.write(f"현재 선택: **{selected_file}**")
            # 미리보기가 안 될 때를 대비해 다운로드 버튼을 아주 크게 만듭니다.
            st.download_button(
                label="👉 클릭하여 원본 PDF 열기 (다운로드)", 
                data=bytes_data, 
                file_name=selected_file,
                mime="application/pdf",
                use_container_width=True # 버튼을 가로로 꽉 차게
            )
            st.info("💡 위 버튼을 누르면 브라우저 하단에 파일이 생기거나 바로 열립니다.")
            
            # (보너스) 미리보기도 일단 시도는 합니다.
            base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

        with col2:
            st.subheader("📊 핵심 전형 요약")
            if df_all is not None:
                info = df_all[df_all['파일명'] == selected_file]
                if not info.empty:
                    row = info.iloc[0]
                    st.success(f"✅ {selected_file} 분석 완료")
                    
                    st.markdown("### **[학생부교과]**")
                    st.write(f"**전형명:** {row.get('교과_전형명', '-')}")
                    st.write(f"**방법:** {row.get('교과_방법', '-')}")
                    st.write(f"**최저:** {row.get('교과_최저', '-')}")
                    
                    st.divider()
                    
                    st.markdown("### **[학생부종합]**")
                    st.write(f"**전형명:** {row.get('종합_전형명', '-')}")
                    st.write(f"**1단계:** {row.get('종합_1단계', '-')}")
                    st.write(f"**2단계:** {row.get('종합_2단계', '-')}")
                    st.write(f"**최저:** {row.get('종합_최저', '-')}")
                else:
                    st.error("엑셀 데이터에서 이 대학을 찾을 수 없습니다.")

else:
    st.error("폴더를 찾을 수 없습니다.")
