import streamlit as st
import pandas as pd
import os

def show_page():

    # 保存先のファイルパスを設定
    file_path = "data.csv"

    # ファイルが存在しない場合、空のCSVファイルを作成
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=["name", "email", "age"])
        df.to_csv(file_path, index=False)

    # ユーザー入力
    st.title("ユーザーデータの入力")
    name = st.text_input("名前")
    email = st.text_input("メールアドレス")
    age = st.number_input("年齢", min_value=0)

    # ボタンが押されたときにデータをCSVに保存
    if st.button("データを保存"):
        if name and email and age:
            # 既存のCSVファイルを読み込む
            df = pd.read_csv(file_path)

            # 新しいデータをDataFrameとして作成
            new_data = pd.DataFrame([{"name": name, "email": email, "age": age}])

            # 既存のデータと新しいデータをマージ
            df = pd.concat([df, new_data], ignore_index=True)

            # マージされたデータを再びCSVに保存
            df.to_csv(file_path, index=False)

            st.success("データが保存されました。")
        else:
            st.error("すべてのフィールドに入力してください。")

    # 保存されたデータの表示
    st.write("保存されたデータ:")
    df = pd.read_csv(file_path)
    st.write(df)