import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("住所取得ツール")

st.write("ボタンを押すと「大阪市淀川区宮原三丁目」の形式で表示します。")

# f-string(f""")を使わず、通常の文字列として定義することでPythonのエラーを完全に防ぎます
# 📍などの絵文字は10進数エンティティ &#128205; に置き換えて安全性を高めています
location_script = """
<div id="result" style="font-size:16px; color:#333; padding:15px; background:#f0f2f6; border-radius:10px; border-left: 5px solid #ff4b4b; min-height: 60px;">
    &#128205; ここに住所が表示されます
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
            // 精度を出すためにzoom=18を指定
            const url = "https://nominatim.openstreetmap.org/reverse?format=json&lat=" + lat + "&lon=" + lon + "&zoom=18&addressdetails=1&accept-language=ja";
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data && data.address) {
                        const a = data.address;
                        
                        // 市町村・区の取得
                        const city = a.city || a.town || a.village || "";
                        const district = a.city_district || "";
                        
                        // 町名（宮原三丁目など）は suburb, neighbourhood, road のいずれかに入っていることが多い
                        let town = a.suburb || a.neighbourhood || a.road || "";
                        
                        // 結合（建物名などは含めない）
                        let finalAddr = city + district + town;

                        // 最終的なクリーンアップ（日本などの不要語削除）
                        finalAddr = finalAddr.replace(/日本|〒[0-9-]+|[a-zA-Z]/g, "").trim();

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
