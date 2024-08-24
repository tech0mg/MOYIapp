import streamlit as st
import requests
import pandas as pd
import time
import os

def show_page():

    # CSV保存先のパス
    SAVE_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "MOYI_test", "selected_hotels.csv")

    # 地区コードを取得する関数
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

    # ホテル情報を取得する関数
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

    # 選択されたホテル情報をCSVに保存する関数
    def save_hotel_to_csv(hotel_info):
        directory = os.path.dirname(SAVE_PATH)
        if not os.path.exists(directory):
            os.makedirs(directory)

        df = pd.DataFrame([hotel_info])
        df.to_csv(SAVE_PATH, mode="a", header=not os.path.exists(SAVE_PATH), index=False, encoding="utf-8-sig")
        st.success(f"ホテル情報をCSVに保存しました: {hotel_info['name']} (保存先: {SAVE_PATH})")

# Streamlitアプリケーション
    try:
        st.title("目的地と予算から宿を選択しましょう")

        # 地区コードを取得
        area_codes = get_area_codes()

        if not area_codes:
            st.error("地区情報の取得に失敗しました。しばらくしてから再試行してください。")
            return

        # 目的地選択
        selected_area = st.selectbox("目的地を選択してください", list(area_codes.keys()))

        # 予算範囲選択
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

            if hotels:
                st.success(f"{len(hotels)}件の宿が見つかりました。")
                for hotel in hotels:
                    col1, col2, col3 = st.columns([2, 4, 1])
                    with col1:
                        st.image(hotel["image"], width=150)
                    with col2:
                        st.write(f"**{hotel['name']}**")
                        st.write(f"料金: {hotel['price']}円")
                        st.write(f"住所: {hotel['address']}")
                    with col3:
                        if st.button("選択", key=hotel["name"]):
                            save_hotel_to_csv({"name": hotel["name"], "address": hotel["address"]})
                    st.write("---")
            else:
                st.warning("条件に合う宿が見つかりませんでした。別の条件で試してみてください。")

        # APIリクエスト制限への対応
        time.sleep(1)
        
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        st.exception(e)    