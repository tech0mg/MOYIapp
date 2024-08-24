import streamlit as st
from openai import OpenAI
import pandas as pd
import os

def show_page():
    # アクセスの為のキーをos.environ["OPENAI_API_KEY"]に代入し、設定
    api_key = os.getenv('OPENAI_API_KEY')
    # openAIの機能をclientに代入
    client = OpenAI()

    # chatGPTにリクエストするためのメソッドを設定。引数には書いてほしい内容と文章のテイストと最大文字数を指定
    def run_gpt(content_text_to_gpt):
        # リクエスト内容を決める
        request_to_gpt= (
            content_text_to_gpt +
            " やりたいことを追加してより有意義な旅行計画にしたいと考えています。" +
            "鎌倉付近で最適な3つの案を名称・説明文100文字程度の構成で考えてほしい。" +
            "また、それぞれを楽しむために具体的な施設やサービスを1つ見つけて紹介してほしい。" +
            "回答は表題に提案名、副題に具体的なサービスや施設の名称のみ、テキストで説明文の構成にしてほしい。"
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


    # 関数化：GPTへのリクエスト内容
    def run_gpt_An(sel1,last_row):
        request_to_sl= (
            last_row + "の選択肢の中で" + sel1 +
            "を旅行先に選びます。示してくれた具体的な施設やサービス名称を１つだけレスポンスで返してほしい。"
        )
    
        response_ls = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": request_to_sl},
            ],
        )
    
        # レスポンスの取得
        output_content_ls = response_ls.choices[0].message.content.strip()
        return output_content_ls
    
    # CSVを作成する
    def save_response_to_csv(response, filename="travel_suggestions.csv"):
        # DataFrameを作成
        df = pd.DataFrame([{"response": response}])
        # CSVファイルに保存
        df.to_csv(filename, index=False)
        print(f"Response saved to {filename}")
    
    # 以下、フロントコード
    st.title('▶ 旅行先提案')  

    # 書かせたい内容
    content_text_to_gpt = st.text_area("どのような旅にしたいか、やりたいことを教えてください！", height=50)

    # GPTにリクエストを送信して結果を取得
    if st.button("送信"):
        # GPTにリクエストを送信して結果を取得し、session_stateに保存
        st.session_state['output_content'] = run_gpt(content_text_to_gpt)
        save_response_to_csv(st.session_state['output_content'])

    # 結果を表示
    if 'output_content' in st.session_state:
        # CSVファイルからデータを読み込み
        df = pd.read_csv('travel_suggestions.csv')
        
        # 最下行のデータを取得
        last_row = df.iloc[-1]['response']
        st.write(last_row)


    # 結果の選択
    options1 = ["1つ目", "2つ目", "3つ目"]
    sel1 = st.selectbox('どれにする？', options1, index=0)

    # GPTにリクエストを送信して結果を取得
    if st.button("決定"):
        output_content_text_sl = run_gpt_An(sel1,last_row)
        st.write(output_content_text_sl)
    