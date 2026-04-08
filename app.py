import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("📍 住所取得ツール")

st.write("ボタンを押すと、現在の位置情報を取得し「大阪市淀川区宮原三丁目」の形式で表示します。")

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
                // 逆ジオコーディング実行
                const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&accept-language=ja`);
                const data = await response.json();
                
                if (data && data.address) {
                    const a = data.address;
                    
                    // 1. 市・区・町名の各パーツを取得
                    const city = a.city || a.town || a.village || "";
                    const district = a.city_district || "";
                    // 町名（suburb）がなければ neighbourhood、それもなければ road を使用
                    const town = a.suburb || a.neighbourhood || a.road || "";

                    // 2. 「大阪府」や「郵便番号」を除去した綺麗な並びにする
                    // シンプルに 市 + 区 + 町名 を結合
                    let formattedAddr = city + district + town;

                    // 万が一、上記で空の場合のバックアップ（全体の住所文字列から抽出）
                    if (formattedAddr === "" && data.display_name) {
                        formattedAddr = data.display_name.split(',')[0]; 
                    }
                    
                    resultDiv.innerHTML = `<strong>整形後の住所:</strong><br>${formattedAddr}`;
                } else {
                    resultDiv.innerText = "住所データが見つかりませんでした。";
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

st.info("※「宮原三丁目」などの詳細な町名は、GPSの精度や地図データの登録状況により表示されない場合があります。")
