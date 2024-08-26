import streamlit as st
import pandas as pd
import googlemaps
import streamlit.components.v1 as components
import os

# Google Maps APIキーの設定
API_KEY = os.getenv("GCP_MAP_API_KEY")

def show_page():
    st.title("旅行計画表")

    # Google Maps APIクライアントの作成
    gmaps = googlemaps.Client(key=API_KEY)

    def load_data():
        # データを読み込む
        plans_df = pd.read_csv('travel_plans.csv')
        hotels_df = pd.read_csv('selected_hotels.csv')
        suggestions_df = pd.read_csv('travel_suggestions.csv')
        return plans_df, hotels_df, suggestions_df

    # データの読み込み
    plans_df, hotels_df, suggestions_df = load_data()

    if not plans_df.empty:
        # 旅行計画の選択
        selected_plan = st.selectbox("旅行計画を選択してください", plans_df['plan_name'])
        selected_plan_details = plans_df[plans_df['plan_name'] == selected_plan].iloc[0]

        # 選択された旅行計画の詳細を表示
        st.write(f"### 選択された旅行計画: {selected_plan}")
        st.write(f"**出発日:** {selected_plan_details['departure_date']}")
        st.write(f"**帰宅日:** {selected_plan_details['return_date']}")
        st.write(f"**出発駅:** {selected_plan_details['departure_station']}")

        # 出発駅を保存
        departure_station = selected_plan_details['departure_station']
    else:
        st.warning("旅行計画がまだ登録されていません。")
        departure_station = None

    # 宿泊施設の情報を表示
    st.write("### 泊まる宿情報")
    if not hotels_df.empty:
        hotel_name = None
        hotel_address = None
        for index, hotel in hotels_df.iterrows():
            st.image(hotel['image'], width=150)
            st.write(f"**名前:** {hotel['name']}")
            st.write(f"**住所:** {hotel['address']}")
            st.write(f"**価格:** {hotel['price']}円")
            st.write(f"[詳細情報]({hotel['url']})")
            st.write("---")
            hotel_name = hotel['name']  # 最初の宿泊施設を選択
            hotel_address = hotel['address']
    else:
        st.warning("宿泊施設情報がありません。")
        hotel_address = None

    # 追加の旅行先の表示
    st.write("### 追加の旅行先の提案")
    suggestion_services = []
    if not suggestions_df.empty:
        for index, row in suggestions_df.iterrows():
            st.write(f"**提案名:** {row['suggestion_name']}")
            st.write(f"**説明:** {row['suggestion_description']}")
            st.write(f"**サービス:** {row['service_name']}")
            st.write("---")
            suggestion_services.append(row['service_name'])
    else:
        st.warning("追加の旅行先情報がありません。")

    # Google Maps APIでルート検索と地図の埋め込み
    if departure_station and hotel_address and suggestion_services:
        st.write("### Google Mapsによるルート検索")
        waypoints = []

        # 中継地点（ウェイポイント）の座標を取得
        for service in suggestion_services:
            geocode_result = gmaps.geocode(service)
            if geocode_result:
                latlng = geocode_result[0]['geometry']['location']
                waypoints.append(f"{{location: {{lat: {latlng['lat']}, lng: {latlng['lng']}}}, stopover: true}}")
            else:
                st.warning(f"{service} の座標を取得できませんでした。")

    # Google Maps APIでルート検索と地図の埋め込み
    if departure_station and hotel_address and suggestion_services:
        coordinates = []

        # 各地点の座標を取得
        for location in [departure_station, hotel_address] + suggestion_services:
            geocode_result = gmaps.geocode(location)
            if geocode_result:
                latlng = geocode_result[0]['geometry']['location']
                coordinates.append((latlng['lat'], latlng['lng']))
            else:
                st.warning(f"{location} の座標を取得できませんでした。")

        # Google Maps埋め込み用のHTMLを作成
        if len(coordinates) >= 2:
            waypoints = [
                f"{{location: {{lat: {coordinates[i][0]}, lng: {coordinates[i][1]}}}, stopover: true}}"
                for i in range(1, len(coordinates) - 1)
            ]

            map_html = f"""
            <div id="map" style="height: 500px;"></div>
            <script>
            function initMap() {{
                var map = new google.maps.Map(document.getElementById('map'), {{
                    zoom: 6,
                    center: {{lat: {coordinates[0][0]}, lng: {coordinates[0][1]}}}
                }});

                var directionsService = new google.maps.DirectionsService();
                var directionsRenderer = new google.maps.DirectionsRenderer();
                directionsRenderer.setMap(map);

                var waypts = [{','.join(waypoints)}];

                directionsService.route(
                {{
                    origin: {{lat: {coordinates[0][0]}, lng: {coordinates[0][1]}}},
                    destination: {{lat: {coordinates[-1][0]}, lng: {coordinates[-1][1]}}},
                    waypoints: waypts,
                    optimizeWaypoints: true,
                    travelMode: 'DRIVING'
                }},
                function(response, status) {{
                    if (status === 'OK') {{
                        directionsRenderer.setDirections(response);
                    }} else {{
                        window.alert('Directions request failed due to ' + status);
                    }}
                }});
            }}
            </script>
            <script src="https://maps.googleapis.com/maps/api/js?key={API_KEY}&callback=initMap" async defer></script>
            """
            components.html(map_html, height=500)

if __name__ == "__main__":
    show_page()