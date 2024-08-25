# pages/page1.py
import streamlit as st
import pandas as pd
import os

print("Current Directory:", os.getcwd())

# CSVファイルのパス
CSV_FILE_PATH = "travel_plans.csv"

def save_to_csv(travel_name):
    # 既存のCSVファイルがあるかどうかをチェック
    if os.path.exists(CSV_FILE_PATH):
        # 既存のデータを読み込む
        df = pd.read_csv(CSV_FILE_PATH)
    else:
        # 新しいデータフレームを作成
        df = pd.DataFrame(columns=["plan_name"])
    
    # 新しい旅行名をデータフレームに追加
    new_entry = pd.DataFrame({"plan_name": [travel_name]})
    df = pd.concat([df, new_entry], ignore_index=True)
    
    # データをCSVに保存
    df.to_csv(CSV_FILE_PATH, index=False)
    st.success(f"旅行計画『{travel_name}』をCSVファイルに保存しました！")

def show_page():
    st.title("旅行いっちゃう？アプリ")
    st.write("旅行名を登録します。ワクワクする名前を記載してください。")
    
    # 旅行名の入力
    travel_name = st.text_input("旅行名を設定してください。")
    
    # 登録ボタン
    if st.button("登録"):
        if travel_name:
            save_to_csv(travel_name)  # 旅行名をCSVファイルに保存
            st.success(f"旅行計画『{travel_name}』を登録しました！")
            st.success(f"次のページで行きたいところを登録してください！")
        else:
            st.error("旅行名を入力してください。")

if __name__ == "__main__":
    show_page()


