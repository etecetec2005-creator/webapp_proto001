import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps
import io
import os
import base64

# --- セキュリティ設定 ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが設定されていません。Streamlitに登録してください。")
    st.stop()

genai.configure(api_key=api_key)

# --- サイドバーによる機能選択 ---
st.sidebar.title("メニュー切替")
app_mode = st.sidebar.selectbox(
    "使用する機能を選択してください",
    ["e-Photo📝黒板", "【テスト版】e-Finder"]
)

# --- 1. e-Photo📝黒板 モード ---
if app_mode == "e-Photo📝黒板":
    st.title("📸 e-Photo📝黒板だよ")

    url_params = st.query_params
    initial_project_name = url_params.get("project_name", "")
    if "project_name" not in st.session_state:
        st.session_state["project_name"] = initial_project_name

    input_val = st.text_input(
        "工事件名を入力してください",
        value=st.session_state["project_name"]
    )

    if input_val != st.session_state["project_name"]:
        st.session_state["project_name"] = input_val
        st.query_params["project_name"] = input_val
        st.rerun()

    st.markdown("<style>div[role='radiogroup'] > label:last-child {margin-left: auto !important; border-left: 1px solid #ddd; padding-left: 15px;}</style>", unsafe_allow_html=True)
    board_position = st.radio("黒板の配置位置", ["左下", "右下", "左上", "右上", "黒板なし"], horizontal=True)

    if "uploader_key_eb" not in st.session_state: st.session_state["uploader_key_eb"] = 0
    if st.button("🔄 画面をリセット"):
        for key in list(st.session_state.keys()):
            if key not in ["project_name", "uploader_key_eb"]: del st.session_state[key]
        st.session_state["uploader_key_eb"] += 1
        st.rerun()

    if not st.session_state["project_name"]:
        st.warning("工事件名を入力してください。"); st.stop()

    img_file = st.file_uploader("撮影/選択", type=["jpg","jpeg","png"], key=f"eb_{st.session_state['uploader_key_eb']}")

    if img_file:
        raw_img = Image.open(img_file)
        img = ImageOps.exif_transpose(raw_img)
        file_size_mb = img_file.size / (1024 * 1024)
        if file_size_mb >= 1.0:
            img = img.resize((img.size[0]//2, img.size[1]//2), Image.Resampling.LANCZOS)
        
        st.image(img, use_container_width=True)
        
        ai_title = ""
        with st.spinner("分析中..."):
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            res = model.generate_content(["20文字以内の日本語タイトルを1つ出力してください。", img])
            ai_title = res.text.strip().replace("\n","").replace("/","-") if res else "解析不可"

        buffered = io.BytesIO(); img.save(buffered, format="JPEG", quality=85)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        auto_save_eb = f"""
        <div id="st_eb" style="font-size:12px; color:gray; padding:10px;">📍 処理中...</div>
        <script>
        (async function() {{
            const st = document.getElementById('st_eb');
            const pj = "{st.session_state['project_name']}";
            const aiT = "{ai_title}";
            const imgB64 = "data:image/jpeg;base64,{img_str}";
            const oW = {img.size[0]}; const oH = {img.size[1]};
            const pos = "{board_position}";
            const now = new Date();
            const dateF = now.getFullYear().toString().slice(-2) + ('0'+(now.getMonth()+1)).slice(-2) + ('0'+now.getDate()).slice(-2) + ('0'+now.getHours()).slice(-2) + ('0'+now.getMinutes()).slice(-2);
            const dateS = now.getFullYear() + "/" + ('0'+(now.getMonth()+1)).slice(-2) + "/" + ('0'+now.getDate()).slice(-2);

            navigator.geolocation.getCurrentPosition(async (p) => {{
                let adr = "住所不明"; let stn = "駅名不明";
                try {{
                    const r = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${{p.coords.latitude}}&lon=${{p.coords.longitude}}&addressdetails=1`,{{headers:{{'Accept-Language':'ja'}}}});
                    const d = await r.json(); if(d.address) adr = (d.address.city||d.address.town||"")+(d.address.suburb||d.address.village||"")+(d.address.road||"")+(d.address.house_number||"");
                    const s = await fetch(`https://express.heartrails.com/api/json?method=getStations&x=${{p.coords.longitude}}&y=${{p.coords.latitude}}`);
                    const sd = await s.json(); if(sd.response.station) stn = sd.response.station[0].name + "駅";
                }} catch(e){{}}
                
                const cv = document.createElement('canvas'); const ctx = cv.getContext('2d'); const i = new Image();
                i.onload = function() {{
                    cv.width = oW; cv.height = oH; ctx.drawImage(i,0,0,oW,oH);
                    if(pos!=="黒板なし"){{
                        const bW=oW*0.3; const bH=bW*0.75; const m=10; let bX,bY;
                        if(pos==="左下"){{bX=m;bY=oH-bH-m}}else if(pos==="右下"){{bX=oW-bW-m;bY=oH-bH-m}}else if(pos==="左上"){{bX=m;bY=m}}else{{bX=oW-bW-m;bY=m}}
                        ctx.fillStyle="#004d40"; ctx.fillRect(bX,bY,bW,bH); ctx.strokeStyle="white"; ctx.lineWidth=2; ctx.strokeRect(bX+3,bY+3,bW-6,bH-6);
                        ctx.beginPath(); ctx.strokeStyle="white"; for(let j=1;j<4;j++){{ctx.moveTo(bX+3,bY+(bH*0.25*j));ctx.lineTo(bX+bW-3,bY+(bH*0.25*j));}}
                        ctx.moveTo(bX+(bW*0.35),bY+3); ctx.lineTo(bX+(bW*0.35),bY+bH-3); ctx.stroke();
                        ctx.fillStyle="white"; const fS=Math.floor(bH/11); ctx.font=fS*0.8+"px sans-serif"; ctx.textBaseline="middle";
                        ["工事件名","工事場所","日　　付","備　　考"].forEach((l,x)=>ctx.fillText(l,bX+8,bY+(bH*(0.125+0.25*x))));
                        [pj, stn, dateS, aiT].forEach((v,x)=>{{
                            if(v.length>10){{
                                ctx.font="bold "+(fS*0.85)+"px sans-serif";
                                ctx.fillText(v.substring(0,10),bX+(bW*0.38),bY+(bH*(0.125+0.25*x))-(fS*0.4));
                                ctx.fillText(v.substring(10,20),bX+(bW*0.38),bY+(bH*(0.125+0.25*x))+(fS*0.5));
                            }}else{{ ctx.font="bold "+fS+"px sans-serif"; ctx.fillText(v,bX+(bW*0.38),bY+(bH*(0.125+0.25*x))); }}
                        }});
                    }}
                    const fN = `${{dateF}}_${{aiT}}_${{adr}}_${{stn}}.jpg`.replace(/[/\\\\?%*:|"<>]/g, '-');
                    const l = document.createElement('a'); l.download=fN; l.href=cv.toDataURL('image/jpeg',0.85); l.click();
                    st.innerText = "✅ 保存完了: " + fN;
                }}; i.src = imgB64;
            }}, (e)=>{{}}, {{enableHighAccuracy:true, timeout:8000}});
        }})();
        </script>
        """
        st.components.v1.html(auto_save_eb, height=130)

# --- 2. 【テスト版】e-Finder モード ---
else:
    st.title("🚉 【テスト版】e-Finder")

    category = st.selectbox(
        "判定カテゴリを選択してください",
        ["すべて", "破損はあるか", "変質はあるか", "変形はあるか", "欠落はあるか", "付着はあるか", "不要な介在物はあるか", "その他"]
    )

    if "uploader_key_ef" not in st.session_state: st.session_state["uploader_key_ef"] = 0
    if st.button("🔄 画面をリセット"):
        for key in list(st.session_state.keys()):
            if key not in ["uploader_key_ef"]: del st.session_state[key]
        st.session_state["uploader_key_ef"] += 1
        st.rerun()

    input_method = st.radio("入力方法", ["カメラで撮影", "画像をアップロード"])
    img_file = st.camera_input("撮影") if input_method == "カメラで撮影" else st.file_uploader("選択", type=["jpg","jpeg","png"], key=f"ef_{st.session_state['uploader_key_ef']}")

    if img_file:
        raw_img = Image.open(img_file)
        img = ImageOps.exif_transpose(raw_img)
        st.image(img, caption="AI解析および黒板合成中...")

        ai_analysis = ""; ai_title = "設備判定"
        with st.spinner("詳細解析中..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash-lite')
                cat_desc = "破損、変質、変形、欠落、付着、不要な介在物のすべて" if category == "すべて" else category
                prompt = f"""前面の設備を詳細に分析してください。
【確認カテゴリ】: {cat_desc}
1. 異常の有無を具体的に判定。2. 箇所・原因・進行度を推測。
結果を100字以内でまとめ、最後に「タイトル：〇〇」と20文字以内で出力してください。"""
                
                response = model.generate_content([prompt, img])
                if response and response.text:
                    full = response.text
                    if "タイトル：" in full:
                        ai_analysis = full.split("タイトル：")[0].strip()
                        ai_title = full.split("タイトル：")[1].strip().replace("\n", "").replace("/", "-")[:20]
                    else: ai_analysis = full
                st.subheader("📋 判定結果")
                st.info(ai_analysis)
            except Exception as e: st.error(f"解析エラー: {e}")

        buffered = io.BytesIO(); img.save(buffered, format="JPEG", quality=95)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        auto_save_ef = f"""
        <div id="st_ef" style="font-size:12px; color:gray; padding:10px;">📍 処理中...</div>
        <script>
        (async function() {{
            const st = document.getElementById('st_ef');
            const aiT = "{ai_title}";
            const aiRes = "{ai_analysis}".replace(/\\n/g, " ");
            const imgB64 = "data:image/jpeg;base64,{img_str}";
            const oW = {img.size[0]}; const oH = {img.size[1]};
            const dateF = new Date().getFullYear().toString().slice(-2) + ('0'+(new Date().getMonth()+1)).slice(-2) + ('0'+new Date().getDate()).slice(-2) + ('0'+new Date().getHours()).slice(-2) + ('0'+new Date().getMinutes()).slice(-2);

            navigator.geolocation.getCurrentPosition(async (p) => {{
                let adr = "住所不明"; let stn = "駅名不明";
                try {{
                    const r = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${{p.coords.latitude}}&lon=${{p.coords.longitude}}&addressdetails=1`,{{headers:{{'Accept-Language':'ja'}}}});
                    const d = await r.json(); if(d.address) adr = (d.address.city||d.address.town||"")+(d.address.suburb||d.address.village||"")+(d.address.road||"")+(d.address.house_number||"");
                    const s = await fetch(`https://express.heartrails.com/api/json?method=getStations&x=${{p.coords.longitude}}&y=${{p.coords.latitude}}`);
                    const sd = await s.json(); if(sd.response.station) stn = sd.response.station[0].name + "駅";
                }} catch(e){{}}

                const cv = document.createElement('canvas'); const ctx = cv.getContext('2d'); const i = new Image();
                i.onload = function() {{
                    const bH = Math.floor(oH * 0.2); // 黒板部分の高さを20%確保
                    cv.width = oW; cv.height = oH + bH;
                    ctx.fillStyle = "white"; ctx.fillRect(0,0,cv.width,cv.height);
                    ctx.drawImage(i,0,0,oW,oH);
                    
                    // 解析用黒板の描画
                    ctx.fillStyle = "#333"; ctx.fillRect(0, oH, oW, bH);
                    ctx.strokeStyle = "white"; ctx.lineWidth = 4; ctx.strokeRect(5, oH+5, oW-10, bH-10);
                    
                    ctx.fillStyle = "white"; 
                    const fS = Math.floor(bH / 4.5);
                    ctx.font = "bold " + fS + "px sans-serif"; ctx.textBaseline = "top";
                    ctx.fillText("【判定結果】 " + aiT, 20, oH + 15);
                    
                    ctx.font = (fS * 0.7) + "px sans-serif";
                    // 分析結果を折り返して描画（簡易版）
                    const words = aiRes.split(""); let line = ""; let y = oH + 15 + fS + 10;
                    for(let n=0; n<words.length; n++){{
                        let testLine = line + words[n];
                        if(ctx.measureText(testLine).width > oW - 40){{
                            ctx.fillText(line, 20, y); line = words[n]; y += (fS * 0.8);
                        }} else {{ line = testLine; }}
                    }}
                    ctx.fillText(line, 20, y);

                    const fN = `${{dateF}}_${{aiT}}_${{adr}}_${{stn}}.jpg`.replace(/[/\\\\?%*:|"<>]/g, '-');
                    const l = document.createElement('a'); l.download=fN; l.href=cv.toDataURL('image/jpeg',0.9); l.click();
                    st.style.color = "green"; st.innerText = "✅ 保存完了: " + fN;
                }}; i.src = imgB64;
            }}, (e)=>{{}}, {{enableHighAccuracy:true, timeout:7000}});
        }})();
        </script>
        """
        st.components.v1.html(auto_save_ef, height=130)
