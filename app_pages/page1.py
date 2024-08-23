# pages/page1.py
import streamlit as st

def show_page():
    st.title("旅行いっちゃう？アプリ")
    st.write("旅行名を登録します。ワクワクする名前を記載してください。")
    
    # 旅行名の入力
    travel_name = st.text_input("旅行名を設定してください。")
    
    # 登録ボタン
    if st.button("登録"):
        if travel_name:
            st.success(f"旅行計画『{travel_name}』を登録しました！")
            st.success(f"次のページで行きたいところを登録してください！")
        else:
            st.error("旅行名を入力してください。")

if __name__ == "__main__":
    show_page()

