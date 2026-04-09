import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os
import base64

# --- セキュリティ設定 ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが設定されていません。StreamlitのSecretsに登録してください。")
    st.stop()

genai.configure(api_key=api_key)

# --- 基本設定 ---
st.set_page_config(page_title="e-Photo_000", layout="centered")
st.title("📸 e-Photo")

# カメラ入力
img_file = st.file_uploader("撮影または画像を選択（高画質）", type=["jpg", "jpeg", "png"], accept_magic_file=True)

if img_file:
    # 1. 画像の読み込みとリサイズ準備
    img = Image.open(img_file)
    width, height = img.size 
    st.image(img, caption="解析・保存プロセスを実行中...")

    # 2. AI解析（Gemini 2.5 Flash-Lite）
    ai_title = "名称未設定"
    with st.spinner("Gemini 2.5 Flash-Lite が解析中..."):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            # プロンプトの変更：20文字以内、電気設備・文字情報への留意事項を追加
            prompt = """この写真の内容を分析し、20文字以内の日本語タイトルを1つだけ出力してください。
【留意事項】写真には電気設備が写っている場合が多くあります。その場合、特に写実的で具体的なタイトルとしてください。
写真に文字や数字が写っている場合はタイトルにその内容も加えてください。
ただし、その文字や数字だけのタイトルにはしないでください。"""
            
            response = model.generate_content([prompt, img])
            if response and response.text:
                ai_title = response.text.strip().replace("\n", "").replace("/", "-").replace(" ", "")
        except Exception as e:
            st.warning(f"⚠️ AI解析をスキップしました: {e}")

    # 3. 画像のBase64変換
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=100, subsampling=0)
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # 4. 全自動JavaScript（住所・駅取得 ＋ 文字埋め込み ＋ JPG保存）
    st.success(f"タイトル確定: {ai_title}")
    
    auto_save_script = f"""
    <div id="status" style="font-size:12px; color:gray; padding:10px; background:#f9f9f9; border-radius:5px;">
        📍 位置情報と駅名を特定して、画像を保存します...
    </div>
    <script>
    (async function() {{
        const status = document.getElementById('status');
        const aiTitle = "{ai_title}";
        const imgBase64 = "data:image/jpeg;base64,{img_str}";
        const oW = {width};
        const oH = {height};

        const now = new Date();
        const dateStr = now.getFullYear().toString().slice(-2) + 
                        ('0' + (now.getMonth() + 1)).slice(-2) + 
                        ('0' + now.getDate()).slice(-2) + 
                        ('0' + now.getHours()).slice(-2) + 
                        ('0' + now.getMinutes()).slice(-2);

        navigator.geolocation.getCurrentPosition(
            async (pos) => {{
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                let finalAddr = "住所不明";
                let stationName = "駅名不明";

                try {{
                    // 1. 住所取得：取りこぼしを防ぐため全パーツをチェック
                    const addrRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${{lat}}&lon=${{lon}}&zoom=18&addressdetails=1&accept-language=ja`);
                    const addrData = await addrRes.json();
                    
                    if (addrData && addrData.address) {{
                        const a = addrData.address;
                        
                        // 候補となるパーツを順番に並べる
                        const parts = [
                            a.city || a.town || a.village || "",
                            a.city_district || "",
                            a.suburb || "",
                            a.neighbourhood || "",
                            a.road || ""
                        ];
                        
                        // 空文字を除去し、重複を排除して結合
                        finalAddr = [...new Set(parts.filter(p => p !== ""))].join("");
                        finalAddr = finalAddr.replace(/日本|〒[0-9-]+/g, "").trim();
                    }}

                    // 2. 最寄り駅取得
                    const stRes = await fetch(`https://express.heartrails.com/api/json?method=getStations&x=${{lon}}&y=${{lat}}`);
                    const stData = await stRes.json();
                    if (stData.response && stData.response.station && stData.response.station.length > 0) {{
                        stationName = stData.response.station[0].name + "駅";
                    }}
                }} catch (e) {{
                    console.error(e);
                }}
                processAndSave(finalAddr, stationName);
            }},
            (err) => {{ processAndSave("位置情報なし", "駅名なし"); }},
            {{ enableHighAccuracy: true, timeout: 7000 }}
        );

        function processAndSave(addr, stn) {{
            const displayText = aiTitle + " _ " + addr + " _ " + stn;
            const safeAddr = addr.replace(/[/\\\\?%*:|"<>]/g, '-');
            const fileName = dateStr + "_" + aiTitle + "_" + safeAddr + "_" + stn + ".jpg";

            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = function() {{
                canvas.width = oW;
                canvas.height = oH;
                ctx.drawImage(img, 0, 0, oW, oH);
                
                const fontSize = Math.floor(oH / 30); 
                ctx.font = "bold " + fontSize + "px sans-serif";
                ctx.textBaseline = "top";
                const padding = fontSize / 2;
                const textWidth = ctx.measureText(displayText).width;
                
                ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
                ctx.fillRect(20, 20, textWidth + (padding * 2), fontSize + (padding * 2));
                
                ctx.fillStyle = "white";
                ctx.fillText(displayText, 20 + padding, 20 + padding);
                
                const link = document.createElement('a');
                link.download = fileName;
                link.href = canvas.toDataURL('image/jpeg', 1.0);
                link.click();
                
                status.style.color = "green";
                status.innerText = "✅ 保存完了: " + fileName;
            }};
            img.src = imgBase64;
        }}
    }})();
    </script>
    """
    st.components.v1.html(auto_save_script, height=120)
