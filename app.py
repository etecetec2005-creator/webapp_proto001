import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("📍 住所取得ツール")

st.write("ボタンを押すと、現在の位置情報を取得し「大阪市淀川区宮原3」の形式で表示します。")

location_script = """
<div id="result" style="font-size:16px; color:#333; padding:15px; background:#f0f2f6; border-radius:10px; border-left: 5px solid #ff4b4b;">
    📍 ここに住所が表示されます
</div>

<button onclick="getLocation()" style="margin-top:10px; padding:10px 20px; background-color:#ff4b4b; color:white; border:none; border-radius:5px; cursor:pointer;">
    現在地を取得
</button>

<script>
function getLocation() {
    const resultDiv = document.getElementById('result');
    resultDiv.innerText = "取得中...";

    if (!navigator.geolocation) {
        resultDiv.innerText = "お使いのブラウザは位置情報に対応していません。";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        async (pos) => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            
            try {
                const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&accept-language=ja`);
                const data = await response.json();
                
                if (data && data.address) {
                    const a = data.address;
                    
                    // 1. 市町村・区の取得
                    const city = a.city || a.town || a.village || "";
                    const district = a.city_district || "";
                    
                    // 2. 町名・丁目部分（複数の候補から取得）
                    let townName = a.suburb || a.neighbourhood || a.quarter || a.road || "";

                    // 3. 漢数字を数字に変換する関数
                    const kanjiMap = {
                        '一丁目': '1', '二丁目': '2', '三丁目': '3', '四丁目': '4', '五丁目': '5',
                        '六丁目': '6', '七丁目': '7', '八丁目': '8', '九丁目': '9', '十丁目': '10',
                        '丁目': '' // 「丁目」自体を消す
                    };
                    
                    for (let key in kanjiMap) {
                        townName = townName.replace(new RegExp(key, 'g'), kanjiMap[key]);
                    }

                    // 結合
                    const formattedAddr = city + district + townName;
                    
                    resultDiv.innerHTML = `<strong>整形後の住所:</strong><br>${formattedAddr}`;
                    console.log("Debug Address Data:", a); // 取得データの中身をブラウザコンソールで確認可能
                } else {
                    resultDiv.innerText = "住所が見つかりませんでした。";
                }
            } catch (error) {
                resultDiv.innerText = "エラー: 住所の取得に失敗しました。";
            }
        },
        (err) => {
            resultDiv.innerText = "位置情報の取得が許可されていないか、タイムアウトしました。";
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
}
</script>
"""

st.components.v1.html(location_script, height=200)

st.divider()
st.caption("※建物内やGPS精度の低い環境では、正確な町名（宮原など）が取得できない場合があります。")
