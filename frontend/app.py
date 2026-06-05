# frontend/app.py
import streamlit as st
import requests

st.set_page_config(page_title="古文微服務系統", page_icon="📜", layout="wide")

st.title("📜 文言文翻譯")
st.write("本系統翻譯、作者與賞析由獨立 API 服務提供運作。")

backend_url = st.sidebar.text_input("FastAPI 後端網址：", value="http://127.0.0.1:8000")

user_input = st.text_area("請輸入文言文段落：", height=150, placeholder="例如：晉太元中，武陵人捕魚為業...")

# 畫出三個並排的漂亮按鈕，對應後端的三個獨立 Endpoints
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    btn_trans = st.button("📝 執行白話翻譯", type="primary", use_container_width=True)
with col_btn2:
    btn_author = st.button("👤 檢索作者生平", type="secondary", use_container_width=True)
with col_btn3:
    btn_appreciate = st.button("🔍 啟動深度賞析", type="secondary", use_container_width=True)


# ─── 1. 翻譯按鈕邏輯 ───
if btn_trans:
    if not user_input.strip():
        st.warning("請先輸入古文。")
    else:
        with st.spinner("⏳ 正在執行翻譯與本機字典比對中..."):
            try:
                res = requests.post(f"{backend_url}/api/v1/translations/", json={"text": user_input, "enable_notes": True}, timeout=None)
                if res.status_code == 200:
                    data = res.json()
                    st.subheader("📋 現代白話翻譯成果")
                    st.success(data.get("translated_text"))
                    
                    # 渲染難字注釋字典
                    notes = data.get("notes", {})
                    if notes:
                        st.markdown("#### 💡 關鍵字詞與典故注釋")
                        for k, v in notes.items():
                            st.markdown(f"- **{k}**：{v}")
                else:
                    st.error(f"錯誤代碼: {res.status_code}")
            except Exception as e:
                st.error(f"連線失敗: {e}")


# ─── 2. 作者按鈕邏輯 ───
if btn_author:
    if not user_input.strip():
        st.warning("請先在上方大框框輸入古文，系統將自動從文本中考證作者生平！")
    else:
        query_name = user_input.strip()
        
        with st.spinner("⏳ 正在由文本全自動考證作者生平中..."):
            try:
                res = requests.get(f"{backend_url}/api/v1/authors/", params={"name": query_name}, timeout=None)
                if res.status_code == 200:
                    authors = res.json()
                    if authors:
                        for aut in authors:
                            st.markdown(f"### 👤 作者：{aut['name']} ({aut['dynasty']}代)")
                            st.caption(f"生卒字號：{aut['birth_death_years'] or '資料暫缺'}")
                            st.info(aut['biography'])
                            st.markdown(f"**📚 經典代表作**：{', '.join([f'《{w}》' for w in aut['major_works']])}")
                    else:
                        st.warning("🤔 Gemini 努力分析了整段文字，但沒有找到明確的歷史作者，請試著換一段古文。")
                else:
                    st.error(f"後端服務回應異常，錯誤代碼: {res.status_code}")
            except Exception as e:
                st.error(f"連線失敗: {e}")


# ─── 3. 賞析按鈕邏輯 ───
if btn_appreciate:
    if len(user_input.strip()) < 5:
        st.warning("內文字數過短，無法進行有效賞析。")
    else:
        with st.spinner("⏳ Gemini 正在從多維度進行深度文學賞析..."):
            try:
                res = requests.post(f"{backend_url}/api/v1/appreciations/", json={"text": user_input}, timeout=None)
                if res.status_code == 200:
                    data = res.json()
                    st.subheader(f"🔍 《{data.get('title', '古文賞析')}》深度文學報告")
                    
                    tab1, tab2, tab3 = st.tabs(["🎯 核心主旨", "✨ 寫作特色與修辭", "📜 時代背景與啟示"])
                    with tab1:
                        st.info(data.get("core_meaning"))
                    with tab2:
                        st.markdown(data.get("literary_style"))
                    with tab3:
                        st.warning(data.get("historical_context"))
                else:
                    st.error(f"錯誤: {res.status_code}")
            except Exception as e:
                st.error(f"連線失敗: {e}")