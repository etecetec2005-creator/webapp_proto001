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
    resultDiv.innerText = "取得中...";import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("📍 住所取得ツール")

st.write("ボタンを押すと、現在の位置情報を取得し、詳細な住所を表示します。")

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
                // 逆ジオコーディング実行（OSM Nominatim）
                const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&accept-language=ja`);
                const data = await response.json();
                
                if (data && data.display_name) {
                    // 1. フル住所（display_name）を取得
                    // 例: "日本, 〒532-0004, 大阪府, 大阪市, 淀川区, 宮原三丁目" 
                    // ※OSMの仕様で、カンマ区切りの順序が逆転している場合があります
                    let parts = data.display_name.split(',').map(p => p.trim());

                    // 2. 不要なワードを除外（日本、郵便番号、都道府県、国名など）
                    const excludeKeywords = ["日本", "〒", "大阪府", "Japan"];
                    let filteredParts = parts.filter(p => !excludeKeywords.some(key => p.includes(key)));

                    // 3. 順序を整えて結合（「大阪市」「淀川区」「宮原三丁目」の順にする）
                    // 多くの場合は配列を逆順（reverse）にすると自然な日本語住所になります
                    let formattedAddr = filteredParts.reverse().join("");

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

st.info("※これでも表示されない場合は、現在地のGPS精度が低く、地図データ上で町名が特定できていない可能性があります。")

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
