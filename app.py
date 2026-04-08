import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("📍 住所取得ツール")

st.write("ボタンを押すと「大阪市淀川区宮原三丁目」の形式で表示します。")

location_script = """
<div id="result" style="font-size:16px; color:#333; padding:15px; background:#f0f2f6; border-radius:10px; border-left: 5px solid #ff4b4b; min-height: 60px;">
    📍 ここに住所が表示されます
</div>

<button id="btn" style="margin-top:20px; padding:15px 24px; background-color:#ff4b4b; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold; width:100%; font-size:16px;">
    住所を取得
</button>

<script>
document.getElementById('btn').onclick = function() {
    const resultDiv = document.getElementById('result');
    const btn = document.getElementById('btn');
    
    resultDiv.innerText = "解析中...";
    btn.disabled = true;

    navigator.geolocation.getCurrentPosition(
        function(pos) {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const url = "https://nominatim.openstreetmap.org/reverse?format=json&lat=" + lat + "&lon=" + lon + "&zoom=18&addressdetails=1&accept-language=ja";
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data && data.address) {
                        const a = data.address;
                        
                        // 1. 必要なパーツだけを順番に定義
                        const city = a.city || a.town || a.village || "";
                        const district = a.city_district || "";
                        const town = a.suburb || a.neighbourhood || "";

                        // 2. 結合（この時点で 建物名 や 郵便番号 は含まれません）
                        let finalAddr = city + district + town;

                        // 3. もし町名(town)が空で、road(道路名)に丁目が入っている場合の予備処理
                        if (town === "" && a.road) {
                            finalAddr += a.road;
                        }

                        // 不要な「日本」や「郵便番号」が混入した時用の最終クリーニング
                        finalAddr = finalAddr.replace(/日本|〒[0-9-]+/g, "");

                        resultDiv.innerHTML = "<strong>整形後の住所:</strong><br>" + finalAddr;
                    } else {
                        resultDiv.innerText = "住所が見つかりませんでした。";
                    }
                    btn.disabled = false;
                })
                .catch(err => {
                    resultDiv.innerText = "エラーが発生しました。";
                    btn.disabled = false;
                });
        },
        function(err) {
            resultDiv.innerText = "位置情報の取得を許可してください。";
            btn.disabled = false;
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
};
</script>
"""

st.components.v1.html(location_script, height=250)
