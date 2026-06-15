import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, VideoClip

# Resolution of the video
VIDEO_SIZE = (1280, 720)
FONT_REGULAR = "C:/Windows/Fonts/georgia.ttf"
FONT_BOLD = "C:/Windows/Fonts/georgiab.ttf"

def draw_text_overlay(text, size=30, is_bold=False, y_offset=0.8, color=(255, 255, 255), width=1280, height=720):
    """Generates a transparent PIL Image with centered, shadowed text."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_path = FONT_BOLD if is_bold else FONT_REGULAR
    font = ImageFont.truetype(font_path, size)
    
    # Calculate text width and height
    text_box = draw.textbbox((0, 0), text, font=font)
    text_w = text_box[2] - text_box[0]
    text_h = text_box[3] - text_box[1]
    
    x = (width - text_w) // 2
    y = int(height * y_offset) - (text_h // 2)
    
    # Draw dark shadow
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 200))
    # Draw main text
    draw.text((x, y), text, font=font, fill=color)
    return img

def get_zoomed_frame(base_img, scale, center_x, center_y, target_size=VIDEO_SIZE):
    """Crops and zooms the image around a center point, preserving aspect ratio."""
    w, h = base_img.size
    tw, th = target_size
    
    # Dimensions of the crop box
    crop_w = int(w / scale)
    crop_h = int(h / scale)
    
    # Force target aspect ratio
    aspect = tw / th
    if crop_w / crop_h > aspect:
        crop_w = int(crop_h * aspect)
    else:
        crop_h = int(crop_w / aspect)
        
    x1 = max(0, min(w - crop_w, int(center_x - crop_w / 2)))
    y1 = max(0, min(h - crop_h, int(center_y - crop_h / 2)))
    x2 = x1 + crop_w
    y2 = y1 + crop_h
    
    cropped = base_img.crop((x1, y1, x2, y2))
    return cropped.resize(target_size, Image.Resampling.LANCZOS)

def create_feathered_mask(width, height, border=15):
    """Creates a transparent mask feathered at the edges."""
    mask = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(mask)
    for x in range(border):
        alpha = int((x / float(border)) * 255)
        draw.line([(x, 0), (x, height)], fill=alpha)
        draw.line([(width - 1 - x, 0), (width - 1 - x, height)], fill=alpha)
    for y in range(border):
        alpha = int((y / float(border)) * 255)
        draw.line([(0, y), (width, y)], fill=alpha)
        draw.line([(0, height - 1 - y), (width, height - 1 - y)], fill=alpha)
    return mask.filter(ImageFilter.GaussianBlur(3))

# ==============================================================================
# SCENE GENERATORS (USING CUSTOM MAKE_FRAME FOR HIGH-PERFORMANCE RENDERING)
# ==============================================================================

def make_scene1_clip(duration=8.0):
    # Scene 1: Sunset City Parallax
    bg = Image.open(r"d:\PORTFOLIO SIX\assets\secret_forbidden_place_bg.jpg").convert("RGBA")
    char = Image.open(r"d:\PORTFOLIO SIX\assets\character_temp.png").convert("RGBA")
    
    # Feather the character cutout so it blends seamlessly
    char_mask = create_feathered_mask(char.width, char.height, border=15)
    
    # Subtitle image
    sub_img = draw_text_overlay("Có những câu chuyện chưa từng được ghi lại...", size=32, y_offset=0.8)

    def make_frame(t):
        # Background zoom out (from 1.05 to 1.0)
        bg_scale = 1.05 - 0.05 * (t / duration)
        bg_frame = get_zoomed_frame(bg, bg_scale, 512, 288)
        
        # Character zoom out slightly faster to create 3D parallax depth
        char_scale = 1.08 - 0.08 * (t / duration)
        
        # Base position of character in original image coordinates
        # X: 330 to 550 (mid 440), Y: 300 to 560 (mid 430)
        # We will crop and scale the character separately
        char_w, char_h = char.size
        new_char_w = int(char_w * char_scale * (bg_frame.width / 1024.0))
        new_char_h = int(char_h * char_scale * (bg_frame.height / 576.0))
        
        resized_char = char.resize((new_char_w, new_char_h), Image.Resampling.LANCZOS)
        resized_mask = char_mask.resize((new_char_w, new_char_h), Image.Resampling.LANCZOS)
        
        # Calculate screen position based on zoom
        # Since background is scaling down, we slide character position slightly
        px = int(390 * (1280.0 / 1024.0) - (new_char_w - char_w) * 0.5)
        py = int(340 * (720.0 / 576.0) - (new_char_h - char_h) * 0.5)
        
        # Paste character onto the zoomed background frame
        bg_frame.paste(resized_char, (px, py), resized_mask)
        
        # Paste subtitle (with fade in / fade out)
        alpha = 255
        if t < 1.5:
            alpha = int((t / 1.5) * 255)
        elif t > duration - 1.5:
            alpha = int(((duration - t) / 1.5) * 255)
            
        if alpha < 255:
            temp_sub = sub_img.copy()
            # Apply alpha opacity
            temp_sub.putalpha(temp_sub.split()[3].point(lambda p: int(p * alpha / 255.0)))
            bg_frame.paste(temp_sub, (0, 0), temp_sub)
        else:
            bg_frame.paste(sub_img, (0, 0), sub_img)
            
        return np.array(bg_frame.convert("RGB"))
        
    return VideoClip(make_frame, duration=duration)

def make_scene2_clip(duration=8.0):
    # Scene 2: Empty Temple Gates
    bg = Image.open(r"d:\PORTFOLIO SIX\assets\secret_forbidden_place_bg.jpg").convert("RGBA")
    sub_img = draw_text_overlay("...Có những con người từng tồn tại, nhưng đã bị xóa sạch khỏi lịch sử.", size=32, y_offset=0.8)

    def make_frame(t):
        # Zoom in slowly (from 1.0 to 1.05)
        scale = 1.0 + 0.05 * (t / duration)
        frame = get_zoomed_frame(bg, scale, 512, 288)
        
        # Subtitle opacity fade
        alpha = 255
        if t < 1.5:
            alpha = int((t / 1.5) * 255)
        elif t > duration - 1.5:
            alpha = int(((duration - t) / 1.5) * 255)
            
        if alpha < 255:
            temp_sub = sub_img.copy()
            temp_sub.putalpha(temp_sub.split()[3].point(lambda p: int(p * alpha / 255.0)))
            frame.paste(temp_sub, (0, 0), temp_sub)
        else:
            frame.paste(sub_img, (0, 0), sub_img)
            
        return np.array(frame.convert("RGB"))
        
    return VideoClip(make_frame, duration=duration)

def make_scene3_clip(duration=9.0):
    # Scene 3: Forgotten Imperial Archive Sheet
    bg = Image.open(r"d:\PORTFOLIO SIX\assets\forgotten_archive_sheet.png").convert("RGBA")
    sub_img = draw_text_overlay("Ẩn sâu dưới lòng Tử Cấm Thành... là nơi lưu giữ những gì thế giới cố gắng lãng quên.", size=32, y_offset=0.8)

    def make_frame(t):
        # Slow panning down and zoom out
        scale = 1.1 - 0.05 * (t / duration)
        cy = int(bg.height * 0.45 + (t / duration) * (bg.height * 0.1))
        frame = get_zoomed_frame(bg, scale, bg.width // 2, cy)
        
        # Subtitle opacity fade
        alpha = 255
        if t < 1.5:
            alpha = int((t / 1.5) * 255)
        elif t > duration - 1.5:
            alpha = int(((duration - t) / 1.5) * 255)
            
        if alpha < 255:
            temp_sub = sub_img.copy()
            temp_sub.putalpha(temp_sub.split()[3].point(lambda p: int(p * alpha / 255.0)))
            frame.paste(temp_sub, (0, 0), temp_sub)
        else:
            frame.paste(sub_img, (0, 0), sub_img)
            
        return np.array(frame.convert("RGB"))
        
    return VideoClip(make_frame, duration=duration)

def make_scene4_clip(duration=8.0):
    # Scene 4: Lục An finding the Lantern
    bg = Image.open(r"d:\PORTFOLIO SIX\assets\luc_an_character_sheet.png").convert("RGBA")
    sub_img = draw_text_overlay("Nơi đây, thứ đầu tiên mất đi không phải sinh mạng...", size=32, y_offset=0.8)

    def make_frame(t):
        # Slow zoom on Lục An's face
        scale = 1.0 + 0.08 * (t / duration)
        frame = get_zoomed_frame(bg, scale, bg.width * 0.4, bg.height * 0.45)
        
        # Subtitle opacity fade
        alpha = 255
        if t < 1.5:
            alpha = int((t / 1.5) * 255)
        elif t > duration - 1.5:
            alpha = int(((duration - t) / 1.5) * 255)
            
        if alpha < 255:
            temp_sub = sub_img.copy()
            temp_sub.putalpha(temp_sub.split()[3].point(lambda p: int(p * alpha / 255.0)))
            frame.paste(temp_sub, (0, 0), temp_sub)
        else:
            frame.paste(sub_img, (0, 0), sub_img)
            
        return np.array(frame.convert("RGB"))
        
    return VideoClip(make_frame, duration=duration)

def make_scene5_clip(duration=8.0):
    # Scene 5: Lantern lights up with glowing blue flame
    bg = Image.open(r"d:\PORTFOLIO SIX\assets\luc_an_character_sheet.png").convert("RGBA")
    sub_img = draw_text_overlay("...Mà là ký ức.", size=32, y_offset=0.8)

    def make_frame(t):
        # Slow zoom in
        scale = 1.08 + 0.04 * (t / duration)
        frame = get_zoomed_frame(bg, scale, bg.width * 0.4, bg.height * 0.45)
        
        # Draw dynamic blue flame glow (pulsating with sine wave)
        glow_size = int(60 + 15 * np.sin(t * 5))
        glow_layer = Image.new("RGBA", VIDEO_SIZE, (0, 0, 0, 0))
        draw_glow = ImageDraw.Draw(glow_layer)
        
        # Lantern coordinates on resized/zoomed frame
        # Let's target the center of the lantern
        lx, ly = 580, 420
        
        # Draw radial glow circles
        for r in range(glow_size, 0, -5):
            alpha = int((1.0 - (r / float(glow_size))) * 50)
            draw_glow.ellipse([lx - r, ly - r, lx + r, ly + r], fill=(0, 220, 255, alpha))
            
        frame.paste(glow_layer, (0, 0), glow_layer)
        
        # Subtitle opacity fade
        alpha = 255
        if t < 1.5:
            alpha = int((t / 1.5) * 255)
        elif t > duration - 1.5:
            alpha = int(((duration - t) / 1.5) * 255)
            
        if alpha < 255:
            temp_sub = sub_img.copy()
            temp_sub.putalpha(temp_sub.split()[3].point(lambda p: int(p * alpha / 255.0)))
            frame.paste(temp_sub, (0, 0), temp_sub)
        else:
            frame.paste(sub_img, (0, 0), sub_img)
            
        return np.array(frame.convert("RGB"))
        
    return VideoClip(make_frame, duration=duration)

def make_scene6_clip(duration=8.0):
    # Scene 6: Wuming Empress (Vô Danh Hoàng Hậu)
    bg = Image.open(r"d:\PORTFOLIO SIX\assets\wuming_character_sheet.png").convert("RGBA")
    sub_img = draw_text_overlay("Ký ức thức tỉnh, đưa sự thật đến gần...", size=32, y_offset=0.8)

    def make_frame(t):
        # Slow pan up
        scale = 1.05
        cy = int(bg.height * 0.5 - (t / duration) * (bg.height * 0.08))
        frame = get_zoomed_frame(bg, scale, bg.width // 2, cy)
        
        # Subtitle opacity fade
        alpha = 255
        if t < 1.5:
            alpha = int((t / 1.5) * 255)
        elif t > duration - 1.5:
            alpha = int(((duration - t) / 1.5) * 255)
            
        if alpha < 255:
            temp_sub = sub_img.copy()
            temp_sub.putalpha(temp_sub.split()[3].point(lambda p: int(p * alpha / 255.0)))
            frame.paste(temp_sub, (0, 0), temp_sub)
        else:
            frame.paste(sub_img, (0, 0), sub_img)
            
        return np.array(frame.convert("RGB"))
        
    return VideoClip(make_frame, duration=duration)

def make_scene7_clip(duration=8.0):
    # Scene 7: Ngọc Mai and the Diary
    bg = Image.open(r"d:\PORTFOLIO SIX\assets\ngoc_mai_character_sheet.png").convert("RGBA")
    sub_img = draw_text_overlay("Một cô gái mang theo cuốn nhật ký mà ngay cả cái chết cũng không thể cướp đi...", size=32, y_offset=0.8)

    def make_frame(t):
        # Slow zoom in
        scale = 1.0 + 0.06 * (t / duration)
        frame = get_zoomed_frame(bg, scale, bg.width * 0.45, bg.height * 0.45)
        
        # Subtitle opacity fade
        alpha = 255
        if t < 1.5:
            alpha = int((t / 1.5) * 255)
        elif t > duration - 1.5:
            alpha = int(((duration - t) / 1.5) * 255)
            
        if alpha < 255:
            temp_sub = sub_img.copy()
            temp_sub.putalpha(temp_sub.split()[3].point(lambda p: int(p * alpha / 255.0)))
            frame.paste(temp_sub, (0, 0), temp_sub)
        else:
            frame.paste(sub_img, (0, 0), sub_img)
            
        return np.array(frame.convert("RGB"))
        
    return VideoClip(make_frame, duration=duration)

def make_scene8_clip(duration=8.0):
    # Scene 8: The Gatekeeper Shiyan
    bg = Image.open(r"d:\PORTFOLIO SIX\assets\shiyan_character_sheet.jpg").convert("RGBA")
    sub_img = draw_text_overlay("...Và kẻ canh giữ bí mật suốt một trăm năm.", size=32, y_offset=0.8)

    def make_frame(t):
        # Dramatic zoom in
        scale = 1.02 + 0.12 * (t / duration)
        frame = get_zoomed_frame(bg, scale, bg.width * 0.5, bg.height * 0.45)
        
        # Subtitle opacity fade
        alpha = 255
        if t < 1.5:
            alpha = int((t / 1.5) * 255)
        elif t > duration - 1.5:
            alpha = int(((duration - t) / 1.5) * 255)
            
        if alpha < 255:
            temp_sub = sub_img.copy()
            temp_sub.putalpha(temp_sub.split()[3].point(lambda p: int(p * alpha / 255.0)))
            frame.paste(temp_sub, (0, 0), temp_sub)
        else:
            frame.paste(sub_img, (0, 0), sub_img)
            
        return np.array(frame.convert("RGB"))
        
    return VideoClip(make_frame, duration=duration)

def make_scene9_clip(duration=9.0):
    # Scene 9: Climax slideshow (Red Veils -> Outer Court -> Memory Garden)
    img1 = Image.open(r"d:\PORTFOLIO SIX\assets\red_veils_sheet.png").convert("RGBA")
    img2 = Image.open(r"d:\PORTFOLIO SIX\assets\outer_court_sheet.png").convert("RGBA")
    img3 = Image.open(r"d:\PORTFOLIO SIX\assets\memory_garden_illustration.jpg").convert("RGBA")
    
    sub_img = draw_text_overlay("Phía sau cánh cửa cuối cùng... là sự thật, hay chỉ là hư vô?", size=32, y_offset=0.8)

    def make_frame(t):
        # Slideshow logic: 3 seconds per image
        if t < 3.0:
            scale = 1.0 + 0.04 * (t / 3.0)
            frame = get_zoomed_frame(img1, scale, img1.width // 2, img1.height // 2)
            # Crossfade to next image at the end
            if t > 2.5:
                alpha = int(((t - 2.5) / 0.5) * 255)
                frame_next = get_zoomed_frame(img2, 1.0, img2.width // 2, img2.height // 2)
                frame = Image.blend(frame, frame_next, alpha / 255.0)
        elif t < 6.0:
            t_rel = t - 3.0
            scale = 1.0 + 0.04 * (t_rel / 3.0)
            frame = get_zoomed_frame(img2, scale, img2.width // 2, img2.height // 2)
            if t_rel > 2.5:
                alpha = int(((t_rel - 2.5) / 0.5) * 255)
                frame_next = get_zoomed_frame(img3, 1.0, img3.width // 2, img3.height // 2)
                frame = Image.blend(frame, frame_next, alpha / 255.0)
        else:
            t_rel = t - 6.0
            scale = 1.0 + 0.04 * (t_rel / 3.0)
            frame = get_zoomed_frame(img3, scale, img3.width // 2, img3.height // 2)
            
        # Subtitle opacity fade
        alpha = 255
        if t < 1.5:
            alpha = int((t / 1.5) * 255)
        elif t > duration - 1.5:
            alpha = int(((duration - t) / 1.5) * 255)
            
        if alpha < 255:
            temp_sub = sub_img.copy()
            temp_sub.putalpha(temp_sub.split()[3].point(lambda p: int(p * alpha / 255.0)))
            frame.paste(temp_sub, (0, 0), temp_sub)
        else:
            frame.paste(sub_img, (0, 0), sub_img)
            
        return np.array(frame.convert("RGB"))
        
    return VideoClip(make_frame, duration=duration)

def make_scene10_clip(duration=6.0):
    # Scene 10: Calligraphic Logo Title Card
    black_bg = Image.new("RGBA", VIDEO_SIZE, (2, 5, 18, 255))
    
    # Title text
    title_img = draw_text_overlay("TỬ CẤM THÀNH: HỒI ỨC CẤM KỴ", size=48, is_bold=True, y_offset=0.45, color=(255, 183, 3))
    # Subtitle
    sub_img = draw_text_overlay("Secret of the Forbidden Place", size=28, is_bold=False, y_offset=0.55, color=(207, 199, 213))

    def make_frame(t):
        frame = black_bg.copy()
        
        # Title Fade In
        alpha_t = 255
        if t < 2.0:
            alpha_t = int((t / 2.0) * 255)
            
        # Subtitle Delay Fade In
        alpha_s = 0
        if t > 1.5:
            t_rel = t - 1.5
            alpha_s = min(255, int((t_rel / 1.5) * 255))
            
        # Apply fade out at the end of video (last 1.5 seconds)
        if t > duration - 1.5:
            fade_out = int(((duration - t) / 1.5) * 255)
            alpha_t = int(alpha_t * fade_out / 255.0)
            alpha_s = int(alpha_s * fade_out / 255.0)
            
        # Paste Title
        if alpha_t > 0:
            temp_t = title_img.copy()
            temp_t.putalpha(temp_t.split()[3].point(lambda p: int(p * alpha_t / 255.0)))
            frame.paste(temp_t, (0, 0), temp_t)
            
        # Paste Subtitle
        if alpha_s > 0:
            temp_s = sub_img.copy()
            temp_s.putalpha(temp_s.split()[3].point(lambda p: int(p * alpha_s / 255.0)))
            frame.paste(temp_s, (0, 0), temp_s)
            
        return np.array(frame.convert("RGB"))
        
    return VideoClip(make_frame, duration=duration)

# ==============================================================================
# MAIN ASSEMBLY PIPELINE
# ==============================================================================

def build_trailer():
    print("Initializing Trailer Assembly Pipeline...")
    
    # 1. Generate all video clips
    print("Generating Scene 1...")
    clip1 = make_scene1_clip()
    print("Generating Scene 2...")
    clip2 = make_scene2_clip()
    print("Generating Scene 3...")
    clip3 = make_scene3_clip()
    print("Generating Scene 4...")
    clip4 = make_scene4_clip()
    print("Generating Scene 5...")
    clip5 = make_scene5_clip()
    print("Generating Scene 6...")
    clip6 = make_scene6_clip()
    print("Generating Scene 7...")
    clip7 = make_scene7_clip()
    print("Generating Scene 8...")
    clip8 = make_scene8_clip()
    print("Generating Scene 9...")
    clip9 = make_scene9_clip()
    print("Generating Scene 10...")
    clip10 = make_scene10_clip()
    
    # 2. Combine all clips sequentially
    print("Concatenating all clips sequentially...")
    from moviepy import concatenate_videoclips
    final_video = concatenate_videoclips([
        clip1, clip2, clip3, clip4, clip5, clip6, clip7, clip8, clip9, clip10
    ])
    
    total_duration = final_video.duration
    print(f"Total video duration: {total_duration} seconds.")
    
    # 3. Add background music
    music_path = r"d:\PORTFOLIO SIX\assets\nhacbackground.mp3"
    if os.path.exists(music_path):
        print(f"Loading background music: {music_path}")
        audio = AudioFileClip(music_path)
        # Cut audio to match video duration
        audio_cut = audio.subclipped(0, total_duration) if hasattr(audio, 'subclipped') else audio.subclip(0, total_duration)
        
        # Apply fade out to audio in last 2 seconds using MoviePy 2.x API
        from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
        audio_cut = AudioFadeOut(duration=2.0).apply(audio_cut)
            
        final_video = final_video.with_audio(audio_cut) if hasattr(final_video, 'with_audio') else final_video.set_audio(audio_cut)
    else:
        print("Warning: nhacbackground.mp3 not found. Video will have no sound.")
        
    # 4. Render and write video to file
    output_path = r"d:\PORTFOLIO SIX\assets\trailer_tucamthanh.mp4"
    print(f"Rendering and saving final video to: {output_path} ...")
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4
    )
    print("Trailer Assembly Succeeded!")

if __name__ == "__main__":
    build_trailer()
