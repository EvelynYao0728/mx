# 将mydata里面所有的文件中的date列数据清空，进行从2000年1月1日开始的标记
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

def process_csv_files(data_dir: str, start_date: str = "2000-01-01"):
    """
    清空所有文件的 'date' 列，并重新标记从 start_date 开始的天数。

    Args:
        data_dir (str): 包含所有 CSV 文件的目录路径。
        start_date (str): 新日期列的起始日期（默认为 "2000-01-01"）。
    """
    data_dir = Path(data_dir).expanduser()
    if not data_dir.exists():
        print(f"目录 {data_dir} 不存在，请检查路径。")
        return

    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        print(f"目录 {data_dir} 中没有找到 CSV 文件。")
        return

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    print(f"开始处理 {len(csv_files)} 个文件，起始日期为 {start_date}...")

    for csv_file in csv_files:
        print(f"正在处理文件: {csv_file.name}")
        try:
            # 读取 CSV 文件
            df = pd.read_csv(csv_file)

            # 将列名转换为小写
            df.columns = [col.lower() for col in df.columns]

            # 确保有 'date' 列
            if "date" not in df.columns:
                print(f"文件 {csv_file.name} 中没有 'date' 列，跳过...")
                continue

            # 清空 'date' 列并重新标记
            df["date"] = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(len(df))]

            # 保存文件
            df.to_csv(csv_file, index=False)
            print(f"文件 {csv_file.name} 处理完成！")

        except Exception as e:
            print(f"处理文件 {csv_file.name} 时出错: {e}")

    print("所有文件处理完成！")

if __name__ == "__main__":
    # 指定存放 CSV 文件的文件夹路径
    data_dir = "mydata"
    process_csv_files(data_dir)