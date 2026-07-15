import os
import sys
import numpy as np
import soundfile as sf
from pydub import AudioSegment
import torchaudio

def crossfade_numpy_arrays(wave1, wave2, sample_rate=24000, crossfade_sec=0.15):
    """Nối 2 đoạn audio numpy array với hiệu ứng crossfade để không bị tiếng click"""
    crossfade_samples = int(crossfade_sec * sample_rate)
    
    crossfade_samples = min(crossfade_samples, len(wave1), len(wave2))
    
    if crossfade_samples <= 0:
        return np.concatenate([wave1, wave2])
        
    prev_overlap = wave1[-crossfade_samples:]
    next_overlap = wave2[:crossfade_samples]
    
    fade_out = np.linspace(1, 0, crossfade_samples)
    fade_in = np.linspace(0, 1, crossfade_samples)
    
    cross_faded_overlap = prev_overlap * fade_out + next_overlap * fade_in
    
    new_wave = np.concatenate([
        wave1[:-crossfade_samples],
        cross_faded_overlap,
        wave2[crossfade_samples:]
    ])
    
    return new_wave

def load_f5_model_colab():
    """Khởi tạo mô hình F5-TTS độc lập ngay trong Notebook"""
    print("[Timeline Prototype] Đang tải mô hình F5-TTS vào bộ nhớ...")
    from omegaconf import OmegaConf
    from hydra.utils import get_class
    from f5_tts.infer.utils_infer import load_model, load_vocoder
    import torch
    
    # Đường dẫn chuẩn trên Colab theo file hướng dẫn của bạn
    ckpt_path = "/content/Vi-F5-TTS/ckpts/model_1000h.pt"
    vocab_path = "/content/Vi-F5-TTS/ckpts/vocab_1000h.txt"
    model_cfg_path = "/content/Vi-F5-TTS/ckpts/vi-fine-tuned-f5-tts.yaml"
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    model_cfg = OmegaConf.load(model_cfg_path)
    model_cls = get_class(f"f5_tts.model.{model_cfg.model.backbone}")
    
    vocoder = load_vocoder(is_local=False, device=device)
    model = load_model(
        model_cls=model_cls,
        model_cfg=model_cfg.model.arch,
        ckpt_path=ckpt_path,
        mel_spec_type="vocos",
        vocab_file=vocab_path,
        ode_method="euler",
        use_ema=True,
        device=device
    )
    print("-> Tải mô hình thành công!")
    return model, vocoder

def dynamic_timeline_inference(
    ref_audio_path, 
    segments, 
    model, 
    vocoder, 
    output_path="output_dynamic.wav",
    target_rms=0.1,
    cross_fade_duration=0.15,
    nfe_step=32,
    cfg_strength=2.0,
    sway_sampling_coef=-1.0
):
    print(f"[Timeline Prototype] Bắt đầu cắt Reference Audio: {ref_audio_path}")
    full_audio = AudioSegment.from_file(ref_audio_path)
    generated_waves = []
    
    from f5_tts.infer.utils_infer import infer_process
    
    for i, seg in enumerate(segments):
        start_ms = int(seg["start_sec"] * 1000)
        end_ms = int(seg["end_sec"] * 1000)
        text_vn = seg["gen_text"]
        
        chunk_audio = full_audio[start_ms:end_ms]
        chunk_ref_path = f"temp_ref_chunk_{i}.wav"
        chunk_audio.export(chunk_ref_path, format="wav")
        
        print(f"\n--- Xử lý Đoạn {i+1} ---")
        print(f"-> Mẫu: {seg['start_sec']}s - {seg['end_sec']}s | Text VN: {text_vn}")
        
        from f5_tts.infer.utils_infer import infer_process, preprocess_ref_audio_text
        
        # Gọi Whisper tự động dịch audio con này ra chữ tiếng Trung
        processed_ref_audio, processed_ref_text = preprocess_ref_audio_text(chunk_ref_path, "")
        print(f"-> Whisper nghe được gốc: {processed_ref_text}")
        
        wave, sr, _ = infer_process(
            ref_audio=processed_ref_audio,
            ref_text=processed_ref_text,  
            gen_text=text_vn,
            model_obj=model,
            vocoder=vocoder,
            speed=1.0,
            nfe_step=nfe_step,
            cfg_strength=cfg_strength,
            sway_sampling_coef=sway_sampling_coef,
            target_rms=target_rms,
            cross_fade_duration=cross_fade_duration
        )
        
        if wave is not None:
            generated_waves.append(wave)
        else:
            print(f"[LỖI] Không thể sinh âm thanh cho đoạn {i+1}")
            
    if not generated_waves:
        print("[LỖI] Không có âm thanh nào được sinh ra!")
        return None
        
    print("\n[Timeline Prototype] Đang ghép nối các đoạn (Crossfade)...")
    final_wave = generated_waves[0]
    for i in range(1, len(generated_waves)):
        final_wave = crossfade_numpy_arrays(final_wave, generated_waves[i])
        
    sf.write(output_path, final_wave, 24000)
    print(f"✅ HOÀN THÀNH! File output đã lưu tại: {output_path}")
    return output_path

# ==========================================
# CÁCH SỬ DỤNG TRÊN COLAB:
# ==========================================
'''
# BƯỚC 1: Load mô hình vào biến cục bộ (Chỉ cần chạy 1 lần đầu)
%cd /content/Vi-F5-TTS
my_model, my_vocoder = load_f5_model_colab()

# BƯỚC 2: Khai báo kịch bản timeline
my_segments = [
    {
        "start_sec": 0.0, 
        "end_sec": 3.0, 
        "gen_text": "Xin chào, ta là bạn của ngươi." # Đoạn bình tĩnh
    },
    {
        "start_sec": 3.0, 
        "end_sec": 6.5, 
        "gen_text": "Nếu ngươi không nghe lời ta, ta sẽ giết ngươi!" # Đoạn gào thét
    }
]

# BƯỚC 3: Chạy sinh audio
out_file = dynamic_timeline_inference(
    ref_audio_path="/content/Vi-F5-TTS/ckpts/my_ref_audio.wav", # CHÚ Ý: Đổi tên file gốc của bạn ở đây!
    segments=my_segments,
    model=my_model,
    vocoder=my_vocoder
)

# BƯỚC 4: Nghe thử
import IPython.display as ipd
ipd.Audio(out_file)
'''
