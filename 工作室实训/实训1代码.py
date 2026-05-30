# 1. 导入必要库（仅需pandas，实训中未使用其他库）
import pandas as pd


# 2. 数据读取（⚠️ 请将路径替换为你电脑中数据文件的实际路径！）
# 读取全球儿童营养不良数据（Global_data.csv）和儿童营养状态数据（data.csv）
data1 = pd.read_csv(r"D:\PythonObjectAll\工作室实训\data\Global_data.csv")
data3 = pd.read_csv(r"D:\PythonObjectAll\工作室实训\data\data.csv")

# 查看全球数据的后10行（验证读取结果）
print("=== 全球儿童营养不良数据后10行 ===")
print(data1.tail(10))
print("\n")


# 3. 全球儿童营养不良信息数据处理（对应实训4.2步骤）
# 3.1 删除末尾5行无效数据（原数据末尾为说明性行，非有效国家数据）
data1.drop(data1.tail(5).index, inplace=True)
print("=== 删除无效数据后，全球数据的后10行 ===")
print(data1.tail(10))
print("\n")

# 3.2 列名修改：将“2020 1”改为“2020”（统一年份列名格式）
data1.rename(columns={'2020 1': '2020'}, inplace=True)
print("=== 列名修改后，全球数据的前5行 ===")
print(data1.head())
print("\n")

# 3.3 查看Note列的异常值分布（确认需删除的标记）
print("=== Note列的值分布 ===")
print(data1['Note'].value_counts())
print("\n")

# 3.4 删除Note列为2、3的数据（无效标记数据）
data1 = data1[~data1['Note'].isin([2, 3])]  # 合并条件，简化代码
# 3.5 删除2000列中值为“-”的无效数据（原数据中“-”代表缺失，需剔除）
data1 = data1[~data1['2000'].isin(["-"])]
print(f"=== 删除无效数据后，全球数据的形状（行×列）：{data1.shape} ===")
print("\n")

# 3.6 查看Indicator/Measure/Estimate列的唯一值（确认无分析意义，可删除）
print("=== Indicator列唯一值数量：", data1['Indicator'].nunique())
print("=== Measure列唯一值数量：", data1['Measure'].nunique())
print("=== Estimate列唯一值数量：", data1['Estimate'].nunique())
print("\n")

# 3.7 删除无分析意义的字段（Note/Indicator/Measure/Estimate）
data2 = data1.drop(['Note', 'Indicator', 'Measure', 'Estimate'], axis=1)  # 统一变量名为data2（原文档Data2大小写错误修正）
print("=== 删除无用字段后，data2的前5行 ===")
print(data2.head())
print("\n")

# 3.8 转换数据类型：将2000~2020年份列转为float（便于后续数值分析）
year_columns = data2.columns[2:]  # 年份列：从第3列开始（前2列为ISO code、Country）
data2[year_columns] = data2[year_columns].astype(float)
print("=== 2020列的数据类型（应显示float64） ===")
print(data2['2020'].dtype)
print("\n")

# 3.9 重复值检测（确认无重复数据）
print(f"=== data2中的重复值数量：{data2.duplicated().sum()} ===")
# 3.10 缺失值检测（确认无缺失数据）
print(f"=== data2中的总缺失值数量：{data2.isna().sum().sum()} ===")
print("\n")

# 3.11 重置索引（删除原索引，重新按顺序编号）
data2.reset_index(drop=True, inplace=True)
print("=== 重置索引后，data2的后5行 ===")
print(data2.tail())
print("\n")


# 4. 儿童营养状态数据处理（对应实训4.3步骤）
# 4.1 重复值检测（确认无重复数据）
print(f"=== 儿童营养数据（data3）中的重复值数量：{data3.duplicated().sum()} ===")
# 4.2 缺失值检测（查看各列缺失情况）
print("=== 儿童营养数据各列缺失值数量 ===")
print(data3.isna().sum())
print("\n")

# 4.3 缺失值处理：删除包含缺失值的行（直接剔除不完整数据）
data3 = data3.dropna()
print(f"=== 删除缺失值后，儿童营养数据的形状（行×列）：{data3.shape} ===")
print("\n")

# 4.4 数据类型转换：将Diet和Status列转为int（原数据可能为object类型，需转为数值型）
data3['Diet'] = data3['Diet'].astype(int)
data3['Status'] = data3['Status'].astype(int)
print("=== 转换类型后，儿童营养数据的前5行 ===")
print(data3.head())
print("\n")

# 4.5 设置索引：将Name列设为DataFrame的索引（便于按姓名查询）
data3.set_index('Name', inplace=True)
print("=== 设置Name为索引后，儿童营养数据的前5行 ===")
print(data3.head())