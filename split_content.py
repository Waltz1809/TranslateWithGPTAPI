import re
import yaml
import cn2an  # Thư viện chuyển số Hán tự sang số Ả Rập

# YAML Dumper tùy chỉnh để sử dụng `|` cho nội dung nhiều dòng
class CustomDumper(yaml.Dumper):
    def represent_scalar(self, tag, value, style=None):
        if tag == 'tag:yaml.org,2002:str' and "\n" in value:
            style = '|'
        return super().represent_scalar(tag, value, style)

def convert_chinese_number_to_arabic(chinese_number):
    """Chuyển đổi số Hán tự sang số Ả Rập."""
    try:
        return cn2an.cn2an(chinese_number, mode="smart")
    except ValueError:
        return None

def clean_empty_lines(lines):
    """Loại bỏ các dòng trống dư thừa."""
    return [line for line in lines if line.strip()]

def split_chapters_and_segments_to_yaml(file_path, max_chars=700, output_file="output_segments.yaml"):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    chapters = []
    current_chapter = []
    current_chapter_number = None
    seen_chapters = set()  # Để tránh lặp chương

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Kiểm tra các mẫu tiêu đề chương
        match_chinese = re.match(r'^第([一二三四五六七八九十百千]+)章', line)
        match_arabic = re.match(r'^第(\d{1,3})章', line)
        match_loose = re.match(r'^(\d{1,3})([^\d].*)$', line)

        chapter_number = None

        if match_chinese:
            chapter_number = convert_chinese_number_to_arabic(match_chinese.group(1))
        elif match_arabic:
            chapter_number = int(match_arabic.group(1))
        elif match_loose:
            chapter_number = int(match_loose.group(1))

        # Nếu nhận diện được số chương
        if chapter_number and 1 <= chapter_number <= 663:
            # Kiểm tra trùng lặp
            if chapter_number in seen_chapters:
                continue
            seen_chapters.add(chapter_number)

            # Lưu chương hiện tại (nếu có)
            if current_chapter:
                chapters.append((current_chapter_number, current_chapter))
                current_chapter = []

            # Bắt đầu chương mới
            current_chapter_number = chapter_number
            current_chapter.append(line)
        else:
            # Nếu không phải tiêu đề chương, thêm vào nội dung chương hiện tại
            if current_chapter is not None:
                current_chapter.append(line)

    # Thêm chương cuối cùng
    if current_chapter:
        chapters.append((current_chapter_number, current_chapter))

    all_segments = []
    segment_id = 1

    # Tách chương thành các segments
    for chapter_number, chapter_lines in chapters:
        title = chapter_lines[0]
        content_lines = chapter_lines[1:]
        current_segment = []
        current_length = 0

        for line in content_lines:
            line_length = len(re.sub(r'\s+', '', line))
            if current_length + line_length > max_chars:
                all_segments.append({
                    "id": f"Chapter_{chapter_number}_Segment_{segment_id}",
                    "title": title,
                    "content": "\n".join(current_segment)
                })
                segment_id += 1
                current_segment = []
                current_length = 0

            current_segment.append(line)
            current_length += line_length

        if current_segment:
            all_segments.append({
                "id": f"Chapter_{chapter_number}_Segment_{segment_id}",
                "title": title,
                "content": "\n".join(current_segment)
            })
            segment_id += 1

    # Lưu các segment vào file YAML
    with open(output_file, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(
            all_segments,
            yaml_file,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            Dumper=CustomDumper
        )

    print(f"Đã lưu các segment vào file '{output_file}'")

# Thay 'your_file.txt' bằng file của bạn
split_chapters_and_segments_to_yaml("your_file.txt")
