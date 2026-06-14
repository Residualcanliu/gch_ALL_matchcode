import csv
import re

NAME = "千幻魔镜 XR"
# ===================== 配置区（你只需要改这里的文件名即可）=====================
INPUT_TXT_PATH = f"{NAME}评论.txt"  # 你的原始txt文件路径
OUTPUT_CSV_PATH = f"{NAME}评论.csv"   # 输出的CSV文件路径

# ---------------------- 核心规则配置（新平台适配版）----------------------
# 1. 时间锚点正则：匹配YYYY-MM-DD格式的时间行
TIME_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})")
# 2. 自动提取时间行里的纯净时间（剔除后面的商品规格）
TIME_EXTRACT = re.compile(r"(\d{4}-\d{2}-\d{2})")
# 3. 要完全过滤的行关键词（匹配到就整行删除）
FULL_DELETE_KEYWORDS = [
    "曰回复", "凸", "超赞", "该店铺购买", "回复", "有用",
]
# 4. 商家自动回复过滤关键词（匹配到就整行删除）
SELLER_REPLY_KEYWORDS = [
    "有不周到之处请您谅解", "祝您生活愉快", "我们一直在努力做得更好"
]
# 5. 商品规格行特征（匹配到就整行删除）
PRODUCT_SPEC_KEYWORDS = ["4K蓝光VR", "VR+", "手柄"]
# 6. 过滤无意义短行（字符数小于该值直接删除）
MIN_VALID_LENGTH = 2
# 7. 自动去重（相同时间+相同评论只保留一条）
AUTO_DEDUPLICATE = True


# ==================================================================================

def main():
    # 1. 读取原始文件，预处理每行（去首尾空格、过滤纯空行）
    with open(INPUT_TXT_PATH, "r", encoding="utf-8") as f:
        raw_lines = [line.strip() for line in f.readlines() if line.strip()]

    if not raw_lines:
        print("错误：输入文件为空！")
        return

    # 2. 定位所有时间行的索引，作为评论块的分割锚点
    time_line_indexes = []
    for idx, line in enumerate(raw_lines):
        if TIME_PATTERN.match(line):
            time_line_indexes.append(idx)

    if not time_line_indexes:
        print("错误：未找到任何符合格式的时间行！")
        return

    # 3. 遍历每个时间锚点，拆分并清洗单条评论
    cleaned_data = []
    total_time_count = len(time_line_indexes)

    for i, time_idx in enumerate(time_line_indexes):
        # --- 步骤1：提取纯净的评论时间 ---
        time_raw_line = raw_lines[time_idx]
        # 从行里提取YYYY-MM-DD格式的时间，忽略后面的商品规格
        time_match = TIME_EXTRACT.search(time_raw_line)
        if not time_match:
            continue
        time_str = time_match.group(1)

        # --- 步骤2：确定当前评论的内容范围 ---
        # 起始：时间行的下一行
        comment_start = time_idx + 1
        # 结束：下一个时间行的前一行（最后一条评论则到文件末尾）
        comment_end = time_line_indexes[i + 1] if i + 1 < total_time_count else len(raw_lines)

        # --- 步骤3：逐行清洗评论内容，过滤所有无效行 ---
        valid_comment_parts = []
        for line in raw_lines[comment_start:comment_end]:
            # 规则1：过滤完全匹配删除关键词的行
            if any(keyword in line for keyword in FULL_DELETE_KEYWORDS):
                continue
            # 规则2：过滤商家自动回复行
            if any(keyword in line for keyword in SELLER_REPLY_KEYWORDS):
                continue
            # 规则3：过滤商品规格行
            if any(keyword in line for keyword in PRODUCT_SPEC_KEYWORDS):
                continue
            # 规则4：过滤无意义短行
            if len(line) < MIN_VALID_LENGTH:
                continue
            # 规则5：过滤纯数字/纯字母的无意义行
            if re.fullmatch(r"^[a-zA-Z0-9\s\W]+$", line):
                continue
            # 规则6：过滤带***的用户名行
            if "***" in line:
                continue
            # 保留有效内容
            valid_comment_parts.append(line)

        # 把多行评论拼接成完整的一条，换行换成空格
        full_comment = " ".join(valid_comment_parts).replace("\n", " ")
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
        seen = set()
        deduplicated_data = []
        for item in cleaned_data:
            unique_key = f"{item['评论时间']}_{item['评论内容']}"
            if unique_key not in seen:
                seen.add(unique_key)
                deduplicated_data.append(item)
        cleaned_data = deduplicated_data

    # 5. 写入CSV文件（Excel打开不乱码）
    with open(OUTPUT_CSV_PATH, "w", encoding="utf-8-sig", newline="") as csvfile:
        fieldnames = ["评论时间", "评论内容"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_data)

    # 输出统计结果
    print(f"数据清洗完成！")
    print(f"共提取有效评论：{len(cleaned_data)} 条")
    print(f"清洗后的文件已保存到：{OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()