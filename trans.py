import yaml
import time
from openai import Client

# YAML Dumper tùy chỉnh để đảm bảo format đẹp
class CustomDumper(yaml.Dumper):
    def represent_scalar(self, tag, value, style=None):
        # Dùng block style '|' cho văn bản nhiều dòng
        if "\n" in value:
            style = '|'
        elif any(c in value for c in ['\\', '"', '\'']):
            # Dùng double-quote nếu có ký tự đặc biệt
            style = '"'
        return super().represent_scalar(tag, value, style)

def load_yaml(file_path):
    """Tải file YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml(data, file_path):
    """Lưu file YAML."""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, Dumper=CustomDumper)

def load_prompt(file_path):
    """Tải nội dung prompt từ file và hợp nhất thành một dòng."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return " ".join(line.strip() for line in f if line.strip())

def translate_segment(segment_content, client, system_prompt, assistant_prompt):
    """Gửi nội dung segment tới API GPT để dịch."""
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": assistant_prompt},
                {"role": "user", "content": f"Dịch từ tiếng Trung sang tiếng Việt đoạn văn sau:\n\n{segment_content}"}
            ],
            model="gpt-4o-mini-2024-07-18",
            max_tokens=5000,
            temperature=0.7
        )
        # Truy cập nội dung đã dịch
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)  # Trả về lỗi nếu có

def main():
    print("--- Dịch YAML bằng GPT ---")
    
    # Các giá trị mặc định
    input_file = input("Nhập tên file YAML cần dịch (mặc định: content.yaml): ").strip() or "content.yaml"
    output_file = input("Nhập tên file YAML để lưu kết quả (mặc định: output.yaml): ").strip() or "output.yaml"
    start_segment = int(input("Nhập số segment bắt đầu (mặc định: 1): ").strip() or 1)
    end_segment = int(input("Nhập số segment kết thúc (để trống nếu muốn dịch hết): ").strip() or -1)
    system_prompt_file = input("Nhập tên file chứa system prompt (mặc định: system.txt): ").strip() or "system.txt"
    assistant_prompt_file = input("Nhập tên file chứa assistant prompt (mặc định: assistant.txt): ").strip() or "assistant.txt"
    api_key = input("Nhập API key của bạn: ").strip()

    # Khởi tạo client OpenAI
    client = Client(api_key=api_key)

    # Tải nội dung các prompt
    system_prompt = load_prompt(system_prompt_file)
    assistant_prompt = load_prompt(assistant_prompt_file)

    # Tải nội dung file YAML
    data = load_yaml(input_file)

    # Xác định phạm vi segment
    if end_segment == -1:  # Nếu không nhập end_segment
        end_segment = len(data)

    translated_segments = []
    log_file = "translation_log.txt"

    # Mở file log
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("--- Log Dịch ---\n")

        # Lặp qua các segment được yêu cầu
        for idx, segment in enumerate(data[start_segment-1:end_segment], start=start_segment):
            print(f"Đang dịch segment {idx}...")
            log.write(f"Segment {idx}: ")

            original_content = segment['content']
            translated_content, error = translate_segment(original_content, client, system_prompt, assistant_prompt)

            if translated_content:
                # Ghi log thành công
                print(f"Segment {idx} dịch thành công.")
                log.write("Thành công\n")

                # Cập nhật nội dung đã dịch vào segment
                segment['content'] = translated_content
            else:
                # Ghi log lỗi
                print(f"Segment {idx} dịch thất bại: {error}")
                log.write(f"Thất bại - {error}\n")

            # Thêm segment đã dịch hoặc chưa dịch vào danh sách
            translated_segments.append(segment)

            # Ghi kết quả sau mỗi segment
            save_yaml(translated_segments, output_file)

            # Chờ 135 giây trước khi tiếp tục
            time.sleep(135)

    print(f"Dịch hoàn tất. Kết quả được lưu vào file '{output_file}'.")
    print(f"Log chi tiết được lưu vào file '{log_file}'.")

if __name__ == "__main__":
    main()

