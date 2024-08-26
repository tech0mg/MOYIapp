import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# CSVファイルのパス
CSV_FILE_PATH = "travel_plans.csv"

def save_to_csv(travel_data):
    # 既存のCSVファイルがあるかどうかをチェック
    if os.path.exists(CSV_FILE_PATH):
        # 既存のデータを読み込む
        df = pd.read_csv(CSV_FILE_PATH)
    else:
        # 新しいデータフレームを作成
        df = pd.DataFrame(columns=["plan_name", "departure_date", "return_date", "departure_station"])
    
    # 新しい旅行計画をデータフレームに追加
    new_entry = pd.DataFrame([travel_data])
    df = pd.concat([df, new_entry], ignore_index=True)
    
    # データをCSVに保存
    df.to_csv(CSV_FILE_PATH, index=False)

def show_page():
    # セッション状態の初期化
    if 'trip_name' not in st.session_state:
        st.session_state.trip_name = ""
    if 'departure_date' not in st.session_state:
        st.session_state.departure_date = date.today()
    if 'return_date' not in st.session_state:
        st.session_state.return_date = date.today()
    if 'departure_station' not in st.session_state:
        st.session_state.departure_station = ""
    if 'travel_data' not in st.session_state:
        st.session_state.travel_data = []

    st.title("旅行いっちゃう？アプリ")

    # 旅行名の入力
    st.session_state.trip_name = st.text_input("旅行名を登録します。ワクワクする名前を記載してください。", st.session_state.trip_name)

    # 出発日の入力
    st.session_state.departure_date = st.date_input(
        "出発日を選んでください。",
        value=st.session_state.departure_date if isinstance(st.session_state.departure_date, (date, datetime)) else date.today()
    )

    # 帰宅日の入力
    st.session_state.return_date = st.date_input(
        "帰宅日を選んでください。",
        value=st.session_state.return_date if isinstance(st.session_state.return_date, (date, datetime)) else date.today()
    )

    # 出発駅の入力
    st.session_state.departure_station = st.text_input("出発駅を入力してください。", st.session_state.departure_station)

    # 旅行データの保存
    if st.button("旅行プランを保存"):
        if st.session_state.trip_name and st.session_state.departure_station:
            travel_entry = {
                "plan_name": st.session_state.trip_name,
                "departure_date": st.session_state.departure_date,
                "return_date": st.session_state.return_date,
                "departure_station": st.session_state.departure_station
            }
            st.session_state.travel_data.append(travel_entry)
            save_to_csv(travel_entry)  # CSVに保存
            st.success(
                    "旅行計画『保存』をCSVファイルに保存しました！" +
                    "次のページで行きたいところを登録してください！"
                    )
        else:
            st.error("すべての項目を入力してください。")

    # 保存された旅行データを表示
    if st.session_state.travel_data:
        st.write("### 保存された旅行プラン")
        st.dataframe(pd.DataFrame(st.session_state.travel_data))

if __name__ == "__main__":
    show_page()
