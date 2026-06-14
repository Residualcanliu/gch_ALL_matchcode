import csv
import re

NAME = "ABDT全景vr"
# ===================== 配置区（你只需要改这里的文件名即可）=====================
INPUT_TXT_PATH = f"{NAME}评论.txt"  # 你的原始txt文件路径
OUTPUT_CSV_PATH = f"{NAME}评论.csv"  # 输出的CSV文件路径
# 时间锚点正则（匹配2024/2025/2026年开头的行）
TIME_PATTERN = re.compile(r"^(2024|2025|2026)年")
# 要删除的行关键词
DELETE_KEYWORD = "已购:  "
# 自动修正OCR识别错误（把时间行末尾的"8"改成"日"，比如"2026年2月218"→"2026年2月21日"）
AUTO_FIX_TIME = True
# 过滤无意义垃圾行（比如Face、Cushion、1I这种）
FILTER_GARBAGE = True
# 自动去重（相同时间+相同评论只保留一条）
AUTO_DEDUPLICATE = True


# ==================================================================================

def main():
    # 1. 读取原始txt文件，预处理每一行
    with open(INPUT_TXT_PATH, "r", encoding="utf-8") as f:
        # 去掉每行首尾空格、过滤纯空行
        raw_lines = [line.strip() for line in f.readlines() if line.strip()]

    if not raw_lines:
        print("错误：输入文件为空！")
        return

    # 2. 定位所有时间行的索引，拆分评论块
    time_line_indexes = []
    for idx, line in enumerate(raw_lines):
        if TIME_PATTERN.match(line):
            time_line_indexes.append(idx)

    if not time_line_indexes:
        print("错误：未找到任何符合格式的时间行！")
        return

    # 3. 遍历每个时间锚点，清洗提取数据
    cleaned_data = []
    for time_idx in time_line_indexes:
        # --- 规则1：删除时间行的上一行（用户名），所以跳过time_idx-1的行
        # --- 提取当前评论的时间
        time_str = raw_lines[time_idx]
        # 修正OCR识别的时间错误（把末尾的8改成日）
        if AUTO_FIX_TIME and time_str.endswith("8"):
            time_str = time_str[:-1] + "日"

        # --- 确定当前评论的内容范围：从时间行的下一行，到下一个时间行的上两行（下一个用户名行）
        current_start = time_idx + 1
        # 找下一个时间行的索引
        next_time_idx = time_line_indexes[time_line_indexes.index(time_idx) + 1] if time_line_indexes.index(
            time_idx) + 1 < len(time_line_indexes) else len(raw_lines)
        # 内容结束位置：下一个时间行的上两行（跳过下一个评论的用户名行）
        current_end = next_time_idx - 1 if next_time_idx < len(raw_lines) else len(raw_lines)

        # --- 提取当前评论的所有行，执行清洗规则
        comment_lines = raw_lines[current_start:current_end]
        valid_comment_parts = []
        for line in comment_lines:
            # 规则2：删除包含"已购:  "的行
            if DELETE_KEYWORD in line:
                continue
            # 规则3：过滤无意义垃圾行
            if FILTER_GARBAGE:
                # 过滤长度小于2的行、纯字母/数字的行
                if len(line) < 2 or re.fullmatch(r"^[a-zA-Z0-9\s]+$", line):
                    continue
            # 保留有效评论行
            valid_comment_parts.append(line)

        # 把多行评论拼接成完整的一条
        full_comment = "".join(valid_comment_parts)
        # 跳过空评论
        if not full_comment.strip():
            continue

        # 加入清洗后的数据
        cleaned_data.append({
            "评论时间": time_str,
            "评论内容": full_comment
        })

    # 4. 自动去重
    if AUTO_DEDUPLICATE:
        # 用 时间+内容 作为唯一键去重
        seen = set()
        deduplicated_data = []
        for item in cleaned_data:
            unique_key = f"{item['评论时间']}_{item['评论内容']}"
            if unique_key not in seen:
                seen.add(unique_key)
                deduplicated_data.append(item)
        cleaned_data = deduplicated_data

    # 5. 写入CSV文件
    with open(OUTPUT_CSV_PATH, "w", encoding="utf-8-sig", newline="") as csvfile:
        # CSV列名：第一列时间，第二列评论
        fieldnames = ["评论时间", "评论内容"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # 写入表头
        writer.writeheader()
        # 写入所有数据
        writer.writerows(cleaned_data)

    # 输出统计信息
    print(f"数据清洗完成！")
    print(f"共提取有效评论：{len(cleaned_data)} 条")
    print(f"清洗后的文件已保存到：{OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()