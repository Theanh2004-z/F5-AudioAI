"""
run_orchestrator.py
This script acts as the bridge between F5-TTS (Voice Generation) and the Controller (AI Brain).
To run on Colab T4:
1. Git clone this repository.
2. Install F5-TTS dependencies.
3. Run this script.
"""
import os
import json
import time
import sys

# Thêm đường dẫn project vào sys.path để các module có thể import nhau
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Hàm giả lập F5-TTS Generation.
# Trong môi trường Production thật, sếp sẽ viết code Load Model F5-TTS và gọi hàm infer_process() tại đây.
def mock_generate_audio(ref_audio, text, speed):
    time.sleep(1)
    return "mock_generated_audio.wav"

from controller.inference_engine.inference_engine import run_inference
from controller.recommendation_engine.recommendation_engine import generate_recommendation

def create_mock_live_sample(text, speed):
    """
    Trong thực tế, sếp sẽ truyền file âm thanh qua thư viện parselmouth/librosa để đo đạc thực tế.
    Ở đây dùng Mock để giả lập.
    """
    return {
        "metadata": {
            "text_length": len(text),
            "speed_setting": speed
        },
        "feature_statistics": {
            "pitch": {"mean": 120.0},
            "speed_ratio": {"mean": 1.0 * speed}
        }
    }

def auto_dubbing_loop(text, ref_audio, max_retries=3):
    current_speed = 1.0
    
    # Đảm bảo các thư mục luôn tồn tại
    os.makedirs("dataset/inference", exist_ok=True)
    os.makedirs("dataset/recommendation", exist_ok=True)
    
    # Khởi tạo luật chữa lỗi tĩnh cho Stage 9
    rules_path = "recommendation_rules.json"
    if not os.path.exists(rules_path):
        with open(rules_path, "w", encoding="utf-8") as f:
            json.dump({
                "rules": [
                    {
                        "condition": {"prediction_value": 0}, # 0 là bị REJECT
                        "action_id": "ACT-ADJUST-SPEED",
                        "priority": 100,
                        "action_metadata": {"delta": -0.1}
                    }
                ]
            }, f, indent=4)
            
    # Lấy thông tin model từ Registry của Stage 7
    registry_path = "dataset/models/model_registry.json"
    if not os.path.exists(registry_path):
        print("[WARNING] Không tìm thấy production_model. Đang tự động đúc 1 cái Não giả lập (Mock Model)...")
        from controller.offline_learning.offline_learning_engine import train_offline_models
        ds_path, rsn_path, pol_path = "test_ds.json", "test_rsn.json", "test_pol.json"
        ds = [{"learning_record_id": f"LRN-{i}", "metadata": {"val": i}, "feature_statistics": {"f1": {"mean": i*0.1}}} for i in range(20)]
        with open(ds_path, "w") as f: json.dump(ds, f)
        with open(rsn_path, "w") as f: json.dump({"findings": []}, f)
        pols = [{"traceability": {"matched_learning_record_ids": [f"LRN-{i}"]}, "policy_type": "POLICY_ACCEPT" if i % 2 == 0 else "POLICY_REJECT"} for i in range(20)]
        with open(pol_path, "w") as f: json.dump({"policies": pols}, f)
        train_offline_models(ds_path, rsn_path, pol_path, "dataset/models")
        
        # Fix missing pipeline
        import pickle
        class DummyPipeline:
            def transform(self, X): return X.values
        with open("dataset/models/trained_models/feature_pipeline.pkl", "wb") as f:
            pickle.dump(DummyPipeline(), f)
            
        for tmp_f in [ds_path, rsn_path, pol_path]:
            if os.path.exists(tmp_f): os.remove(tmp_f)
            
        print("[SUCCESS] Đã đúc xong Không gian Não giả lập. Sẵn sàng!\n")
        
    for attempt in range(1, max_retries + 1):
        print(f"\n[ORCHESTRATOR] --- Vòng lặp thứ {attempt} ---")
        
        # 1. Bắt F5-TTS đẻ Audio (Dùng hàm Mock cho mục đích demo)
        print(f"[F5-TTS] Đang sinh Audio với tốc độ {current_speed}...")
        gen_audio = mock_generate_audio(ref_audio=ref_audio, text=text, speed=current_speed)
        
        # 2. Đo đạc file Audio (Mô phỏng Stage 1-5)
        sample_path = f"dataset/inference/live_sample_{attempt}.json"
        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump(create_mock_live_sample(text, current_speed), f, indent=4)
            
        # 3. Kích hoạt Bộ Não: Suy luận (Stage 8)
        print("[STAGE 8] Đang đưa cho AI chấm điểm...")
        try:
            prediction_result = run_inference(sample_path, registry_path)
            pred_val = prediction_result["prediction"]["prediction_value"]
            print(f"   => AI Phán Quyết: {pred_val} (Độ tự tin: {prediction_result['prediction']['confidence_score']})")
        except Exception as e:
            print(f"   => Lỗi suy luận: {e}")
            break
            
        # Giả định 1 là ACCEPT, 0 là REJECT
        if pred_val == 1:
            print("[ORCHESTRATOR] ✅ AI CHẤP NHẬN. File đạt chuẩn hoàn hảo!")
            return gen_audio
            
        # 4. Kích hoạt Bộ Não: Xin lời khuyên (Stage 9)
        print("[STAGE 9] ❌ AI TỪ CHỐI. Đang tra cứu Sổ tay kinh nghiệm để sửa lỗi...")
        prediction_path = os.path.join("dataset/inference", f"prediction_{prediction_result['inference_session_id']}.json")
        try:
            rec_result = generate_recommendation(prediction_path, rules_path)
            action = rec_result["primary_action_id"]
            
            print(f"   => Lời khuyên (Action ID): {action}")
            if action == "ACT-ADJUST-SPEED":
                delta = rec_result["action_metadata"].get("delta", -0.1)
                current_speed += delta
                print(f"[ORCHESTRATOR] Áp dụng sửa chữa: Thay đổi tốc độ về {current_speed:.2f}")
            else:
                print("[ORCHESTRATOR] Hành động nằm ngoài tầm tự động hóa. Chờ con người xử lý.")
                break
        except Exception as e:
            print(f"   => Lỗi sinh khuyến nghị: {e}")
            break

    print("[ORCHESTRATOR] ⚠️ Vượt quá số lần thử nghiệm tối đa. Audio không đạt chuẩn.")
    return None

if __name__ == "__main__":
    print("=========================================================")
    print(" F5 AI SYSTEM - HỆ THỐNG ĐIỀU PHỐI LỒNG TIẾNG TỰ ĐỘNG ")
    print("=========================================================")
    test_text = "Chào mừng sếp đến với kỷ nguyên AI lồng tiếng tự động."
    test_ref = "ref_voice.wav"
    
    auto_dubbing_loop(test_text, test_ref)
