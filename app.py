import streamlit as st
from app_pages import page1, page2, page3, page4

st.set_page_config(
    page_title="ホーム",  # ブラウザタブに表示されるタイトル
    page_icon="🏠",     # オプション: ページアイコン（emojiや文字列）
    layout="wide",      # オプション: レイアウト ("centered" または "wide")
    initial_sidebar_state="expanded"  # サイドバーの初期状態 ("expanded" または "collapsed")
)

st.title("ホーム")

PAGES = {
    "Page 1": page1,
    "Page 2": page2,
    "Page 3": page3,
    "Page 4": page4
}

def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    page = PAGES[selection]
    page.show_page()

if __name__ == "__main__":
    main()
