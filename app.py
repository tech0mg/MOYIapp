import streamlit as st
from pages import page1, page2, page3, page4

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
