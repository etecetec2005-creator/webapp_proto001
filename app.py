import streamlit as st

st.set_page_config(page_title="位置情報・駅取得", layout="centered")
st.title("📍 住所 ＆ 最寄り駅 取得")

st.write("ボタンを押すと、現在地の住所と一番近い駅を表示します。")

# JavaScriptコード（住所特定 ＋ 駅検索）
location_script = """
<div id="result" style="font-size:15px; color:#333; padding:15px; background:#f0f2f6; border-radius:10px; border-left: 5px solid #007bff; min-height: 80px; line-height: 1.6;">
    🧭 ここに情報が表示されます
</div>

<button id="btn" style="margin-top:20px; padding:15px 24px; background-color:#007bff; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold; width:100%; font-size:16px;">
    現在地を解析する
</button>

<script>
document.getElementById('btn').onclick = function() {
    const resultDiv = document.getElementById('result');
    const btn = document.getElementById('btn');import streamlit as st

st.set_page_config(page_title="位置情報取得", layout="centered")
st.title("📍 住所 ＆ 最寄り駅 取得")

st.write("ボタンを押すと、現在の住所と最寄り駅を表示します。")

# JavaScriptコード（住所特定 ＋ 最寄り駅1つのみ取得）
location_script = """
<div id="result" style="font-size:15px; color:#333; padding:15px; background:#f0f2f6; border-radius:10px; border-left: 5px solid #007bff; min-height: 80px; line-height: 1.6;">
    🧭 ここに情報が表示されます
</div>

<button id="btn" style="margin-top:20px; padding:15px 24px; background-color:#007bff; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold; width:100%; font-size:16px;">
    現在地を解析する
</button>

<script>
document.getElementById('btn').onclick = function() {
    const resultDiv = document.getElementById('result');
    const btn = document.getElementById('btn');
    
    resultDiv.innerHTML = "🛰️ 座標を取得中...";
    btn.disabled = true;
    btn.style.backgroundColor = "#ccc";

    navigator.geolocation.getCurrentPosition(
        async function(pos) {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            
            try {
                // 1. 住所の取得 (OSM Nominatim)
                const addrUrl = "https://nominatim.openstreetmap.org/reverse?format=json&lat=" + lat + "&lon=" + lon + "&zoom=18&addressdetails=1&accept-language=ja";
                const addrRes = await fetch(addrUrl);
                const addrData = await addrRes.json();
                
                let displayAddr = "住所不明";
                if (addrData && addrData.address) {
                    const a = addrData.address;
                    const city = a.city || a.town || a.village || "";
                    const dist = a.city_district || "";
                    // 町名・丁目 (候補を順番に確認)
                    const town = a.suburb || a.neighbourhood || a.road || a.quarter || "";
                    
                    displayAddr = (city + dist + town).replace(/日本|〒[0-9-]+/g, "").trim();
                }

                // 2. 最寄り駅の取得 (HeartRails Express API)
                const stationUrl = "https://express.heartrails.com/api/json?method=getStations&x=" + lon + "&y=" + lat;
                const stationRes = await fetch(stationUrl);
                const stationData = await stationRes.json();
                
                let displayStation = "駅が見つかりませんでした";
                if (stationData.response && stationData.response.station && stationData.response.station.length > 0) {
                    // 1番近い駅のみを取得し「〇〇駅」形式にする
                    const s = stationData.response.station[0];
                    displayStation = s.name + "駅";
                }

                // 3. 結果の表示
                resultDiv.innerHTML = "<strong>🏠 住所:</strong><br>" + displayAddr + 
                                     "<br><br><strong>🚉 最寄り駅:</strong><br>" + displayStation;

            } catch (error) {
                resultDiv.innerHTML = "❌ 情報の取得中にエラーが発生しました。";
            } finally {
                btn.disabled = false;
                btn.style.backgroundColor = "#007bff";
            }
        },
        function(err) {
            resultDiv.innerHTML = "⚠️ 位置情報の取得を許可してください。";
            btn.disabled = false;
            btn.style.backgroundColor = "#007bff";
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
};
</script>
"""

st.components.v1.html(location_script, height=300)
    
    resultDiv.innerHTML = "🛰️ 座標を取得中...";
    btn.disabled = true;
    btn.style.backgroundColor = "#ccc";

    navigator.geolocation.getCurrentPosition(
        async function(pos) {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            
            resultDiv.innerHTML = "🔍 住所と駅を検索中...";
            
            try {
                // 1. 住所の取得 (OSM Nominatim)
                const addrUrl = "https://nominatim.openstreetmap.org/reverse?format=json&lat=" + lat + "&lon=" + lon + "&zoom=18&addressdetails=1&accept-language=ja";
                const addrRes = await fetch(addrUrl);
                const addrData = await addrRes.json();
                
                let displayAddr = "住所不明";
                if (addrData && addrData.address) {
                    const a = addrData.address;
                    const city = a.city || a.town || a.village || "";
                    const dist = a.city_district || "";
                    const town = a.suburb || a.neighbourhood || a.road || "";
                    displayAddr = (city + dist + town).replace(/日本|〒[0-9-]+/g, "");
                }

                // 2. 最寄り駅の取得 (HeartRails Express API)
                const stationUrl = "https://express.heartrails.com/api/json?method=getStations&x=" + lon + "&y=" + lat;
                const stationRes = await fetch(stationUrl);
                const stationData = await stationRes.json();
                
                let displayStation = "駅が見つかりませんでした";
                if (stationData.response && stationData.response.station && stationData.response.station.length > 0) {
                    const s = stationData.response.station[0];
                    displayStation = s.line + " " + s.name + "駅 (約" + s.distance + ")";
                }

                // 3. 結果の表示
                resultDiv.innerHTML = "<strong>🏠 住所:</strong><br>" + displayAddr + 
                                     "<br><br><strong>🚉 最寄り駅:</strong><br>" + displayStation;

            } catch (error) {
                resultDiv.innerHTML = "❌ 情報の取得中にエラーが発生しました。";
            } finally {
                btn.disabled = false;
                btn.style.backgroundColor = "#007bff";
            }
        },
        function(err) {
            resultDiv.innerHTML = "⚠️ 位置情報の取得を許可してください。";
            btn.disabled = false;
            btn.style.backgroundColor = "#007bff";
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
};
</script>
"""

st.components.v1.html(location_script, height=300)

st.divider()
st.caption("※最寄り駅は現在地から直線距離で最も近いものを表示します。")
