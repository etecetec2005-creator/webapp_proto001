import streamlit as st

st.set_page_config(page_title="住所取得", layout="centered")
st.title("📍 住所取得ツール")

st.write("下のボタンを押してください。")

# Pythonのf-stringを一切使わず、JSとの衝突をゼロにします
location_script = """
<div id="result" style="font-size:16px; color:#333; padding:15px; background:#f0f2f6; border-radius:10px; border-left: 5px solid #ff4b4b; min-height: 60px; line-height: 1.5;">
    📍 ここに住所が表示されます
</div>

<button id="btn" style="margin-top:20px; padding:15px 24px; background-color:#ff4b4b; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold; width:100%; font-size:16px;">
    現在地から住所を取得
</button>

<script>
document.getElementById('btn').onclick = function() {
    const resultDiv = document.getElementById('result');
    const btn = document.getElementById('btn');
    
    resultDiv.innerText = "解析中...";
    btn.disabled = true;
    btn.style.backgroundColor = "#ccc";

    navigator.geolocation.getCurrentPosition(
        function(pos) {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            // ズームレベル18（詳細）で取得
            const url = "https://nominatim.openstreetmap.org/reverse?format=json&lat=" + lat + "&lon=" + lon + "&zoom=18&addressdetails=1&accept-language=ja";
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data && data.display_name) {
                        // 1. フル住所を取得 (例: "日本, 〒532-0004, 大阪府, 大阪市, 淀川区, 宮原三丁目")
                        let rawAddr = data.display_name;
                        
                        // 2. 不要なパーツを「空文字」に置換して消し去る（正規表現）
                        // 日本、Japan、郵便番号、都道府県、国名を削除
                        let cleanAddr = rawAddr
                            .replace(/日本|Japan/g, "")
                            .replace(/〒[0-9-]+/g, "")
                            .replace(/[a-zA-Z]/g, "") // 英字削除
                            .replace(/大阪府|東京都|京都府|兵庫県|./, "") // 最初の「.」などを掃除
                            .replace(/[, 　]/g, ""); // カンマとスペースを削除
                            
                        // 3. もし「大阪府」が削りきれなかった場合の予備処理
                        cleanAddr = cleanAddr.replace("大阪府", "").replace("兵庫県", "").replace("京都府", "");

                        // 4. 文字の並びを「市区町村〜」に整える
                        // OSMは「番地, 町名, 区, 市...」の順で返すことがあるため、
                        // もし「大阪市」が後ろにあるなら、前後を入れ替える処理はせず、
                        // 全パーツをバラして逆順に結合する
                        let parts = data.display_name.split(',').map(s => s.trim());
                        let filtered = parts.filter(p => !/日本|Japan|〒|府|県/.test(p));
                        let finalResult = filtered.reverse().join("");

                        resultDiv.innerHTML = "<strong>整形後の住所:</strong><br>" + finalResult;
                    } else {
                        resultDiv.innerText = "住所が見つかりませんでした。";
                    }
                    btn.disabled = false;
                    btn.style.backgroundColor = "#ff4b4b";
                })
                .catch(err => {
                    resultDiv.innerText = "エラー: 住所の取得に失敗しました。";
                    btn.disabled = false;
                    btn.style.backgroundColor = "#ff4b4b";
                });
        },
        function(err) {
            resultDiv.innerText = "位置情報の取得を許可してください。";
            btn.disabled = false;
            btn.style.backgroundColor = "#ff4b4b";
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
};
</script>
"""

st.components.v1.html(location_script, height=280)

st.info("※OSMの地図データに町名が登録されていない地点では、これ以上詳細な住所が出ない場合があります。その場合はGoogle Maps APIなどの有料サービスが必要になります。")
