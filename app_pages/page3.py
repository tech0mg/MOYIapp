import streamlit as st
import requests
import pandas as pd
import time
import os

def show_page():
    RAKUTEN_APPLICATION_ID = os.getenv("RAKUTEN_APPLICATION_ID")
    RAKUTEN_AFFILIATE_ID = os.getenv("RAKUTEN_AFFILIATE_ID")
    SAVE_PATH = "selected_hotels.csv"

    def get_area_codes():
        url = "https://app.rakuten.co.jp/services/api/Travel/GetAreaClass/20131024"
        params = {
            "format": "json",
            "applicationId": RAKUTEN_APPLICATION_ID,
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            area_codes = {}
            for large_class in data["areaClasses"]["largeClasses"][0]["largeClass"][1]["middleClasses"]:
                middle_class = large_class["middleClass"][0]
                middle_class_code = middle_class["middleClassCode"]
                middle_class_name = middle_class["middleClassName"]

                if "smallClasses" in large_class["middleClass"][1]:
                    for small_class in large_class["middleClass"][1]["smallClasses"]:
                        small_class_info = small_class["smallClass"][0]
                        small_class_code = small_class_info["smallClassCode"]
                        small_class_name = small_class_info["smallClassName"]
                        full_name = f"{middle_class_name} - {small_class_name}"
                        area_codes[full_name] = {
                            "middle": middle_class_code,
                            "small": small_class_code
                        }
                else:
                    area_codes[middle_class_name] = {
                        "middle": middle_class_code,
                        "small": ""
                    }

            return area_codes
        except requests.exceptions.RequestException as e:
            st.error(f"地区コードの取得に失敗しました: {e}")
            return {}

    def get_hotels(area_code, min_price, max_price):
        url = "https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426"
        params = {
            "format": "json",
            "applicationId": RAKUTEN_APPLICATION_ID,
            "affiliateId": RAKUTEN_AFFILIATE_ID,
            "largeClassCode": "japan",
            "middleClassCode": area_code["middle"],
            "smallClassCode": area_code["small"] if area_code["small"] else area_code["middle"],
            "hotelThumbnailSize": 3,
            "responseType": "small",
            "datumType": 1,
            "minCharge": min_price,
            "maxCharge": max_price,
            "hits": 30,
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            hotels = []
            if "hotels" in data:
                for hotel in data["hotels"]:
                    hotel_info = hotel["hotel"][0]["hotelBasicInfo"]
                    price = hotel_info.get("hotelMinCharge")

                    if price is not None and min_price <= price <= max_price:
                        hotels.append({
                            "name": hotel_info.get("hotelName", "不明"),
                            "address": f"{hotel_info.get('address1', '')} {hotel_info.get('address2', '')}",
                            "price": price,
                            "url": hotel_info.get("hotelInformationUrl", "#"),
                            "image": hotel_info.get("hotelThumbnailUrl", "")
                        })

            hotels.sort(key=lambda x: x["price"])

            return hotels
        except requests.exceptions.RequestException as e:
            st.error(f"ホテル情報の取得に失敗しました: {e}")
            return []

    def save_hotel_to_csv(hotels, filename=SAVE_PATH):
        df_hotel = pd.DataFrame(hotels)
        df_hotel.drop_duplicates(subset='name', inplace=True)
        df_hotel.to_csv(filename, index=False)

    # 初期化: セッション状態のチェック
    if 'output_hotel' not in st.session_state:
        st.session_state['output_hotel'] = []

    if 'selected_hotels' not in st.session_state:
        st.session_state['selected_hotels'] = []

    st.title("目的地と予算から宿を選択しましょう")

    area_codes = get_area_codes()

    if not area_codes:
        st.error("地区情報の取得に失敗しました。しばらくしてから再試行してください。")
        return

    selected_area = st.selectbox("目的地を選択してください", list(area_codes.keys()))

    price_range = st.select_slider(
        "予算範囲を選択してください",
        options=list(range(1000, 51000, 1000)),
        value=(8000, 20000)
    )
    min_price, max_price = price_range

    if st.button("検索"):
        with st.spinner("宿を検索中..."):
            area_code = area_codes[selected_area]
            hotels = get_hotels(area_code, min_price, max_price)
            st.session_state['output_hotel'] = hotels
            st.session_state['selected_hotels'] = []

        if hotels:
            st.success(f"{len(hotels)}件の宿が見つかりました。")
        else:
            st.warning("条件に合う宿が見つかりませんでした。別の条件で試してみてください。")

    # ホテル情報の表示とチェックボックスによる選択
    if st.session_state['output_hotel']:
        for hotel in st.session_state['output_hotel']:
            col1, col2, col3 = st.columns([2, 4, 1])
            with col1:
                st.image(hotel["image"], width=150)
            with col2:
                st.write(f"**{hotel['name']}**")
                st.write(f"料金: {hotel['price']}円")
                st.write(f"住所: {hotel['address']}")
            with col3:
                if st.checkbox("選択", key=hotel["name"]):
                    if hotel not in st.session_state['selected_hotels']:
                        st.session_state['selected_hotels'].append(hotel)
                else:
                    if hotel in st.session_state['selected_hotels']:
                        st.session_state['selected_hotels'].remove(hotel)
            st.write("---")

    # CSVに保存するボタン
    if st.button("CSVに保存"):
        if st.session_state['selected_hotels']:
            save_hotel_to_csv(st.session_state['selected_hotels'])
            st.success("選択された宿泊施設をCSVに保存しました。")
        else:
            st.warning("宿泊施設が選択されていません。")

    # APIリクエスト制限への対応
    time.sleep(1)

