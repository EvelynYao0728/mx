# 用于将mydata里面所有的文件dump_bin成qlib喜欢的格式
import pandas as pd
from pathlib import Path
import shutil
from qlib_dump_bin import DumpDataAll

class DataManager:
    def __init__(self, csv_dir: str, qlib_export_path: str):
        self._csv_dir = Path(csv_dir).expanduser()
        self._qlib_export_path = Path(qlib_export_path).expanduser()

    def _dump_qlib_data(self, csv_file: Path):
        """
        将单个 CSV 文件转存为 Qlib 二进制数据。
        """
        try:
            print(f"Starting dump_bin for {csv_file.name}...")
            DumpDataAll(
                csv_path=csv_file,
                qlib_dir=self._qlib_export_path,
                date_field_name="date",
                exclude_fields="date,symbol",  # 根据需求调整排除字段
                symbol_field_name="symbol"    
            ).dump()
            print(f"dump_bin completed for {csv_file.name}.")
        except Exception as e:
            print(f"Error while processing {csv_file.name}: {e}")

    def run(self):
        """
        遍历 `mydata` 文件夹中的所有 CSV 文件，并进行转换。
        """
        csv_files = list(self._csv_dir.glob("*.csv"))
        if not csv_files:
            print(f"No CSV files found in the directory: {self._csv_dir}")
            return
        
        print(f"Found {len(csv_files)} CSV file(s) in {self._csv_dir}.")
        for csv_file in csv_files:
            self._dump_qlib_data(csv_file)

        
        #try:
         #   shutil.copy(
          #      self._qlib_export_path / "calendars/day.txt",
           #     self._qlib_export_path / "calendars/day_future.txt"
           # )
            #print("Calendars updated.")
    
        
        #except Exception as e:
         #   print(f"Error while updating calendars: {e}")


    def _update_instruments_file(self, symbols: list):
        """
        更新 instruments/all.txt 文件，添加所有 symbol。
        """
        instruments_file = self._qlib_export_path / "instruments/all.txt"
        start_date = "2000-01-01"
        end_date = "2072-09-07"

        try:
            print("Updating instruments/all.txt...")
            with instruments_file.open("w") as f:
                for symbol in symbols:
                    f.write(f"{symbol}\t{start_date}\t{end_date}\n")
            print("instruments/all.txt updated successfully.")
        except Exception as e:
            print(f"Error while updating instruments file: {e}")

    def run(self):
        """
        遍历 `mydata` 文件夹中的所有 CSV 文件，并进行转换。
        """
        csv_files = list(self._csv_dir.glob("*.csv"))
        if not csv_files:
            print(f"No CSV files found in the directory: {self._csv_dir}")
            return
        
        print(f"Found {len(csv_files)} CSV file(s) in {self._csv_dir}.")
        
        symbols = []  # 用于收集所有符号
        for csv_file in csv_files:
            self._dump_qlib_data(csv_file)
            
            # 从文件中提取 symbol 名称
            symbol = csv_file.stem  # 假设文件名即 symbol
            symbols.append(symbol)
        
        # 更新 instruments/all.txt 文件
        self._update_instruments_file(symbols)

if __name__ == "__main__":
    # 数据文件夹路径
    data_dir = "mydata"  
    # 指定 Qlib 数据输出目录
    qlib_output_dir = "qlib_data/cn_data_rolling"

    # 运行转换
    dm = DataManager(
        csv_dir=data_dir,
        qlib_export_path=qlib_output_dir,
    )
    dm.run()
