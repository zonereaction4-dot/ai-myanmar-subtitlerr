import os
import cv2
import numpy as np
import subprocess
from PIL import Image, ImageDraw, ImageFont

def parse_srt(srt_path):
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read().replace('\r\n', '\n')
    blocks = content.strip().split('\n\n')
    subtitles = []
    
    def time_to_sec(time_str):
        time_str = time_str.strip()
        h, m, s = time_str.split(':')
        s, ms = s.split(',')
        return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0

    for block in blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) >= 3:
            time_line = lines[1]
            text_line = " ".join(lines[2:])
            if " --> " in time_line:
                try:
                    start_t, end_t = time_line.split(" --> ")
                    subtitles.append({
                        'start': time_to_sec(start_t),
                        'end': time_to_sec(end_t),
                        'text': text_line
                    })
                except Exception:
                    continue
    return subtitles

def merge_subtitles_to_video(video_path: str, srt_path: str, bgm_path: str = None, size_choice: str = "မူရင်းအတိုင်း (Original)") -> str:
    temp_output = os.path.splitext(video_path)[0] + "_temp.mp4"
    output_path = os.path.splitext(video_path)[0] + "_cloud_final.mp4"
    
    subs = parse_srt(srt_path)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0
        
    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Target Resolution & Crop Logic
    target_w, target_h = orig_w, orig_h
    crop_x, crop_y, crop_w, crop_h = 0, 0, orig_w, orig_h
    
    if size_choice == "1:1 (Facebook Square)":
        target_w, target_h = 720, 720
        side = min(orig_w, orig_h)
        crop_w, crop_h = side, side
        crop_x = (orig_w - side) // 2
        crop_y = (orig_h - side) // 2
    elif size_choice == "9:16 (TikTok / Reels)":
        target_w, target_h = 720, 1280
        if orig_w / orig_h > 9 / 16:
            crop_h = orig_h
            crop_w = int(orig_h * (9 / 16))
            crop_x = (orig_w - crop_w) // 2
            crop_y = 0
        else:
            crop_w = orig_w
            crop_h = int(orig_w * (16 / 9))
            crop_x = 0
            crop_y = (orig_h - crop_h) // 2
    elif size_choice == "16:9 (YouTube / FB Video)":
        target_w, target_h = 1280, 720
        if orig_w / orig_h > 16 / 9:
            crop_h = orig_h
            crop_w = int(orig_h * (16 / 9))
            crop_x = (orig_w - crop_w) // 2
            crop_y = 0
        else:
            crop_w = orig_w
            crop_h = int(orig_w * (9 / 16))
            crop_x = 0
            crop_y = (orig_h - crop_h) // 2

    # Cloud Linux အတွက် လိုက်ဖက်သော mp4v codec ကိုသုံးခြင်း
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_output, fourcc, fps, (target_w, target_h))
    
    # ✨ Folder ထဲသို့ ထည့်ထားသော မြန်မာဖောင့်အား တိုက်ရိုက်ဖတ်ခြင်း
    font_path = "myanmar.ttf"
    if not os.path.exists(font_path):
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" # Cloud Failback
        
    try:
        font = ImageFont.truetype(font_path, int(target_h * 0.045))
        title_font = ImageFont.truetype(font_path, int(target_h * 0.035))
    except Exception:
        font = ImageFont.load_default()
        title_font = font

    frame_idx = 0
    subs.sort(key=lambda k: k['start'])

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        current_time = frame_idx / fps
        
        frame_cropped = frame[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
        frame_resized = cv2.resize(frame_cropped, (target_w, target_h))
        frame_resized = cv2.convertScaleAbs(frame_resized, alpha=1.03, beta=1)
        
        img_pil = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        active_text = None
        for sub in subs:
            if sub['start'] <= current_time <= sub['end']:
                active_text = sub['text']
                break
            elif sub['start'] > current_time:
                break
                
        if active_text:
            bbox = draw.textbbox((0, 0), active_text, font=font)
            text_w = bbox[2] - bbox[0]
            x = (target_w - text_w) // 2
            y = int(target_h * 0.82)
            
            draw.text((x-2, y-2), active_text, font=font, fill="black")
            draw.text((x+2, y-2), active_text, font=font, fill="black")
            draw.text((x-2, y+2), active_text, font=font, fill="black")
            draw.text((x+2, y+2), active_text, font=font, fill="black")
            draw.text((x, y), active_text, font=font, fill="white")
                
        title_text = "Oneminutestory"
        t_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        t_w = t_bbox[2] - t_bbox[0]
        draw.text((target_w - t_w - 20, 20), title_text, font=title_font, fill="yellow")

        frame_out = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        out.write(frame_out)
        frame_idx += 1

    cap.release()
    out.release()
    
    # Linux-based FFmpeg Command (Ultrafast Rendering)
    if bgm_path and os.path.exists(bgm_path):
        audio_filter = "[0:a]volume=0.85[a1];[1:a]volume=0.15[a2];[a1][a2]amix=inputs=2:duration=first:dropout_transition=2"
        audio_command = [
            'ffmpeg', '-y',
            '-i', video_path, '-i', bgm_path, '-i', temp_output,
            '-filter_complex', audio_filter,
            '-map', '2:v', '-c:v', 'libx264', '-preset', 'ultrafast', '-c:a', 'aac', '-shortest',
            output_path
        ]
    else:
        audio_command = [
            'ffmpeg', '-y', '-i', temp_output, '-i', video_path,
            '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'ultrafast', '-c:a', 'aac', output_path
        ]
    
    try:
        subprocess.run(audio_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if os.path.exists(temp_output):
            os.remove(temp_output)
        return output_path
    except Exception:
        if os.path.exists(temp_output):
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_output, output_path)
        return output_path