import streamlit as st
import pandas as pd
import os
from openai import OpenAI

# CSVファイルのパス
CSV_FILE_PATH = "travel_suggestions.csv"

def save_to_csv(suggestion_data):
    try:
        # 既存のCSVファイルがあるかどうかをチェック
        if os.path.exists(CSV_FILE_PATH) and os.path.getsize(CSV_FILE_PATH) > 0:
            # 既存のデータを読み込む
            df = pd.read_csv(CSV_FILE_PATH)
        else:
            # ファイルが存在しないか、空の場合は新しいデータフレームを作成
            df = pd.DataFrame(columns=["suggestion_name", "suggestion_description", "service_name"])

        # 新しい提案をデータフレームに追加
        new_entry = pd.DataFrame([suggestion_data])
        df = pd.concat([df, new_entry], ignore_index=True)

        # データをCSVに保存
        df.to_csv(CSV_FILE_PATH, index=False)
    except pd.errors.EmptyDataError:
        st.error("CSVファイルが空です。新しいファイルを作成します。")
        df = pd.DataFrame([suggestion_data], columns=["suggestion_name", "suggestion_description", "service_name"])
        df.to_csv(CSV_FILE_PATH, index=False)

def show_page():
    # アクセスの為のキーをos.environ["OPENAI_API_KEY"]に代入し、設定
    api_key = os.getenv('OPENAI_API_KEY')
    # openAIの機能をclientに代入
    client = OpenAI()

    # CSVファイルから住所データを読み込む
    def load_address_data():
        try:
            hotels_df = pd.read_csv('selected_hotels.csv')
            return hotels_df['address'].tolist()
        except FileNotFoundError:
            st.error("selected_hotels.csv ファイルが見つかりません。")
            return []

    # chatGPTにリクエストするためのメソッドを設定。引数には書いてほしい内容と文章のテイストと最大文字数を指定
    def run_gpt(content_text_to_gpt, address):
        # リクエスト内容を決める
        request_to_gpt = (
            content_text_to_gpt +
            f"以下のフォーマットに従って、旅行先の候補として{address}付近で観光地、アクティビティ、おいしいご飯屋さんを提案してください。\n\n" +
            "1. 提案名: ここに提案名を記述\n" +
            "   説明文: ここに提案の説明文（100文字程度）を記述\n" +
            "   サービス: ここに具体的な施設やサービスの名称を記述\n\n" +
            "このフォーマットを3つの異なる提案について繰り返してください。各提案は新しい行で始めてください。" +
            "回答は次のような形式で、番号付きリストとして表示してください。\n\n" +
            "1. 提案名: 〇〇\n   説明文: △△△△△△\n   サービス: □□□\n" +
            "2. 提案名: 〇〇\n   説明文: △△△△△△\n   サービス: □□□\n" +
            "3. 提案名: 〇〇\n   説明文: △△△△△△\n   サービス: □□□\n"
        )
        
        # 決めた内容を元にclient.chat.completions.createでchatGPTにリクエスト
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": request_to_gpt},
            ],
        )

        # レスポンスの内容
        output_content = response.choices[0].message.content.strip()
        return output_content

    # フロントエンドコード
    st.title('▶ 旅行先提案')

    # CSVから住所を読み込む
    address_list = load_address_data()

    # ユーザーにアドレスを選択させる
    if address_list:
        selected_address = st.selectbox("住所を選択してください", address_list)
        content_text_to_gpt = st.text_area("どのような旅にしたいか、やりたいことを教えてください！", height=50)

        # GPTにリクエストを送信して結果を取得
        if st.button("送信"):
            output_content = run_gpt(content_text_to_gpt, selected_address)
            st.session_state['output_content'] = output_content

        # セッションに保存された提案内容を表示して選択肢にする
        if 'output_content' in st.session_state:
            st.write(st.session_state['output_content'])

            # 提案内容の選択肢を表示
            suggestions = st.session_state['output_content'].split("\n\n")  # 提案を分割
            suggestion_titles = [s.split("\n")[0].strip() for s in suggestions]  # 提案のタイトルだけを抽出
            
            selected_suggestions = []
            for idx, title in enumerate(suggestion_titles):
                # ユニークなキーを使用してチェックボックスを作成
                if st.checkbox(title, key=f"checkbox_{idx}"):
                    selected_suggestions.append(title)

            # 選択された提案を保存
            if st.button("選択を保存"):
                for selected_title in selected_suggestions:
                    selected_suggestion = next(s for s in suggestions if s.startswith(selected_title))
                    suggestion_parts = selected_suggestion.split("\n")
                    suggestion_data = {
                        "suggestion_name": suggestion_parts[0].strip(),
                        "suggestion_description": suggestion_parts[1].strip(),
                        "service_name": suggestion_parts[2].strip() if len(suggestion_parts) > 2 else ""
                    }
                    save_to_csv(suggestion_data)
                st.success("提案が保存されました。")
    else:
        st.error("住所情報がありません。")

if __name__ == "__main__":
    show_page()
