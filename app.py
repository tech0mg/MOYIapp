import streamlit as st
from pages import page1, page2, page3

# タブの作成
tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

with tab1:
    page1.render()

with tab2:
    page2.render()

with tab3:
    page3.render()
