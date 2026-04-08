import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("📍 住所取得ツール")

st.write("ボタンを押すと、現在の位置情報を「大阪市淀川区宮原3」のような形式で取得します。")

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
                    
                    // 各パーツを取得（存在しない場合は空文字）
                    const city = a.city || a.town || a.village || "";
                    const district = a.city_district || "";
                    let suburb = a.suburb || a.neighbourhood || "";

                    // 「三丁目」などを「3」に置換し、余計な「丁目」を消す簡易的な変換
                    suburb = suburb.replace(/一丁目/g, '1')
                                   .replace(/二丁目/g, '2')
                                   .replace(/三丁目/g, '3')
                                   .replace(/四丁目/g, '4')
                                   .replace(/五丁目/g, '5')
                                   .replace(/六丁目/g, '6')
                                   .replace(/七丁目/g, '7')
                                   .replace(/八丁目/g, '8')
                                   .replace(/九丁目/g, '9')
                                   .replace(/丁目/g, '');

                    const formattedAddr = city + district + suburb;
                    
                    resultDiv.innerHTML = `<strong>整形後の住所:</strong><br>${formattedAddr}`;
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
st.info("※OpenStreetMapのデータ構造により、場所によっては表記がわずかに異なる場合があります。")
