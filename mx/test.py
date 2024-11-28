import pandas as pd
import numpy as np
import math

# 读取CSV文件
csv_file_path = "RB_3s.csv"
df = pd.read_csv(csv_file_path)
import pandas as pd



# 计算滚动窗口的均值
df['ts_mean_openav1_30'] = df['Openav1'].rolling(window=30).mean()

# 按照公式计算因子
df['factor'] = (-1)*(
    (df['Openap4'] + df['Openav1']) /
    (
        (30.0 + ((df['ts_mean_openav1_30'] * 0.01) * 0.5)) * df['Close']
    )
)

# 计算因子的值：买1的amt - 卖1的amt
#factor1 = df["Closebv1"]*df["Closebp1"] -df["Closeav1"]*df["Closeap1"]
#factor1 = math.log(0.5 * (math.log(((df["Close"] + 2.0) * ((-10.0 / df["High"]) / -5.0) * 5.0)) / -0.5))
# 不同时间间隔下的未来收益率数据
r1 = df["r1"]
r2 = df["r2"]
r3 = df["r3"]
r4 = df["r4"]

# 将收益率数据向前移动对应的时间步数
r1_shifted = r1.shift(-1)  # 3秒，因此移动1步
r2_shifted = r2.shift(-1) # 30秒，3秒的10倍，因此移动10步
r3_shifted = r3.shift(-1) # 60秒，3秒的20倍，因此移动20步
r4_shifted = r4.shift(-1) # 300秒，3秒的100倍，因此移动100步

# 将计算后的因子值和移动后的收益率数据添加回DataFrame
#df['factor1'] = factor1
df['r1_shifted'] = r1_shifted
df['r2_shifted'] = r2_shifted
df['r3_shifted'] = r3_shifted
df['r4_shifted'] = r4_shifted

# 移除NaN值
df = df.dropna(subset=['factor1', 'r1_shifted', 'r2_shifted', 'r3_shifted', 'r4_shifted'])

# 定义计算IC的函数
def calculate_ic(group, factor_column, return_column):
    factor_values = group[factor_column].dropna()
    return_values = group[return_column].dropna()

    # 确保两个序列长度相同
    mask = factor_values.index == return_values.index
    factor_values = factor_values[mask]
    return_values = return_values[mask]

    # 计算Spearman秩相关系数
    corr = factor_values.corr(return_values, method='spearman')
    # 计算皮尔逊相关系数
    #corr = factor_values.corr(return_values)
    # 计算皮尔逊相关系数
    #corr_matrix = np.corrcoef(factor_values, return_values)

    # corr_matrix[0,1] 或者 corr_matrix[1,0] 就是 factor_values 和 return_values 之间的相关系数
    #corr = corr_matrix[0, 1]

    return corr

# 按日期分组并计算每个分组的IC值
ic_by_date1 = df.groupby('Tradingday').apply(calculate_ic, 'factor1', 'r1_shifted')
ic_by_date2 = df.groupby('Tradingday').apply(calculate_ic, 'factor1', 'r2_shifted')
ic_by_date3 = df.groupby('Tradingday').apply(calculate_ic, 'factor1', 'r3_shifted')
ic_by_date4 = df.groupby('Tradingday').apply(calculate_ic, 'factor1', 'r4_shifted')

# 打印IC值
print("IC值（1秒后）:\n", ic_by_date1)
print("IC值（10秒后）:\n", ic_by_date2)
print("IC值（20秒后）:\n", ic_by_date3)
print("IC值（100秒后）:\n", ic_by_date4)

# 计算IC值的平均值和信息比率（IC_IR）
ic_mean1 = ic_by_date1.mean()
ic_ir1 = ic_mean1 / ic_by_date1.std() if ic_by_date1.std() != 0 else float('inf')
print("IC均值（3秒后）:", ic_mean1)
print("IC_IR（3秒后）:", ic_ir1)

ic_mean2 = ic_by_date2.mean()
ic_ir2 = ic_mean2 / ic_by_date2.std() if ic_by_date2.std() != 0 else float('inf')
print("IC均值（30秒后）:", ic_mean2)
print("IC_IR（30秒后）:", ic_ir2)

ic_mean3 = ic_by_date3.mean()
ic_ir3 = ic_mean3 / ic_by_date3.std() if ic_by_date3.std() != 0 else float('inf')
print("IC均值（60秒后）:", ic_mean3)
print("IC_IR（60秒后）:", ic_ir3)

ic_mean4 = ic_by_date4.mean()
ic_ir4 = ic_mean4 / ic_by_date4.std() if ic_by_date4.std() != 0 else float('inf')
print("IC均值（300秒后）:", ic_mean4)
print("IC_IR（300秒后）:", ic_ir4)