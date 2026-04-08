import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("📍 住所取得ツール")

st.write("ボタンを押すと、現在の位置情報を取得し、詳細な住所を表示します。")

# JavaScriptコードを変数に格納
# インデントに注意し、Pythonの構文として正しく認識されるようにします
location_script = """
<div id="result" style="font-size:16px; color:#333; padding:15px; background:#f0f2f6; border-radius:10px; border-left: 5px solid #ff4b4b;">
    📍 ここに住所が表示されます
</div>

<button onclick="getLocation()" style="margin-top:10px; padding:10px 20px; background-color:#ff4b4b; color:white; border:none; border-radius:5px; cursor:pointer;">
    現在地を取得
</button>

<script>
async function getLocation() {
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
                // 逆ジオコーディング実行（OSM Nominatim）
                const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&accept-language=ja`);
                const data = await response.json();
                
                if (data && data.display_name) {
                    // 住所パーツを取得
                    const a = data.address;
                    
                    // 大阪市 + 淀川区 + 町名 を順番に探して結合
                    const city = a.city || a.town || a.village || "";
                    const district = a.city_district || "";
                    const suburb = a.suburb || a.neighbourhood || a.road || "";
                    
                    let formattedAddr = city + district + suburb;

                    // もし上記で空なら、フル住所からフィルタリングして作成
                    if (!formattedAddr) {
                        let parts = data.display_name.split(',').map(p => p.trim());
                        const exclude = ["日本", "〒", "大阪府", "Japan"];
                        formattedAddr = parts.filter(p => !exclude.some(k => p.includes(k))).reverse().join("");
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
            resultDiv.innerText = "位置情報の取得を許可してください（設定を確認してください）。";
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
}
</script>
"""

# HTMLをコンポーネントとして実行
st.components.v1.html(location_script, height=200)

st.divider()
st.caption("※ブラウザの位置情報許可が『ON』である必要があります。")
