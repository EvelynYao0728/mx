from alphagen.data.expression import Feature, Ref
from alphagen_qlib.stock_data import FeatureType

# 定义基础特征
high = Feature(FeatureType.HIGH)
low = Feature(FeatureType.LOW)
volume = Feature(FeatureType.VOLUME)
open_ = Feature(FeatureType.OPEN)
close = Feature(FeatureType.CLOSE)
turnover = Feature(FeatureType.TURNOVER)
oi = Feature(FeatureType.OI)
upper_limit = Feature(FeatureType.UPPERLIMIT)
lower_limit = Feature(FeatureType.LOWERLIMIT)


# Open-related features
openbp1 = Feature(FeatureType.OPENBP1)
openbv1 = Feature(FeatureType.OPENBV1)
openap1 = Feature(FeatureType.OPENAP1)
openav1 = Feature(FeatureType.OPENAV1)

openbp2 = Feature(FeatureType.OPENBP2)
openbv2 = Feature(FeatureType.OPENBV2)
openap2 = Feature(FeatureType.OPENAP2)
openav2 = Feature(FeatureType.OPENAV2)

openbp3 = Feature(FeatureType.OPENBP3)
openbv3 = Feature(FeatureType.OPENBV3)
openap3 = Feature(FeatureType.OPENAP3)
openav3 = Feature(FeatureType.OPENAV3)

openbp4 = Feature(FeatureType.OPENBP4)
openbv4 = Feature(FeatureType.OPENBV4)
openap4 = Feature(FeatureType.OPENAP4)
openav4 = Feature(FeatureType.OPENAV4)

openbp5 = Feature(FeatureType.OPENBP5)
openbv5 = Feature(FeatureType.OPENBV5)
openap5 = Feature(FeatureType.OPENAP5)
openav5 = Feature(FeatureType.OPENAV5)

# Close-related features
closebp1 = Feature(FeatureType.CLOSEBP1)
closebv1 = Feature(FeatureType.CLOSEBV1)
closeap1 = Feature(FeatureType.CLOSEAP1)
closeav1 = Feature(FeatureType.CLOSEAV1)

closebp2 = Feature(FeatureType.CLOSEBP2)
closebv2 = Feature(FeatureType.CLOSEBV2)
closeap2 = Feature(FeatureType.CLOSEAP2)
closeav2 = Feature(FeatureType.CLOSEAV2)

closebp3 = Feature(FeatureType.CLOSEBP3)
closebv3 = Feature(FeatureType.CLOSEBV3)
closeap3 = Feature(FeatureType.CLOSEAP3)
closeav3 = Feature(FeatureType.CLOSEAV3)

closebp4 = Feature(FeatureType.CLOSEBP4)
closebv4 = Feature(FeatureType.CLOSEBV4)
closeap4 = Feature(FeatureType.CLOSEAP4)
closeav4 = Feature(FeatureType.CLOSEAV4)

closebp5 = Feature(FeatureType.CLOSEBP5)
closebv5 = Feature(FeatureType.CLOSEBV5)
closeap5 = Feature(FeatureType.CLOSEAP5)
closeav5 = Feature(FeatureType.CLOSEAV5)


# 使用 VWAP 示例特征
# 如果需要支持 VWAP，可以定义类似的 FeatureType，例如：
# vwap = Feature(FeatureType.VWAP)

# 定义目标计算逻辑
# 当前的目标：过去 20 天的 Close 相对于当前 Close 的变化率
target = Ref(close, -20) / close - 1
#target = 1- Ref(close, -20) / close 
#target = -closeav1*closeap1+closebv1*closebp1
#-df["Closebv1"]*df["Closebp1"] + df["Closeav1"]*df["Closeap1"]

# 替代目标：使用 vwap 计算变化率（如果 VWAP 被支持）
# target = Ref(vwap, -21) / Ref(vwap, -1) - 1
