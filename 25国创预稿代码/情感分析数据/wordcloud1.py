# -------------------------- 1. 导入依赖库 --------------------------
import jieba
import pandas as pd
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 解决matplotlib中文显示问题
plt.rcParams["font.sans-serif"] = ["SimHei"]  # Windows用这个
# plt.rcParams["font.sans-serif"] = ["PingFang SC"]  # Mac用这个，注释上面一行，打开这一行
plt.rcParams["axes.unicode_minus"] = False

# -------------------------- 2. 全局配置区（只需要改这里的路径和参数） --------------------------
# 3个评论文件路径，按你的实际文件名修改
COMMENT_FILE_PATHS = [
    "B站ai眼镜评论数据_合并情感分析.csv",
    "微博ai眼镜评论数据_合并情感分析.csv",
    "抖音ai眼镜评论数据_合并情感分析.csv"
]
# 评论内容所在的列名，必须和你的文件里的列名完全一致
COMMENT_COLUMN = "评论内容"
# 停用词文件路径
STOPWORDS_PATH = "stopwords.txt"
# 自定义保留核心词文件路径
RESERVED_WORDS_PATH = "reserved_keywords.txt"
# 词云生成后保存的文件名
WORDCLOUD_SAVE_NAME = "全量评论词云图1.png"
# 中文字体路径（解决词云中文乱码，必填！）
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"
# 词云图片尺寸、分辨率配置
WORDCLOUD_WIDTH = 800
WORDCLOUD_HEIGHT = 600
WORDCLOUD_DPI = 300


