import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("📍 住所取得ツール")

st.write("ボタンを押すと、現在の位置情報から住所を特定します。")

# JavaScriptで位置情報を取得し、住所を逆引きする
# Nominatim（OpenStreetMapのサービス）を使用して住所に変換します
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
                // OpenStreetMapのNominatim APIを使用して逆ジオコーディング
                const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&accept-language=ja`);
                const data = await response.json();
                
                if (data && data.display_name) {
                    resultDiv.innerHTML = `<strong>取得した住所:</strong><br>${data.display_name}`;
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

# HTML/JavaScriptを埋め込み
st.components.v1.html(location_script, height=200)

st.info("※ ブラウザで位置情報の利用許可を求められた場合は「許可」を選択してください。")
