import streamlit as str_lit
import os
import time  # ⏳ ဗီဒီယိုဆာဗာပေါ်မှာ စောင့်ရန်နှင့် အချိန်ရေတွက်ရန်
import google.generativeai as genai
from google import genai as genai_v1
import re
import json
from utils.video_merger import merge_subtitles_to_video

# 🔑 [AI KEY CONFIG] Streamlit Cloud Secrets မှတစ်ဆင့် API Key ရယူခြင်း
api_key_str = None
if "GEMINI_API_KEY" in str_lit.secrets:
    api_key_str = str_lit.secrets["GEMINI_API_KEY"]
elif "google_api_key" in str_lit.secrets:
    api_key_str = str_lit.secrets["google_api_key"]
else:
    if os.path.exists("key.txt"):
        with open("key.txt", "r") as f:
            api_key_str = f.read().strip()

if api_key_str:
    genai.configure(api_key=api_key_str)

str_lit.set_page_config(page_title="AI Myanmar Subtitler Pro", layout="wide")

# Premium UI Styling
str_lit.markdown("""
    <style>
    .main-title { font-size: 36px !important; font-weight: bold; color: #FFFFFF; margin-bottom: 5px; }
    .sub-title { font-size: 18px !important; color: #B0B0B0; margin-bottom: 25px; }
    .stRadio > label { font-size: 18px !important; font-weight: bold !important; color: #FFFFFF !important; }
    .timer-box { background-color: #1E293B; border-left: 5px solid #3B82F6; padding: 15px; border-radius: 5px; margin: 15px 0; color: #38BDF8; font-weight: bold; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

str_lit.markdown('<p class="main-title">🎬 Copyright Bypass Pro</p>', unsafe_allow_html=True)
str_lit.markdown('<p class="sub-title">ဗီဒီယိုများအား မြန်မာစာလုံးပေါင်းသတ်ပုံအမှန်ဖြင့် စာတန်းထိုးခြင်းနှင့် Size ညှိခြင်းစနစ်။</p>', unsafe_allow_html=True)

# Sidebar Options
str_lit.sidebar.markdown("### ⚙️ လုပ်ဆောင်ချက် ရွေးချယ်ရန်")
mode = str_lit.sidebar.radio(
    "အသုံးပြုမည့် နည်းလမ်းကို ရွေးချယ်ပါ-",
    ["✨ ဗီဒီယို + SRT + BGM တိုက်ရိုက်မြှုပ်နှံမည် (အကြံပြုချက်)", "🤖 AI စနစ်ဖြင့် အော်တိုစာတန်းထိုးမည် (Gemini Mode)"]
)

def clean_json_string(raw_code):
    raw_code = re.sub(r'//.*?\n', '\n', raw_code)
    match = re.search(r'\[\s*\{.*\}\s*\]', raw_code, re.DOTALL)
    if match:
        return match.group(0)
    return raw_code.strip()

def generate_srt_from_ai(video_path):
    try:
        if not api_key_str:
            raise ValueError("Streamlit Secrets ထဲတွင် API Key မတွေ့ရှိရပါ။")
            
        client = genai_v1.Client(api_key=api_key_str)
        
        # ဗီဒီယိုအား AI Cloud ပေါ်သို့ တင်ခြင်း
        str_lit.info("⏳ ဗီဒီယိုအား AI ဆာဗာသို့ တင်သွင်းနေပါသည်...")
        video_file = client.files.upload(file=video_path)
        
        # ဗီဒီယိုဖိုင် ACTIVE ဖြစ်သည်အထိ ဆာဗာတွင် စောင့်ဆိုင်းပေးခြင်း
        str_lit.info("⚡ AI မှ ဗီဒီယိုဖိုင်အား စတင်ဆန်းစစ်နေပါသည်... ခေတ္တစောင့်ဆိုင်းပေးပါ...")
        while video_file.state.name == "PROCESSING":
            time.sleep(3)
            video_file = client.files.get(name=video_file.name)
            
        if video_file.state.name == "FAILED":
            raise ValueError("AI ဆာဗာမှ ဗီဒီယိုအား ဖတ်ရှုရန် Ngreငြင်းပယ်လိုက်ပါသည်။")
            
        prompt = """
        Analyze this video and generate subtitles in Myanmar language. 
        Return ONLY a raw JSON array of objects. Do not include markdown formatting, no ```json, no explanations.
        Each object MUST have 'start' (float seconds), 'end' (float seconds), and 'text' (Myanmar text transcription).
        Example format: [{"start": 0.5, "end": 3.2, "text": "မင်္ဂလာပါဗျာ"}]
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_file, prompt]
        )
        
        try:
            client.files.delete(name=video_file.name)
        except:
            pass
            
        cleaned_reply = clean_json_string(response.text)
        data = json.loads(cleaned_reply)
        
        srt_content = ""
        for idx, item in enumerate(data, 1):
            start_sec = item['start']
            end_sec = item['end']
            text = item['text']
            
            def format_time(seconds):
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                s = int(seconds % 60)
                ms = int((seconds - int(seconds)) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
                
            srt_content += f"{idx}\n{format_time(start_sec)} --> {format_time(end_sec)}\n{text}\n\n"
            
        ai_srt_path = "ai_generated.srt"
        with open(ai_srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content.strip() + "\n")
        return ai_srt_path
    except Exception as e:
        str_lit.error(f"AI ကနေ စာတန်းဖတ်ယူရာတွင် အမှားအယွင်းရှိနေပါသည်- {str(e)}")
        return None

# --- MODE 1: MANUAL SRT MERGE ---
if mode == "✨ ဗီဒီယို + SRT + BGM တိုက်ရိုက်မြှုပ်နှံမည် (အကြံပြုချက်)":
    col1, col2 = str_lit.columns(2)
    with col1:
        v_file = str_lit.file_uploader("၁။ မိမိစက်ထဲမှ ဗီဒီယိုဖိုင် တင်ပါ (.mp4)", type=["mp4", "mov"])
        srt_file = str_lit.file_uploader("၂။ ၎င်းဗီဒီယိုအတွက် စာတန်းထိုးဖိုင် တင်ပါ (.srt)", type=["srt"])
    with col2:
        bgm_file = str_lit.file_uploader("၃။ [မဖြစ်မနေမဟုတ်] နောက်ခံတေးဂီတ တင်ပါ (.mp3 / .wav)", type=["mp3", "wav"])
        size_opt = str_lit.selectbox("၄။ ဗီဒီယို အရွယ်အစား (Size) ကို ရွေးချယ်ပါ-", ["မူရင်းအတိုင်း (Original)", "1:1 (Facebook Square)", "9:16 (TikTok / Reels)", "16:9 (YouTube / FB Video)"])

    if str_lit.button("🎬 စာတန်းထိုးနှင့် ဗီဒီယို ပေါင်းစပ်ထုတ်ယူမည်"):
        if v_file and srt_file:
            # ⏱️ အချိန်စတင်ရေတွက်ခြင်း ကွက်လပ်နေရာ ဖန်တီးခြင်း
            start_time = time.time()
            timer_placeholder = str_lit.empty()
            
            with str_lit.spinner("🔮 ဗီဒီယိုအား စတိုင်သစ်များဖြင့် ပေါင်းစပ်ဖန်တီးနေပါသည်... ขေတ္တစောင့်ဆိုင်းပေးပါ..."):
                with open("temp_v.mp4", "wb") as f: f.write(v_file.read())
                with open("temp_s.srt", "wb") as f: f.write(srt_file.read())
                
                bgm_p = None
                if bgm_file:
                    bgm_p = "temp_b.mp3"
                    with open(bgm_p, "wb") as f: f.write(bgm_file.read())
                
                # အချိန်စက္ကန့်အလိုက် အော်တိုတိုးပြပေးမည့် Loop စနစ်
                output = None
                # သီးခြား Thread မလိုဘဲ စာသားမထွက်မချင်း Timer ကို ပုံမှန်ပြသရန် Background စနစ်ဖြင့် ချိတ်ဆက်ခြင်း
                # မှတ်ချက် - merge_subtitles_to_video အလုပ်လုပ်နေချိန် ပြသရန် timer နေရာကို static သတ်မှတ်ထားပါသည်
                elapsed_sec = 0
                
                # ဗီဒီယိုစတင်လုပ်ဆောင်ခြင်း
                output = merge_subtitles_to_video("temp_v.mp4", "temp_s.srt", bgm_p, size_opt)
                
                # ပြီးဆုံးသွားချိန် စုစုပေါင်းကြာချိန်ကို တွက်ချက်ခြင်း
                total_elapsed = time.time() - start_time
                mins = int(total_elapsed // 60)
                secs = int(total_elapsed % 60)
                timer_placeholder.markdown(f'<div class="timer-box">⏱️ ဗီဒီယိုထုတ်လုပ်မှု ပြီးဆုံးသွားပါပြီ။ စုစုပေါင်းကြာမြင့်ချိန်: {mins} မိနစ် {secs} စက္ကန့်</div>', unsafe_allow_html=True)
                
                if output and os.path.exists(output):
                    str_lit.success("🎉 ဗီဒီယို ပေါင်းစပ်ခြင်း အောင်မြင်ပါသည်!")
                    with open(output, "rb") as f:
                        str_lit.download_button("📥 ပြီးစီးသည့် ဗီဒီယိုအား ဒေါင်းလုဒ်ဆွဲရန်", f, file_name="final_video.mp4")
                    str_lit.video(output)
                    
                    for tmp in ["temp_v.mp4", "temp_s.srt", "temp_b.mp3", output]:
                        if tmp and os.path.exists(tmp): os.remove(tmp)
        else:
            str_lit.warning("⚠️ ကျေးဇူးပြု၍ ဗီဒီယိုနှင့် SRT ဖိုင်ကို အပြည့်အစုံ တင်ပေးပါဗျာ။")

# --- MODE 2: AI AUTOMATIC SUBTITLE ---
else:
    str_lit.markdown("### 🤖 Gemini AI ဖြင့် အော်တိုမြန်မာစာတန်းထိုးထုတ်ယူခြင်း")
    
    col1, col2 = str_lit.columns(2)
    with col1:
        v_file = str_lit.file_uploader("မိမိဗီဒီယို တင်သွင်းပါ (.mp4)", type=["mp4"])
    with col2:
        size_opt = str_lit.selectbox("ဗီဒီယို အရွယ်အစား (Size) ကို ရွေးချယ်ပါ-", ["မူရင်းအတိုင်း (Original)", "1:1 (Facebook Square)", "9:16 (TikTok / Reels)", "16:9 (YouTube / FB Video)"])

    if str_lit.button("🧠 AI စနစ်ဖြင့် အော်တိုစာတန်းထိုးပြီး ဗီဒီယိုထုတ်ယူမည်"):
        if v_file:
            start_time = time.time()
            timer_placeholder = str_lit.empty()
            
            with str_lit.spinner("⚡ AI မှ ဗီဒီယိုကို နားထောင်ပြီး မြန်မာစာတန်းထိုး စတင်ဖန်တီးနေပါသည်..."):
                with open("ai_temp_v.mp4", "wb") as f: f.write(v_file.read())
                
                generated_srt = generate_srt_from_ai("ai_temp_v.mp4")
                
                if generated_srt and os.path.exists(generated_srt):
                    str_lit.text_area("📝 AI မှ ထုတ်ပေးလိုက်သော SRT စာသားများ-", open(generated_srt, 'r', encoding='utf-8').read(), height=150)
                    
                    final_output = merge_subtitles_to_video("ai_temp_v.mp4", generated_srt, None, size_opt)
                    
                    total_elapsed = time.time() - start_time
                    mins = int(total_elapsed // 60)
                    secs = int(total_elapsed % 60)
                    timer_placeholder.markdown(f'<div class="timer-box">⏱️ AI အော်တိုလုပ်ဆောင်မှု ပြီးဆုံးပါပြီ။ စုစုပေါင်းကြာမြင့်ချိန်: {mins} မိနစ် {secs} စက္ကန့်</div>', unsafe_allow_html=True)
                    
                    if final_output and os.path.exists(final_output):
                        str_lit.success("🎉 AI စနစ်ဖြင့် ဗီဒီယိုအော်တိုစာတန်းထိုးခြင်း အောင်မြင်ပါသည်!")
                        with open(final_output, "rb") as f:
                            str_lit.download_button("📥 AI စာတန်းထိုးပြီးသား ဗီဒီယိုအား ဒေါင်းလုဒ်ဆွဲရန်", f, file_name="ai_final_video.mp4")
                        str_lit.video(final_output)
                        
                        for tmp in ["ai_temp_v.mp4", generated_srt, final_output]:
                            if os.path.exists(tmp): os.remove(tmp)
        else:
            str_lit.warning("⚠️ ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင် တင်ပေးပါဗျာ။")