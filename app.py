import streamlit as st
from app_pages import page1, page2, page3, page4, page5

st.set_page_config(
    page_title="ホーム",  # ブラウザタブに表示されるタイトル
    page_icon="🏠",     # オプション: ページアイコン（emojiや文字列）
    layout="wide",      # オプション: レイアウト ("centered" または "wide")
    initial_sidebar_state="expanded"  # サイドバーの初期状態 ("expanded" または "collapsed")
)

PAGES = {
    "旅行計画登録": page1,
    "旅行計画表": page2,
    "目的地設定": page3,
    "メンバー登録": page4,
    "旅行先提案": page5
}

def main():
    st.sidebar.title("機能一覧")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    page = PAGES[selection]
    page.show_page()

if __name__ == "__main__":
    main()
