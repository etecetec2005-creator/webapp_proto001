import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("📍 住所取得ツール")

st.write("ボタンを押すと、現在地の詳細な住所を表示します。")

# JavaScriptコード（Pythonのf-string用に波括弧を二重化して修正）
location_script = f"""
<div id="result" style="font-size:16px; color:#333; padding:15px; background:#f0f2f6; border-radius:10px; border-left: 5px solid #ff4b4b;">
    📍 ここに住所が表示されます
</div>

<button id="get-pos-btn" onclick="getLocation()" style="margin-top:10px; padding:10px 20px; background-color:#ff4b4b; color:white; border:none; border-radius:5px; cursor:pointer;">
    現在地を取得
</button>

<script>
async function getLocation() {{
    const resultDiv = document.getElementById('result');
    const btn = document.getElementById('get-pos-btn');
    
    resultDiv.innerText = "位置情報を取得中...";
    btn.disabled = true;
    btn.style.backgroundColor = "#ccc";

    if (!navigator.geolocation) {{
        resultDiv.innerText = "お使いのブラウザは位置情報に対応していません。";
        btn.disabled = false;
        btn.style.backgroundColor = "#ff4b4b";
        return;
    }}

    navigator.geolocation.getCurrentPosition(
        async (pos) => {{
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            
            try {{
                const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${{lat}}&lon=${{lon}}&accept-language=ja`;
                const response = await fetch(url);
                const data = await response.json();
                
                if (data && data.address) {{
                    const a = data.address;
                    
                    // 市、区、町名（suburb/neighbourhood/road）を抽出
                    const city = a.city || a.town || a.village || "";
                    const district = a.city_district || "";
                    const town = a.suburb || a.neighbourhood || a.quarter || a.road || "";

                    let formattedAddr = city + district + town;

                    // バックアップ：もし短すぎたらフル住所から抽出
                    if (formattedAddr.length < 5 && data.display_name) {{
                        let fullParts = data.display_name.split(',').map(p => p.trim());
                        const exclude = ["日本", "Japan", "〒", "大阪府"];
                        formattedAddr = fullParts
                            .filter(p => !exclude.some(k => p.includes(k)))
                            .reverse()
                            .join("");
                    }}

                    resultDiv.innerHTML = `<strong>整形後の住所:</strong><br>${{formattedAddr}}`;
                }} else {{
                    resultDiv.innerText = "住所データが見つかりませんでした。";
                }}
            {{ catch (error) {{
                resultDiv.innerText = "エラー: 住所の取得に失敗しました。";
            }}
        }},
        (err) => {{
            resultDiv.innerText = "位置情報の利用を許可してください（ブラウザの設定を確認してください）。";
        }},
        {{ enableHighAccuracy: true, timeout: 10000 }}
    );
    
    // ボタンを再度有効化（数秒後）
    setTimeout(() => {{
        btn.disabled = false;
        btn.style.backgroundColor = "#ff4b4b";
    }}, 3000);
}}
</script>
"""

# HTMLを表示
st.components.v1.html(location_script, height=200)

st.divider()
st.info("ボタンが反応しない場合は、ページを再読み込み（リロード）してからお試しください。")
