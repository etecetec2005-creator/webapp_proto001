import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps
import io
import os
import base64

# --- セキュリティ設定 ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが設定されていません。StreamlitのSecretsに登録してください。")
    st.stop()

genai.configure(api_key=api_key)

# --- サイドバーによる機能選択 ---
st.sidebar.title("メニュー切替")
app_mode = st.sidebar.selectbox(
    "使用する機能を選択してください",
    ["e-Photo📝黒板", "設備状態チェッカー"]
)

# --- 1. e-Photo📝黒板 モード ---
if app_mode == "e-Photo📝黒板":
    st.set_page_config(page_title="e-Photo📝黒板", layout="centered")
    st.title("📸 e-Photo📝黒板")

    # URLパラメータ保持
    url_params = st.query_params
    initial_project_name = url_params.get("project_name", "")
    if "project_name" not in st.session_state:
        st.session_state["project_name"] = initial_project_name

    input_val = st.text_input(
        "工事件名を入力してください（URLに保存されます）",
        value=st.session_state["project_name"],
        placeholder="例：〇〇ビル電気設備工事"
    )

    if input_val != st.session_state["project_name"]:
        st.session_state["project_name"] = input_val
        st.query_params["project_name"] = input_val
        st.rerun()

    # 黒板配置設定
    st.markdown("""
        <style>
        div[role="radiogroup"] > label:last-child {
            margin-left: auto !important;
            border-left: 1px solid #ddd;
            padding-left: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    board_position = st.radio(
        "黒板の配置位置を選択してください",
        ["左下", "右下", "左上", "右上", "黒板なし"],
        index=0,
        horizontal=True
    )

    if "uploader_key_eb" not in st.session_state:
        st.session_state["uploader_key_eb"] = 0

    def reset_eb():
        preserved = ["project_name", "uploader_key_eb"]
        for key in list(st.session_state.keys()):
            if key not in preserved:
                del st.session_state[key]
        st.session_state["uploader_key_eb"] += 1
        st.rerun()

    if st.button("🔄 画面をリセットして最初に戻る", key="btn_reset_eb"):
        reset_eb()

    if not st.session_state["project_name"]:
        st.warning("⚠️ 撮影の前に、ページ上部で「工事件名」を入力してください。")
        st.stop()

    img_file = st.file_uploader(
        "撮影または画像を選択", 
        type=["jpg", "jpeg", "png"], 
        key=f"uploader_eb_{st.session_state['uploader_key_eb']}",
        accept_multiple_files=False
    )

    if img_file:
        try:
            file_size_mb = img_file.size / (1024 * 1024)
            raw_img = Image.open(img_file)
            img = ImageOps.exif_transpose(raw_img)
            original_width, original_height = img.size
            
            if file_size_mb >= 1.0:
                new_width = original_width // 2
                new_height = original_height // 2
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resize_msg = f"⚠️ リサイズ完了 ({file_size_mb:.2f}MB → 1/2)"
            else:
                new_width, new_height = original_width, original_height
                resize_msg = f"✅ オリジナル維持 ({file_size_mb:.2f}MB)"
            
            st.image(img, caption=f"{resize_msg} : {new_width}x{new_height}", use_container_width=True)

            ai_title = "" 
            with st.spinner("分析中..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash-lite')
                    prompt = "この写真の内容を分析し、20文字以内の日本語タイトルを1つだけ出力してください。"
                    response = model.generate_content([prompt, img])
                    if response and response.text:
                        ai_title = response.text.strip().replace("\n", "").replace("/", "-").replace(" ", "")
                except: ai_title = "解析不可"

            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=85) 
            img_str = base64.b64encode(buffered.getvalue()).decode()

            auto_save_script = f"""
            <div id="status_eb" style="font-size:12px; color:gray; padding:10px; background:#f9f9f9; border-radius:5px; border-left: 5px solid #2e7d32; margin-top: 10px;">
                📍 処理を開始します...
            </div>
            <script>
            (async function() {{
                const status = document.getElementById('status_eb');
                const projectName = "{st.session_state['project_name']}";
                const aiTitle = "{ai_title}";
                const imgBase64 = "data:image/jpeg;base64,{img_str}";
                const oW = {new_width};
                const oH = {new_height};
                const posSetting = "{board_position}";

                const now = new Date();
                const fileDateStr = now.getFullYear().toString().slice(-2) + ('0' + (now.getMonth() + 1)).slice(-2) + ('0' + now.getDate()).slice(-2) + ('0' + now.getHours()).slice(-2) + ('0' + now.getMinutes()).slice(-2);
                const dateStr = now.getFullYear() + "/" + ('0' + (now.getMonth() + 1)).slice(-2) + "/" + ('0' + now.getDate()).slice(-2);

                navigator.geolocation.getCurrentPosition(async (pos) => {{
                    let addrStr = "住所不明"; let stnName = "駅名不明";
                    try {{
                        const aRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${{pos.coords.latitude}}&lon=${{pos.coords.longitude}}&addressdetails=1`, {{headers:{{'Accept-Language':'ja'}}}});
                        const aD = await aRes.json();
                        if(aD.address){{
                            const a = aD.address;
                            addrStr = (a.city||a.town||a.city_district||"") + (a.suburb||a.neighbourhood||a.village||a.subdistrict||"") + (a.road||"") + (a.house_number||"");
                        }}
                        const sRes = await fetch(`https://express.heartrails.com/api/json?method=getStations&x=${{pos.coords.longitude}}&y=${{pos.coords.latitude}}`);
                        const sD = await sRes.json();
                        if(sD.response.station) stnName = sD.response.station[0].name + "駅";
                    }} catch(e){{}}
                    
                    const canvas = document.createElement('canvas'); const ctx = canvas.getContext('2d'); const i = new Image();
                    i.onload = function() {{
                        canvas.width = oW; canvas.height = oH; ctx.drawImage(i, 0, 0, oW, oH);
                        if(posSetting !== "黒板なし"){{
                            const bW = oW*0.3; const bH = bW*0.75; const m = 10;
                            let bX, bY;
                            if(posSetting==="左下"){{bX=m; bY=oH-bH-m}} else if(posSetting==="右下"){{bX=oW-bW-m; bY=oH-bH-m}} else if(posSetting==="左上"){{bX=m; bY=m}} else {{bX=oW-bW-m; bY=m}}
                            ctx.fillStyle="#004d40"; ctx.fillRect(bX,bY,bW,bH); ctx.strokeStyle="white"; ctx.lineWidth=2; ctx.strokeRect(bX+3,bY+3,bW-6,bH-6);
                            ctx.beginPath(); ctx.strokeStyle="white";
                            for(let j=1;j<4;j++){{ ctx.moveTo(bX+3,bY+(bH*0.25*j)); ctx.lineTo(bX+bW-3,bY+(bH*0.25*j)); }}
                            ctx.moveTo(bX+(bW*0.35),bY+3); ctx.lineTo(bX+(bW*0.35),bY+bH-3); ctx.stroke();
                            ctx.fillStyle="white"; const fS = Math.floor(bH/11); ctx.font = fS*0.8+"px sans-serif"; ctx.textBaseline="middle";
                            const labels = ["工事件名","工事場所","日　　付","備　　考"];
                            labels.forEach((l,idx)=>ctx.fillText(l,bX+8,bY+(bH*(0.125+0.25*idx))));
                            const vals = [projectName, stnName, dateStr, aiTitle];
                            vals.forEach((v,idx)=>{{
                                if(v.length>10){{
                                    ctx.font="bold "+(fS*0.85)+"px sans-serif";
                                    ctx.fillText(v.substring(0,10),bX+(bW*0.38),bY+(bH*(0.125+0.25*idx))-(fS*0.4));
                                    ctx.fillText(v.substring(10,20),bX+(bW*0.38),bY+(bH*(0.125+0.25*idx))+(fS*0.5));
                                }} else {{
                                    ctx.font="bold "+fS+"px sans-serif";
                                    ctx.fillText(v,bX+(bW*0.38),bY+(bH*(0.125+0.25*idx)));
                                }}
                            }});
                        }}
                        const dN = `${{fileDateStr}}_${{aiTitle}}_${{addrStr}}_${{stnName}}.jpg`.replace(/[/\\\\?%*:|"<>]/g, '-');
                        const l = document.createElement('a'); l.download=dN; l.href=canvas.toDataURL('image/jpeg',0.85); l.click();
                        status.innerText = "✅ 保存完了: " + dN;
                    }};
                    i.src = imgBase64;
                }}, (err)=>{{}}, {{enableHighAccuracy:true, timeout:8000}});
            }})();
            </script>
            """
            st.components.v1.html(auto_save_script, height=130)
        except Exception as e: st.error(f"エラー: {e}")

# --- 2. 設備状態チェッカー モード ---
else:
    st.set_page_config(page_title="Railway Electric Facility Checker", layout="centered")
    st.title("🚉 設備の状態は？")

    category = st.selectbox(
        "判定カテゴリを選択してください",
        ["すべて", "破損はあるか（損傷、き裂、折損、切れ など）", "変質はあるか（腐食、劣化、さび など）", "変形はあるか（わん曲、ねじれ、傾斜 など）", "欠落はあるか（脱落、ゆるみ など）", "付着はあるか（汚損、漏油、漏水 など）", "不要な介在物はあるか", "その他"]
    )

    if "uploader_key_rc" not in st.session_state:
        st.session_state["uploader_key_rc"] = 0

    def reset_rc():
        preserved = ["uploader_key_rc"]
        for key in list(st.session_state.keys()):
            if key not in preserved:
                del st.session_state[key]
        st.session_state["uploader_key_rc"] += 1
        st.rerun()

    if st.button("🔄 画面をリセットして最初に戻る", key="btn_reset_rc"):
        reset_rc()

    input_method = st.radio("入力方法を選択してください", ["カメラで撮影", "画像をアップロード"])
    img_file = None
    if input_method == "カメラで撮影":
        img_file = st.camera_input("設備を撮影", key=f"rc_cam_{st.session_state['uploader_key_rc']}")
    else:
        img_file = st.file_uploader("画像を選択してください", type=["jpg", "jpeg", "png"], key=f"rc_up_{st.session_state['uploader_key_rc']}")

    if img_file:
        raw_img = Image.open(img_file)
        img = ImageOps.exif_transpose(raw_img)
        width, height = img.size 
        st.image(img, caption="解析・保存プロセスを実行中...")

        ai_analysis = ""; ai_title = "設備判定"
        with st.spinner("AIが詳細に解析中..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash-lite')
                prompt = f"写真の設備を観察し、カテゴリ【{category}】に関して100字以内で分析してください。最後に「タイトル：〇〇」と20文字以内で出力してください。"
                response = model.generate_content([prompt, img])
                if response and response.text:
                    full = response.text
                    if "タイトル：" in full:
                        ai_analysis = full.split("タイトル：")[0].strip()
                        ai_title = full.split("タイトル：")[1].strip().replace("\n", "").replace("/", "-")[:20]
                    else: ai_analysis = full
                st.subheader("📋 判定結果")
                st.write(ai_analysis)
            except Exception as e: st.error(f"解析エラー: {e}")

        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=100)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        auto_save_script_rc = f"""
        <div id="status_rc" style="font-size:12px; color:gray; padding:10px; background:#f9f9f9; border-radius:5px;">
            📍 位置情報を特定して画像を保存します...
        </div>
        <script>
        (async function() {{
            const status = document.getElementById('status_rc');
            const aiTitle = "{ai_title}";
            const imgBase64 = "data:image/jpeg;base64,{img_str}";
            const oW = {width}; const oH = {height};
            const now = new Date();
            const dateStr = now.getFullYear().toString().slice(-2) + ('0'+(now.getMonth()+1)).slice(-2) + ('0'+now.getDate()).slice(-2) + ('0'+now.getHours()).slice(-2) + ('0'+now.getMinutes()).slice(-2);

            navigator.geolocation.getCurrentPosition(async (pos) => {{
                let addrStr = "住所不明"; let stnName = "駅名不明";
                try {{
                    const aRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${{pos.coords.latitude}}&lon=${{pos.coords.longitude}}&addressdetails=1`, {{headers:{{'Accept-Language':'ja'}}}});
                    const aD = await aRes.json();
                    if(aD.address){{
                        const a = aD.address;
                        addrStr = (a.city||a.town||a.city_district||"") + (a.suburb||a.neighbourhood||a.village||a.subdistrict||"") + (a.road||"") + (a.house_number||"");
                    }}
                    const sRes = await fetch(`https://express.heartrails.com/api/json?method=getStations&x=${{pos.coords.longitude}}&y=${{pos.coords.latitude}}`);
                    const sD = await sRes.json();
                    if(sD.response.station) stnName = sD.response.station[0].name + "駅";
                }} catch(e){{}}

                const canvas = document.createElement('canvas'); const ctx = canvas.getContext('2d'); const i = new Image();
                i.onload = function() {{
                    canvas.width = oW; canvas.height = oH; ctx.drawImage(i, 0, 0, oW, oH);
                    const fS = Math.floor(oH / 35); ctx.font = "bold " + fS + "px sans-serif"; ctx.textBaseline = "top";
                    const display = aiTitle + " _ " + addrStr + " _ " + stnName;
                    ctx.fillStyle = "rgba(0, 0, 0, 0.6)"; ctx.fillRect(20, 20, ctx.measureText(display).width + fS, fS + fS/2);
                    ctx.fillStyle = "white"; ctx.fillText(display, 20 + fS/2, 20 + fS/4);
                    const dN = `${{dateStr}}_${{aiTitle}}_${{addrStr}}_${{stnName}}.jpg`.replace(/[/\\\\?%*:|"<>]/g, '-');
                    const l = document.createElement('a'); l.download=dN; l.href=canvas.toDataURL('image/jpeg',1.0); l.click();
                    status.style.color = "green"; status.innerText = "✅ 保存完了: " + dN;
                }};
                i.src = imgBase64;
            }}, (err)=>{{}}, {{enableHighAccuracy:true, timeout:7000}});
        }})();
        </script>
        """
        st.components.v1.html(auto_save_script_rc, height=120)
