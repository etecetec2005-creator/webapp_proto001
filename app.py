import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("📍 住所取得ツール")

st.write("ボタンを押すと、現在地の詳細な住所を表示します。")

# JavaScriptコード（住所取得ロジックを大幅強化）
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
    resultDiv.innerText = "位置情報を取得中...";

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
                const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&accept-language=ja`;
                const response = await fetch(url);
                const data = await response.json();
                
                if (data && data.address) {
                    const a = data.address;
                    
                    // 1. 候補となる地名パーツをすべて配列に入れる
                    // 市、区、町名、近隣、道路名など、OSMが返しうる全項目を網羅
                    const parts = [
                        a.city || a.town || a.village || "",
                        a.city_district || "",
                        a.suburb || "",
                        a.neighbourhood || "",
                        a.quarter || "",
                        a.road || ""
                    ];

                    // 2. 空の項目を除去し、重複を排除（ユニークな値だけ残す）
                    const uniqueParts = [...new Set(parts.filter(p => p !== ""))];
                    
                    // 3. 結合して表示用文字列を作成
                    let formattedAddr = uniqueParts.join("");

                    // 4. 万が一まだ短い場合、display_nameから不要語を除去して抽出（最終手段）
                    if (formattedAddr.length < 6 && data.display_name) {
                        let fullParts = data.display_name.split(',').map(p => p.trim());
                        const exclude = ["日本", "Japan", "〒", "大阪府", "532-0004"];
                        formattedAddr = fullParts
                            .filter(p => !exclude.some(k => p.includes(k)))
                            .reverse()
                            .join("");
                    }

                    resultDiv.innerHTML = `<strong>整形後の住所:</strong><br>${formattedAddr}`;
                } else {
                    resultDiv.innerText = "住所データが見つかりませんでした。";
                }
            } catch (error) {
                console.error(error);
                resultDiv.innerText = "エラー: 住所の取得に失敗しました。";
            }
        },
        (err) => {
            resultDiv.innerText = "位置情報の利用を許可してください。";
        },
        {{ enableHighAccuracy: true, timeout: 10000 }}
    );
}
</script>
"""

# HTMLを表示
st.components.v1.html(location_script, height=200)

st.divider()
st.caption("※GPS信号の届きにくい場所では『大阪市淀川区』までしか特定できない場合があります。")
