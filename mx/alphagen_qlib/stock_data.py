from typing import List, Union, Optional, Tuple, Dict
from enum import IntEnum
import numpy as np
import pandas as pd
import torch


class FeatureType(IntEnum):
    # 基础列
    OPEN = 0
    CLOSE = 1
    HIGH = 2
    LOW = 3
    VOLUME = 4
    TURNOVER = 5
    OI = 6
    
    # Open 的价格和量相关
    OPENBP1 = 7
    OPENBV1 = 8
    OPENAP1 = 9
    OPENAV1 = 10
    OPENBP2 = 11
    OPENBV2 = 12
    OPENAP2 = 13
    OPENAV2 = 14
    OPENBP3 = 15
    OPENBV3 = 16
    OPENAP3 = 17
    OPENAV3 = 18
    OPENBP4 = 19
    OPENBV4 = 20
    OPENAP4 = 21
    OPENAV4 = 22
    OPENBP5 = 23
    OPENBV5 = 24
    OPENAP5 = 25
    OPENAV5 = 26

    # Close 的价格和量相关
    CLOSEBP1 = 27
    CLOSEBV1 = 28
    CLOSEAP1 = 29
    CLOSEAV1 = 30
    CLOSEBP2 = 31
    CLOSEBV2 = 32
    CLOSEAP2 = 33
    CLOSEAV2 = 34
    CLOSEBP3 = 35
    CLOSEBV3 = 36
    CLOSEAP3 = 37
    CLOSEAV3 = 38
    CLOSEBP4 = 39
    CLOSEBV4 = 40
    CLOSEAP4 = 41
    CLOSEAV4 = 42
    CLOSEBP5 = 43
    CLOSEBV5 = 44
    CLOSEAP5 = 45
    CLOSEAV5 = 46

    # 限价
    UPPERLIMIT = 47
    LOWERLIMIT = 48
def change_to_raw_min(features):
    """
    将特征转换为原始特征的最小单位，例如对体积进行单位缩放或进行简单转换。
    """
    result = []
    for feature in features:
        if feature in ['$vwap']:
            # vwap 使用 money 和 volume 的比值计算
            result.append("$money/$volume")
        elif feature in ['$volume', '$turnover', '$oi']:
            # 对 volume、turnover 和 oi 进行缩放
            result.append(f"{feature}/100000")
        elif feature in [
            '$open', '$close', '$high', '$low', 
            '$upperlimit', '$lowerlimit'
        ]:
            # 保留基础价格类特征
            result.append(feature)
        elif feature.startswith('$openbp') or feature.startswith('$closebp') or \
             feature.startswith('$openap') or feature.startswith('$closeap'):
            # 保留价格相关的分档数据
            result.append(feature)
        elif feature.startswith('$openbv') or feature.startswith('$closebv') or \
             feature.startswith('$openav') or feature.startswith('$closeav'):
            # 对量相关的分档数据进行单位缩放
            result.append(f"{feature}/100000")
        else:
            # 未知特征直接保留
            result.append(feature)
    print(result)
    return result


def change_to_raw(features):
    """
    将特征转换为原始特征，并根据因子调整价格类特征或缩放体积类特征。
    """
    result = []
    for feature in features:
        if feature in ['$open', '$close', '$high', '$low', '$vwap']:
            # 对价格类特征进行因子调整
            result.append(f"{feature}*$factor")
        elif feature in ['$volume', '$turnover', '$oi']:
            # 对 volume、turnover 和 oi 进行因子调整和单位缩放
            result.append(f"{feature}/$factor/1000000")
        elif feature in ['$upperlimit', '$lowerlimit']:
            # 对限价类特征进行因子调整
            result.append(f"{feature}*$factor")
        elif feature.startswith('$openbp') or feature.startswith('$closebp') or \
             feature.startswith('$openap') or feature.startswith('$closeap'):
            # 对分档价格类特征进行因子调整
            result.append(f"{feature}*$factor")
        elif feature.startswith('$openbv') or feature.startswith('$closebv') or \
             feature.startswith('$openav') or feature.startswith('$closeav'):
            # 对分档量类特征进行因子调整和单位缩放
            result.append(f"{feature}/$factor/1000000")
        else:
            # 遇到未支持的特征，抛出错误
            raise ValueError(f"Feature {feature} not supported")
    print(result)
    return result

