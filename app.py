import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("📍 住所取得ツール")

st.write("下のボタンを押してください。ブラウザが位置情報の許可を求めたら「許可」してください。")

# f-stringを使わず、純粋な文字列として定義することでJavaScriptとの衝突を防ぎます
location_script = """
<div id="result" style="font-size:16px; color:#333; padding:15px; background:#f0f2f6; border-radius:10px; border-left: 5px solid #ff4b4b; min-height: 50px;">
    📍 ここに住所が表示されます
</div>

<button id="btn" style="margin-top:20px; padding:12px 24px; background-color:#ff4b4b; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">
    現在地から住所を取得する
</button>

<script>
document.getElementById('btn').onclick = function() {
    const resultDiv = document.getElementById('result');
    const btn = document.getElementById('btn');
    
    resultDiv.innerText = "位置情報を取得中...（数秒かかります）";
    btn.disabled = true;
    btn.style.backgroundColor = "#ccc";

    if (!navigator.geolocation) {
        resultDiv.innerText = "エラー: お使いのブラウザは位置情報に対応していません。";
        btn.disabled = false;
        btn.style.backgroundColor = "#ff4b4b";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function(pos) {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const url = "https://nominatim.openstreetmap.org/reverse?format=json&lat=" + lat + "&lon=" + lon + "&accept-language=ja";
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data && data.address) {
                        const a = data.address;
                        // 市・区・町名を順番に結合
                        const city = a.city || a.town || a.village || "";
                        const district = a.city_district || "";
                        const town = a.suburb || a.neighbourhood || a.quarter || a.road || "";
                        
                        let formattedAddr = city + district + town;

                        // もし空っぽならフル住所から「日本」などを除いて表示
                        if (formattedAddr.length < 3 && data.display_name) {
                            formattedAddr = data.display_name.replace(/日本, |〒[0-9-]+, |大阪府, /g, "");
                        }

                        resultDiv.innerHTML = "<strong>整形後の住所:</strong><br>" + formattedAddr;
                    } else {
                        resultDiv.innerText = "住所が見つかりませんでした。";
                    }
                    btn.disabled = false;
                    btn.style.backgroundColor = "#ff4b4b";
                })
                .catch(err => {
                    resultDiv.innerText = "通信エラーが発生しました。";
                    btn.disabled = false;
                    btn.style.backgroundColor = "#ff4b4b";
                });
        },
        function(err) {
            resultDiv.innerText = "位置情報の取得が拒否されました。ブラウザの設定で許可してください。";
            btn.disabled = false;
            btn.style.backgroundColor = "#ff4b4b";
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
};
</script>
"""

# HTMLを表示（高さを少し広めに設定）
st.components.v1.html(location_script, height=250)

st.divider()
st.caption("※iPhone/Android等のスマホでも、ブラウザの位置情報をONにすれば動作します。")
