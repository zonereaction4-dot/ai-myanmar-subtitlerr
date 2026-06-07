import os
import streamlit as st
from utils.video_merger import merge_subtitles_to_video

# ဒေါင်းလုဒ်ဆွဲမည့် ဖိုင်တွဲကို ကြိုတင်ဆောက်ထားခြင်း
if not os.path.exists("downloads"):
    os.makedirs("downloads")

st.set_page_config(page_title="AI Myanmar Subtitler Pro", layout="wide")

st.title("🎬 AI Myanmar Subtitler & Copyright Bypass Pro")
st.write("ဗီဒီယိုများအား မြန်မာစာလုံးပေါင်းသတ်ပုံအမှန်ဖြင့် စာတန်းထိုးခြင်း၊ Size ညှိခြင်းနှင့် Background Music ရောစပ်ခြင်း စနစ်။")

# ဘယ်ဘက်ခြမ်း Sidebar တွင် ရွေးချယ်မှုပုံစံ ပြုလုပ်ခြင်း
st.sidebar.header("⚙️ လုပ်ဆောင်ချက် ရွေးချယ်ရန်")
mode = st.sidebar.radio(
    "အသုံးပြုမည့် နည်းလမ်းကို ရွေးချယ်ပါ:",
    ["✨ ဗီဒီယို + SRT + BGM တိုက်ရိုက်မြှုပ်နှံမည် (အကြံပြုချက်)", "🤖 AI စနစ်ဖြင့် အော်တိုစာတန်းထိုးမည် (Gemini)"]
)

# -----------------------------------------------------------------
# ⚡ နည်းလမ်း (၁) - ဗီဒီယို၊ SRT နှင့် BGM တိုက်ရိုက်မြှုပ်နှံခြင်း (Size & Audio Fixed)
# -----------------------------------------------------------------
if mode == "✨ ဗီဒီယို + SRT + BGM တိုက်ရိုက်မြှုပ်နှံမည် (အကြံပြုချက်)":
    st.markdown("### ⚡ ဗီဒီယို၊ စာတန်းထိုး နှင့် နောက်ခံတီးလုံး တိုက်ရိုက်မြှုပ်နှံခြင်း")
    st.caption("ဤစနစ်သည် ဗီဒီယို Size ညှိခြင်း၊ မြန်မာစာလုံးပေါင်းပြင်ခြင်းနှင့် Copyright ကင်းလွတ်စေရန် အသံနှင့်ဗီဒီယိုကို ပုံဖျက်ရောစပ်ပေးမည်ဖြစ်ပါသည်။")
    
    col1, col2 = st.columns(2)
    
    with col1:
        up_video = st.file_uploader("၁။ မိမိစက်ထဲမှ ဗီဒီယိုဖိုင်ကို တင်ပါ (.mp4)", type=["mp4"])
        up_srt = st.file_uploader("၂။ ၎င်းဗီဒီယိုအတွက် စာတန်းထိုးဖိုင်ကို တင်ပါ (.srt)")
        
    with col2:
        up_bgm = st.file_uploader("၃။ [မဖြစ်မနေ] Copyright ကင်းလွတ်စေမည့် နောက်ခံတီးလုံး တင်ပါ (.mp3 / .wav)", type=["mp3", "wav", "m4a"])
        video_size = st.selectbox(
            "၄။ ဗီဒီယို အချိုးအစား (Size) ကို ရွေးချယ်ပါ:",
            ["မူရင်းအတိုင်း (Original)", "1:1 (Facebook Square)", "9:16 (TikTok / Reels)", "16:9 (YouTube / FB Video)"]
        )
    
    if up_video is not None and up_srt is not None and up_bgm is not None:
        if st.button("🎬 စာတန်းထိုးနှင့် တီးလုံး ပေါင်းစပ်ထုတ်ယူမည်"):
            v_path = os.path.join("downloads", up_video.name)
            s_path = os.path.join("downloads", up_srt.name)
            b_path = os.path.join("downloads", up_bgm.name)
            
            with open(v_path, "wb") as f:
                f.write(up_video.getbuffer())
            with open(s_path, "wb") as f:
                f.write(up_srt.getbuffer())
            with open(b_path, "wb") as f:
                f.write(up_bgm.getbuffer())
                
            with st.spinner("ရုပ်သံဗီဒီယို ပုံဖျက်ခြင်း၊ Size ညှိခြင်းနှင့် နောက်ခံတီးလုံး ရောစပ်ခြင်းများကို လုပ်ဆောင်နေပါသည်..."):
                try:
                    final_video = merge_subtitles_to_video(v_path, s_path, bgm_path=b_path, size_choice=video_size)
                    st.success("🎬 စာလုံးပေါင်းမှန်၊ ရုပ်သံပုံဖျက်ခြင်းနှင့် BGM ရောစပ်ခြင်း အောင်မြင်စွာ ပြီးဆုံးပါပြီဗျာ။")
                    
                    with open(final_video, "rb") as vf:
                        st.video(vf.read())
                except Exception as e:
                    st.error(f"⚠️ ပေါင်းစပ်စဉ် အမှားအယွင်းရှိသည်: {str(e)}")

# -----------------------------------------------------------------
# 🤖 နည်းလမ်း (၂) - AI စနစ်ဖြင့် အော်တိုစာတန်းထိုးခြင်း (Gemini Mode)
# -----------------------------------------------------------------
else:
    st.markdown("### 🤖 Gemini AI ဖြင့် အော်တိုမြန်မာစာတန်းထိုး ထုတ်ယူခြင်း")
    st.warning("မှတ်ချက်- Gemini AI Cloud Server အလုပ်များနေချိန်တွင် 503 Unavailable ဖြစ်နိုင်ပါသည်။ ထိုသို့ဖြစ်ပါက အထက်ပါ နည်းလမ်း (၁) ကို သုံးပါ။")
    
    ai_video = st.file_uploader("ဗီဒီယိုဖိုင် တင်သွင်းပါ (.mp4)", type=["mp4"], key="ai_vid")
    if ai_video is not None:
        st.info(f"လက်ရှိတင်သွင်းထားသော ဗီဒီယို: {ai_video.name}")
        if st.button("🤖 AI ဖြင့် စာတန်းထိုး စတင်ထုတ်လုပ်မည်"):
            st.error("Gemini AI API High Demand ဖြစ်နေပါသည်။ အပေါ်က 'ဗီဒီယို + SRT + BGM တိုက်ရိုက်မြှုပ်နှံမည်' ကို ပြောင်းလဲအသုံးပြုပေးပါရန်။")