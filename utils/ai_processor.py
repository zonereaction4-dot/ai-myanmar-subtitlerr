import os
from google import genai
from google.genai import types

def generate_myanmar_subtitles(video_path: str) -> str:
    # API Key အား Environment Variable ထံမှ ဖတ်ယူခြင်း
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY ကို စနစ်ထဲမှာ ရှာမတွေ့ပါ။ ကျေးဇူးပြု၍ တပ်ဆင်ပေးပါ။")
        
    # Gemini Client အား Connect လုပ်ခြင်း
    client = genai.Client(api_key=api_key)
    
    print("\n[အဆင့် ၁]: ဗီဒီယိုဖိုင်ကို Gemini AI Server ပေါ်သို့ တင်နေပါသည်...")
    video_file = client.files.upload(file=video_path)
    print(f"[အဆင့် ၂]: Gemini က ဗီဒီယိုကို စစ်ဆေးနေပါသည် (ခဏစောင့်ပေးပါ)...")
    
    # AI ထံ တောင်းဆိုမည့် Prompt ညွှန်ကြားချက်
    prompt = (
        "You are an expert subtitle generator. Listen to the audio of this video very carefully. "
        "Translate and transcribe the spoken language directly into beautifully structured Myanmar (Burmese) language. "
        "Output ONLY the raw SRT format text. Ensure correct timestamps like [00:00:02,000 --> 00:00:05,500]. "
        "Do not include any extra explanations, markdown blocks, or introductory text. Just give me the pure SRT content."
    )
    
    print("[အဆင့် ၃]: Gemini မှ မြန်မာစာတန်းထိုး စတင်ဖန်တီးနေပါပြီ...")
    
    try:
        # 💡 Server အလွန်တောင့်တင်းပြီး Error တက်ခဲသော gemini-1.5-pro အား အသုံးပြုထားပါသည်
        response = client.models.generate_content(
            model='gemini-1.5-pro',
            contents=[video_file, prompt]
        )
        
        print("[အဆင့် ၄]: လုံခြုံရေးအရ Gemini Server ပေါ်မှ ဗီဒီယိုကို ပြန်လည်ရှင်းလင်းနေပါသည်...")
        client.files.delete(name=video_file.name)
        
        print("✨ အားလုံးအောင်မြင်ပါပြီ။ မြန်မာစာတန်းထိုး ရလဒ်ထွက်ပေါ်လာပါပြီ။")
        return response.text
        
    except Exception as e:
        # အကယ်၍ အကြောင်းအမျိုးမျိုးကြောင့် ထပ်ဖြစ်ပါက Server အမှားကို သိနိုင်ရန်
        try:
            client.files.delete(name=video_file.name)
        except:
            pass
        raise e