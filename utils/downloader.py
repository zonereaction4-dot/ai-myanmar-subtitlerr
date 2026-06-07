import os
import yt_dlp

def download_video(video_url: str, output_dir: str = "downloads") -> str:
    """
    ပေးထားသော URL (YouTube, TikTok, Rednote) မှ ဗီဒီယိုကို 
    အကောင်းဆုံး အရည်အသွေးဖြင့် ဒေါင်းလုဒ်ဆွဲပြီး လမ်းကြောင်း (File Path) ကို ပြန်ပေးသည်။
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(epoch)d_%(title)s.%(ext)s'),
        'ignoreerrors': False,
        'noplaylist': True,
    }

    try:
        print(f"Starting download from: {video_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            
            if not os.path.exists(file_path):
                base_path, _ = os.path.splitext(file_path)
                for file in os.listdir(output_dir):
                    if file.startswith(os.path.basename(base_path)):
                        file_path = os.path.join(output_dir, file)
                        break

            print(f"Download completed successfully! File saved at: {file_path}")
            return file_path

    except Exception as e:
        print(f"An error occurred during download: {str(e)}")
        raise e

# --- စမ်းသပ်ရန်အပိုင်း ---
if __name__ == "__main__":
    # စမ်းသပ်လိုသည့် YouTube သို့မဟုတ် TikTok Link ကို ဒီနေရာတွင် ထည့်ပါ
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
    try:
        saved_path = download_video(test_url)
        print(f"Test Success: {saved_path}")
    except Exception as e:
        print("Test Failed.")