class StockData:
    _qlib_initialized: bool = False

    def __init__(self,
                 instrument: Union[str, List[str]],
                 start_time: str,
                 end_time: str,
                 max_backtrack_days: int = 100,
                 max_future_days: int = 30,
                 features: Optional[List[FeatureType]] = None,
                 device: torch.device = torch.device('cuda:0'),
                 raw:bool = False,
                 qlib_path:Union[str,Dict] = "",
                 freq:str = 'day',
                 ) -> None:
        self._init_qlib(qlib_path)
        self.df_bak = None
        self.raw = raw
        self._instrument = instrument
        self.max_backtrack_days = max_backtrack_days
        self.max_future_days = max_future_days
        self._start_time = start_time
        self._end_time = end_time
        self._features = features if features is not None else list(FeatureType)
        self.device = device
        self.freq = freq
        self.data, self._dates, self._stock_ids = self._get_data()


    @classmethod
    def _init_qlib(cls,qlib_path) -> None:
        if cls._qlib_initialized:
            return
        import qlib
        from qlib.config import REG_CN
        qlib.init(provider_uri=qlib_path, region=REG_CN)
        cls._qlib_initialized = True

    def _load_exprs(self, exprs: Union[str, List[str]]) -> pd.DataFrame:
        # This evaluates an expression on the data and returns the dataframe
        # It might throw on illegal expressions like "Ref(constant, dtime)"
        from qlib.data.dataset.loader import QlibDataLoader
        from qlib.data import D
        if not isinstance(exprs, list):
            exprs = [exprs]
        cal: np.ndarray = D.calendar(freq=self.freq)
        start_index = cal.searchsorted(pd.Timestamp(self._start_time))  # type: ignore
        end_index = cal.searchsorted(pd.Timestamp(self._end_time))  # type: ignore
        real_start_time = cal[start_index - self.max_backtrack_days]
        if cal[end_index] != pd.Timestamp(self._end_time):
            end_index -= 1
        # real_end_time = cal[min(end_index + self.max_future_days,len(cal)-1)]
        real_end_time = cal[end_index + self.max_future_days]
        result =  (QlibDataLoader(config=exprs,freq=self.freq)  # type: ignore
                .load(self._instrument, real_start_time, real_end_time))
        return result
    
    def _get_data(self) -> Tuple[torch.Tensor, pd.Index, pd.Index]:
        features = ['$' + f.name.lower() for f in self._features]
        if self.raw and self.freq == 'day':
            features = change_to_raw(features)
        elif self.raw:
            features = change_to_raw_min(features)
        df = self._load_exprs(features)
        self.df_bak = df
        # import pdb; pdb.set_trace()
        
        
        print(f"df is {df}")
        df = df.stack().unstack(level=1)
        dates = df.index.levels[0]                                      # type: ignore
        stock_ids = df.columns
        values = df.values
        values = values.reshape((-1, len(features), values.shape[-1]))  # type: ignore
        return torch.tensor(values, dtype=torch.float, device=self.device), dates, stock_ids

    @property
    def n_features(self) -> int:
        return len(self._features)

    @property
    def n_stocks(self) -> int:
        return self.data.shape[-1]

    @property
    def n_days(self) -> int:
        return self.data.shape[0] - self.max_backtrack_days - self.max_future_days

    def add_data(self,data:torch.Tensor,dates:pd.Index):
        data = data.to(self.device)
        self.data = torch.cat([self.data,data],dim=0)
        self._dates = pd.Index(self._dates.append(dates))


    def make_dataframe(
        self,
        data: Union[torch.Tensor, List[torch.Tensor]],
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
            Parameters:
            - `data`: a tensor of size `(n_days, n_stocks[, n_columns])`, or
            a list of tensors of size `(n_days, n_stocks)`
            - `columns`: an optional list of column names
            """
        if isinstance(data, list):
            data = torch.stack(data, dim=2)
        if len(data.shape) == 2:
            data = data.unsqueeze(2)
        if columns is None:
            columns = [str(i) for i in range(data.shape[2])]
        n_days, n_stocks, n_columns = data.shape
        if self.n_days != n_days:
            raise ValueError(f"number of days in the provided tensor ({n_days}) doesn't "
                             f"match that of the current StockData ({self.n_days})")
        if self.n_stocks != n_stocks:
            raise ValueError(f"number of stocks in the provided tensor ({n_stocks}) doesn't "
                             f"match that of the current StockData ({self.n_stocks})")
        if len(columns) != n_columns:
            raise ValueError(f"size of columns ({len(columns)}) doesn't match with "
                             f"tensor feature count ({data.shape[2]})")
        if self.max_future_days == 0:
            date_index = self._dates[self.max_backtrack_days:]
        else:
            date_index = self._dates[self.max_backtrack_days:-self.max_future_days]
        index = pd.MultiIndex.from_product([date_index, self._stock_ids])
        data = data.reshape(-1, n_columns)
        return pd.DataFrame(data.detach().cpu().numpy(), index=index, columns=columns)
    
    