# -------------------------- 3. 读取txt文件：停用词+保留核心词 --------------------------
def load_words_from_txt(file_path):
    """从txt文件读取词汇，返回去重后的集合，适配停用词/保留词读取"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # 逐行读取，去除首尾空格、换行符、特殊符号，过滤空行
            words_set = set()
            for line in f:
                clean_word = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", line.strip())
                if clean_word:
                    words_set.add(clean_word)
        print(f"成功读取文件 {file_path}，共加载 {len(words_set)} 个词汇")
        return words_set
    except FileNotFoundError:
        print(f"错误：未找到文件 {file_path}，请检查文件名和路径是否正确")
        return set()
    except Exception as e:
        print(f"读取文件 {file_path} 失败：{str(e)}")
        return set()


# 加载停用词和保留词
stopwords_set = load_words_from_txt(STOPWORDS_PATH)
reserved_words_set = load_words_from_txt(RESERVED_WORDS_PATH)

# -------------------------- 4. 批量读取3个评论文件，合并全量数据 --------------------------
all_comments = []
for file_path in COMMENT_FILE_PATHS:
    try:
        # 自动识别csv/excel文件，读取数据
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            print(f"跳过不支持的文件格式：{file_path}，仅支持csv/xlsx/xls")
            continue

        # 校验评论列是否存在
        if COMMENT_COLUMN not in df.columns:
            print(f"文件 {file_path} 中未找到列名 [{COMMENT_COLUMN}]，请检查列名配置")
            continue

        # 提取评论列，加入全量列表
        comment_list = df[COMMENT_COLUMN].dropna().astype(str).tolist()
        all_comments.extend(comment_list)
        print(f"成功读取文件 {file_path}，加载有效评论 {len(comment_list)} 条")

    except FileNotFoundError:
        print(f"错误：未找到文件 {file_path}，请检查文件名和路径是否正确")
    except Exception as e:
        print(f"读取文件 {file_path} 失败：{str(e)}")

# 校验是否读取到有效评论
if not all_comments:
    print("错误：未读取到任何有效评论数据，程序终止")
    exit()
print(f"\n3个文件合计加载有效评论 {len(all_comments)} 条，开始文本处理...")


# -------------------------- 5. 【6层强过滤】文本分词+停用词过滤（核心痛点词强制保留） --------------------------
def clean_text(text):
    """预处理评论文本，去除特殊符号、表情、英文无意义字符，只保留中文、数字、英文"""
    # 去除网址、@用户、#话题、emoji、标点符号、特殊字符
    text = re.sub(r"http\S+", "", text)  # 去除网址
    text = re.sub(r"@\w+", "", text)  # 去除@用户
    text = re.sub(r"#.*?#", "", text)  # 去除话题
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", " ", text)  # 只保留中文/英文/数字
    text = re.sub(r"\s+", " ", text).strip()  # 合并多余空格
    return text


def comment_cut_and_filter(text):
    """单条评论分词+6层强过滤处理，彻底清除无效词"""
    # 第一步：文本清洗
    clean_comment = clean_text(text)
    if not clean_comment:
        return []

    # 第二步：jieba精准分词
    word_list = jieba.lcut(clean_comment)

    # 第三步：6层强过滤规则（保留词优先级最高，直接跳过所有过滤）
    result_words = []
    for word in word_list:
        # 【强制保留层】自定义核心痛点词，直接保留，无视所有过滤规则
        if word in reserved_words_set:
            result_words.append(word)
            continue

        # 【过滤层1】去除停用词
        if word in stopwords_set:
            continue

        # 【过滤层2】去除长度小于2的单字/单字符（彻底解决单字残留）
        if len(word) < 2:
            continue

        # 【过滤层3】去除纯数字/纯英文无意义词汇（只保留你定义的核心英文词）
        if word.isdigit():
            continue
        if word.isascii() and word not in reserved_words_set:
            continue

        # 【过滤层4】去除无意义的叠词/语气词残留
        invalid_patterns = ["哈哈", "哈哈哈哈", "卧槽", "哇", "啊", "呀", "呢", "吧", "吗"]
        if any(pattern in word for pattern in invalid_patterns):
            continue

        # 【过滤层5】去除纯动词/无意义虚词残留
        invalid_verbs = ["看", "说", "去", "来", "有", "是", "在", "和", "与", "或", "而", "及", "对", "给", "把", "被",
                         "让", "为", "以", "于", "之"]
        if word in invalid_verbs:
            continue

        # 所有过滤都通过，保留该词
        result_words.append(word)

    return result_words


# 全量评论批量处理
all_words = []
for comment in all_comments:
    cut_words = comment_cut_and_filter(comment)
    all_words.extend(cut_words)

# 校验是否有有效分词结果
if not all_words:
    print("错误：分词后无有效词汇，请检查停用词和评论内容，程序终止")
    exit()
print(f"文本处理完成，合计有效分词 {len(all_words)} 个，开始生成词云图...")

# 把分词结果拼接成空格分隔的字符串（词云输入要求）
words_for_wordcloud = " ".join(all_words)

# -------------------------- 6. 生成并保存词云图 --------------------------
# 词云核心配置，可按需修改参数
wordcloud = WordCloud(
    font_path=FONT_PATH,  # 中文字体，解决乱码
    width=WORDCLOUD_WIDTH,  # 图片宽度
    height=WORDCLOUD_HEIGHT,  # 图片高度
    background_color="white",  # 背景色，可改成black等
    max_words=200,  # 词云显示最大词汇数
    max_font_size=200,  # 最大字号
    min_font_size=10,  # 最小字号
    collocations=False,  # 关闭重复词汇统计
    prefer_horizontal=0.9,  # 横向词汇占比
    stopwords=stopwords_set  # 词云层二次过滤停用词
)

# 生成词云
wordcloud.generate(words_for_wordcloud)

# 保存词云图片
wordcloud.to_file(WORDCLOUD_SAVE_NAME)
print(f"优化版词云图已生成并保存为：{WORDCLOUD_SAVE_NAME}")

# 弹窗展示词云图
plt.figure(figsize=(16, 9), dpi=WORDCLOUD_DPI)
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")  # 关闭坐标轴
plt.tight_layout()
plt.show()