import streamlit as st
import pandas as pd

def show_page():
    st.title("旅行計画表")

    def load_data():
        # データを読み込む
        plans_df = pd.read_csv('travel_plans.csv')
        hotels_df = pd.read_csv('selected_hotels.csv')
        suggestions_df = pd.read_csv('travel_suggestions.csv')
        return plans_df, hotels_df, suggestions_df

    st.title("旅行計画の表示")

    # データの読み込み
    plans_df, hotels_df, suggestions_df = load_data()

    # 旅行計画の選択
    selected_plan = st.selectbox("旅行計画を選択してください", plans_df['plan_name'])
    st.write(f"選択された旅行計画: **{selected_plan}**")

    # 宿泊施設の情報を表示
    st.write("### 泊まる宿情報")
    for index, hotel in hotels_df.iterrows():
        st.image(hotel['image'], width=150)
        st.write(f"**名前:** {hotel['name']}")
        st.write(f"**住所:** {hotel['address']}")
        st.write(f"**価格:** {hotel['price']}円")
        st.write(f"[詳細情報]({hotel['url']})")
        st.write("---")

    # 追加の旅行先の表示
    st.write("### 追加の旅行先の提案")
    for suggestion in suggestions_df['response']:
        st.write(f"- {suggestion}")
