# 此函数用于将输入的文件分成20个子文件并保存到特定路径，防止因数据量过大处理困难
import pandas as pd

# 读取 CSV 文件
file_path = "rb2405.csv" 
df = pd.read_csv(file_path)

# 将列名转换为小写
df.columns = [col.lower() for col in df.columns]

# 增加一列 "factor"，所有值设置为 1
df["factor"] = 1

# 统计总行数
total_rows = df.shape[0]
print(f"原始数据总行数: {total_rows}")

# 设置分组数（20个文件）
num_groups = 20

# 输出文件的基础名称
output_base = "mydata/rb2405_part"

# 遍历分组并保存
for j in range(num_groups):
    # 获取当前分组数据，第 j 行、第 j+20 行、第 j+40 行...
    group_data = df.iloc[j::num_groups]
    
    # 生成输出文件名
    output_path = f"{output_base}_{j + 1}.csv"
    
    # 保存分组数据到 CSV 文件
    group_data.to_csv(output_path, index=False)
    print(f"保存 {output_path}，包含 {len(group_data)} 行")

print("处理完成！所有拆分文件已保存。")