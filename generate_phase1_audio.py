import os
import subprocess

def create_ssml_file(filename, content):
    ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'>
    <voice name='zh-CN-YunxiNeural'>
        {content}
    </voice>
</speak>"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ssml)

# Text: "你好，我是你的朋友。" (Hello, I am your friend)
# Text: "如果你不听我的话，我就杀了你！" (If you don't listen to me, I will kill you!)

os.makedirs("Phase1_Tests", exist_ok=True)

# Test 1: Toàn bộ bình tĩnh
create_ssml_file("Phase1_Tests/t1.ssml", 
    "<prosody rate='0%' pitch='0%' volume='default'>你好，我是你的朋友。如果你不听我的话，我就杀了你！</prosody>")

# Test 2: Đầu bình tĩnh, cuối hét (To to, cao độ tăng mạnh, nói nhanh hơn một chút)
create_ssml_file("Phase1_Tests/t2.ssml", 
    "<prosody rate='-10%' pitch='-10%' volume='default'>你好，我是你的朋友。</prosody> "
    "<prosody rate='+20%' pitch='+40%' volume='x-loud'>如果你不听我的话，我就杀了你！</prosody>")

# Test 3: Đầu hét, cuối bình tĩnh
create_ssml_file("Phase1_Tests/t3.ssml", 
    "<prosody rate='+20%' pitch='+40%' volume='x-loud'>你好，我是你的朋友！</prosody> "
    "<prosody rate='-10%' pitch='-10%' volume='default'>如果你不听我的话，我就杀了你。</prosody>")

# Test 4: Nói nhanh
create_ssml_file("Phase1_Tests/t4.ssml", 
    "<prosody rate='+50%' pitch='0%' volume='default'>你好，我是你的朋友。如果你不听我的话，我就杀了你！</prosody>")

# Test 5: Nói chậm
create_ssml_file("Phase1_Tests/t5.ssml", 
    "<prosody rate='-40%' pitch='0%' volume='default'>你好，我是你的朋友。如果你不听我的话，我就杀了你！</prosody>")

print("Đang tạo 5 file Audio cực đoan bằng Edge-TTS...")
for i in range(1, 6):
    print(f"Generating Test {i}...")
    subprocess.run(["edge-tts", "-f", f"Phase1_Tests/t{i}.ssml", "--write-media", f"Phase1_Tests/Test{i}.mp3"])
    os.remove(f"Phase1_Tests/t{i}.ssml")

print("Hoàn thành! Các file đã được lưu trong thư mục Phase1_Tests/")
