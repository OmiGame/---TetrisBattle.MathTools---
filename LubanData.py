import os
import sys
sys.path.append(os.path.abspath('Gen'))
import json
from GenCode import schema as schema

# -------------------------------------
# 1. 获取luban数据表
# -------------------------------------

def loader(f):
    return json.load(open('GenData/' + f + ".json", 'r', encoding="utf-8"))

tables = schema.cfg_Tables(loader)

class 全局参数:
    # 游戏基本参数
    角色等级上限 = tables.Tb游戏基本参数.getDataList()[0].角色等级上限
    每个方块的小方块数 = tables.Tb游戏基本参数.getDataList()[0].每个方块的小方块数
    小方块经验值 = tables.Tb游戏基本参数.getDataList()[0].小方块经验值
    最大上阵角色数 = tables.Tb游戏基本参数.getDataList()[0].最大上阵角色数
    角色品质划分 = tables.Tb游戏基本参数.getDataList()[0].角色品质划分
    战场总长度 = tables.Tb游戏基本参数.getDataList()[0].战场总长度
    一般默认移动速度 = tables.Tb游戏基本参数.getDataList()[0].一般默认移动速度
    关卡时长 = tables.Tb游戏基本参数.getDataList()[0].关卡时长
    肉鸽技能选择次数 = tables.Tb游戏基本参数.getDataList()[0].肉鸽技能选择次数
    怪物波次间隔 = tables.Tb游戏基本参数.getDataList()[0].怪物波次间隔
    坦克生存时间 = tables.Tb游戏基本参数.getDataList()[0].坦克生存时间
    近战生存时间 = tables.Tb游戏基本参数.getDataList()[0].近战生存时间
    远程生存时间 = tables.Tb游戏基本参数.getDataList()[0].远程生存时间
    刺客生存时间 = tables.Tb游戏基本参数.getDataList()[0].刺客生存时间
    平均生存时间 = tables.Tb游戏基本参数.getDataList()[0].平均生存时间
    属性换算比例 = tables.Tb游戏基本参数.getDataList()[0].属性换算比例
    血量战力价值 = tables.Tb游戏基本参数.getDataList()[0].血量战力价值
    DPS战力价值 = tables.Tb游戏基本参数.getDataList()[0].DPS战力价值

    # 玩家操作评估
    平均一个方块下几秒 = tables.Tb玩家操作评估.getDataList()[0].平均一个方块下几秒
    平均一秒下几个方块 = tables.Tb玩家操作评估.getDataList()[0].平均一秒下几个方块
    每行能放几个小方块 = tables.Tb玩家操作评估.getDataList()[0].每行能放几个小方块
    玩家1分钟下方块数 = tables.Tb玩家操作评估.getDataList()[0].玩家1分钟下方块数
    玩家10分钟下方块数 = tables.Tb玩家操作评估.getDataList()[0].玩家10分钟下方块数
    消除效率 = tables.Tb玩家操作评估.getDataList()[0].消除效率
    玩家10分钟消除方块数 = tables.Tb玩家操作评估.getDataList()[0].玩家10分钟消除方块数
    玩家1分钟获得经验值 = tables.Tb玩家操作评估.getDataList()[0].玩家1分钟获得经验值
    玩家10分钟获得经验值 = tables.Tb玩家操作评估.getDataList()[0].玩家10分钟获得经验值
    平均每个方块小兵数 = tables.Tb玩家操作评估.getDataList()[0].平均每个方块小兵数
    玩家每秒下几个兵 = tables.Tb玩家操作评估.getDataList()[0].玩家每秒下几个兵
    玩家每秒消除几行 = tables.Tb玩家操作评估.getDataList()[0].玩家每秒消除几行
    玩家每秒获取经验速度 = tables.Tb玩家操作评估.getDataList()[0].玩家每秒获取经验速度
    玩家每分获取经验速度 = tables.Tb玩家操作评估.getDataList()[0].玩家每分获取经验速度
    玩家10分钟消除总行数 = tables.Tb玩家操作评估.getDataList()[0].玩家10分钟消除总行数

    # 攻击范围收益倍率
    攻击范围1格 = tables.Tb攻击范围收益倍率表.getDataList()[0].攻击范围1格
    攻击范围2格 = tables.Tb攻击范围收益倍率表.getDataList()[0].攻击范围2格
    攻击范围3格 = tables.Tb攻击范围收益倍率表.getDataList()[0].攻击范围3格
    攻击范围4格 = tables.Tb攻击范围收益倍率表.getDataList()[0].攻击范围4格
    攻击范围5格 = tables.Tb攻击范围收益倍率表.getDataList()[0].攻击范围5格

    # 肉鸽技能相关
    肉鸽技能总字典 = tables.Tb肉鸽技能数据表.getDataMap()
    所有肉鸽技能名称列表 = list(肉鸽技能总字典.keys())
    肉鸽技能总数 = len(所有肉鸽技能名称列表)


    # 消除倍率表
    class 消除倍率:
        class 熟练度:
            新手 = tables.Tb消除倍率表.get("熟练度").消除参数.get("新手").参数值
            熟练 = tables.Tb消除倍率表.get("熟练度").消除参数.get("熟练").参数值
            高手 = tables.Tb消除倍率表.get("熟练度").消除参数.get("高手").参数值

        class I型方块下落概率:
            基础值 = tables.Tb消除倍率表.get("I型方块下落概率").消除参数.get("基础值").参数值
            失败buff加成 = tables.Tb消除倍率表.get("I型方块下落概率").消除参数.get("失败buff加成").参数值
            保底机制 = tables.Tb消除倍率表.get("I型方块下落概率").消除参数.get("保底机制").参数值
            肉鸽技能 = tables.Tb消除倍率表.get("I型方块下落概率").消除参数.get("肉鸽技能").参数值

        class 自动消除效率:
            自动消除10000 = tables.Tb消除倍率表.get("自动消除效率").消除参数.get("自动消除10000").参数值
            自动消除8 = tables.Tb消除倍率表.get("自动消除效率").消除参数.get("自动消除8").参数值
            自动消除7 = tables.Tb消除倍率表.get("自动消除效率").消除参数.get("自动消除7").参数值
            自动消除6 = tables.Tb消除倍率表.get("自动消除效率").消除参数.get("自动消除6").参数值

        class 可操作行:
            可操作行20 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行20").参数值
            可操作行19 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行19").参数值
            可操作行18 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行18").参数值
            可操作行17 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行17").参数值
            可操作行16 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行16").参数值
            可操作行15 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行15").参数值
            可操作行14 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行14").参数值
            可操作行13 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行13").参数值
            可操作行12 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行12").参数值
            可操作行11 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行11").参数值
            可操作行10 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行10").参数值
            可操作行9 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行9").参数值
            可操作行8 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行8").参数值
            可操作行7 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行7").参数值
            可操作行6 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行6").参数值
            可操作行5 = tables.Tb消除倍率表.get("可操作行").消除参数.get("可操作行5").参数值

        class 可操作列:
            可操作列10 = tables.Tb消除倍率表.get("可操作列").消除参数.get("可操作列10").参数值
            可操作列9 = tables.Tb消除倍率表.get("可操作列").消除参数.get("可操作列9").参数值
            可操作列8 = tables.Tb消除倍率表.get("可操作列").消除参数.get("可操作列8").参数值
            可操作列7 = tables.Tb消除倍率表.get("可操作列").消除参数.get("可操作列7").参数值
            可操作列6 = tables.Tb消除倍率表.get("可操作列").消除参数.get("可操作列6").参数值
            可操作列5 = tables.Tb消除倍率表.get("可操作列").消除参数.get("可操作列5").参数值
            可操作列4 = tables.Tb消除倍率表.get("可操作列").消除参数.get("可操作列4").参数值
            可操作列3 = tables.Tb消除倍率表.get("可操作列").消除参数.get("可操作列3").参数值
            可操作列2 = tables.Tb消除倍率表.get("可操作列").消除参数.get("可操作列2").参数值
            可操作列1 = tables.Tb消除倍率表.get("可操作列").消除参数.get("可操作列1").参数值

        class 方块下落速度:
            方块下落速度0_7 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.7").参数值
            方块下落速度0_8 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.8").参数值
            方块下落速度0_9 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.9").参数值
            方块下落速度0_10 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.10").参数值
            方块下落速度0_11 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.11").参数值
            方块下落速度0_12 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.12").参数值
            方块下落速度0_13 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.13").参数值
            方块下落速度0_14 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.14").参数值
            方块下落速度0_15 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.15").参数值
            方块下落速度0_16 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.16").参数值
            方块下落速度0_17 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.17").参数值
            方块下落速度0_18 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.18").参数值
            方块下落速度0_19 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.19").参数值
            方块下落速度0_20 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.20").参数值
            方块下落速度0_21 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.21").参数值
            方块下落速度0_22 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.22").参数值
            方块下落速度0_23 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.23").参数值
            方块下落速度0_24 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.24").参数值
            方块下落速度0_25 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.25").参数值
            方块下落速度0_26 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.26").参数值
            方块下落速度0_27 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.27").参数值
            方块下落速度0_28 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.28").参数值
            方块下落速度0_29 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.29").参数值
            方块下落速度0_30 = tables.Tb消除倍率表.get("方块下落速度").消除参数.get("方块下落速度0.30").参数值

        class 基本方块类型:
            基本类型 = tables.Tb消除倍率表.get("基本方块类型").消除参数.get("基本类型").参数值
            加小方块 = tables.Tb消除倍率表.get("基本方块类型").消除参数.get("加小方块").参数值
            加1个5格方块 = tables.Tb消除倍率表.get("基本方块类型").消除参数.get("加1个5格方块").参数值
            无I型方块 = tables.Tb消除倍率表.get("基本方块类型").消除参数.get("无I型方块").参数值

        class 方块层数:
            方块层数1 = tables.Tb消除倍率表.get("方块层数").消除参数.get("方块层数1").参数值
            方块层数2 = tables.Tb消除倍率表.get("方块层数").消除参数.get("方块层数2").参数值
            方块层数3 = tables.Tb消除倍率表.get("方块层数").消除参数.get("方块层数3").参数值

        class 方块障碍机制:
            无 = tables.Tb消除倍率表.get("方块障碍机制").消除参数.get("无").参数值
            方块不能旋转 = tables.Tb消除倍率表.get("方块障碍机制").消除参数.get("方块不能旋转").参数值

        class 方块上的小兵数:
            方块上的小兵数1 = tables.Tb消除倍率表.get("方块上的小兵数").消除参数.get("方块上的小兵数1").参数值
            方块上的小兵数2 = tables.Tb消除倍率表.get("方块上的小兵数").消除参数.get("方块上的小兵数2").参数值
            方块上的小兵数3 = tables.Tb消除倍率表.get("方块上的小兵数").消除参数.get("方块上的小兵数3").参数值
            方块上的小兵数4 = tables.Tb消除倍率表.get("方块上的小兵数").消除参数.get("方块上的小兵数4").参数值




# 引用案例
# 因为luban的python版本没有做定义索引器 []，所以不能像C#中通过  tables.Tb角色初始属性表[key]，只能通过 tables.Tb角色初始属性表.get(key) 进行访问
# 正常一行多列表的引用
# print(查找角色初始属性字典("士兵"))#获得角色名
# print(tables.Tb角色初始属性表.getDataList())  #返回所有list的内存地址
# print(tables.Tb角色初始属性表.getDataList()[0])  #返回list[0]的内存地址，也就是第一行数据的地址
# print(tables.Tb角色初始属性表.getDataList()[0].__dict__)  #返回第一行数据地址下保存的字典数据
# print(tables.Tb角色初始属性表.get("士兵"))   #获得key所在的内存地址
# print(tables.Tb角色初始属性表.get("士兵").__dict__)   #获得key的地址所保存的数据
# print(tables.Tb角色初始属性表.get("弓箭手").期望生命周期)  #获得期望生命周期 属性
# print(tables.Tb角色初始属性表.get("士兵").角色名称)  #属性可正常访问
#
# #多行多列表，需要先获得最外层字典名，再根据内层字典查找数据。具体把键当成横坐标，属性当纵坐标，以此来定位数据
# print(tables.Tb角色技能数据表.get("士兵").各等级技能倍率.get(5).血量特效倍率)
# print(tables.Tb消除倍率表.get("可操作列").消除参数.get(f"可操作列9").参数值)

#
# #纵表的引用方式本质上和横表一样，但因为没有key值所以无法直接引用，可以直接用getdatalist(0)获取所有数据，然后直接根据属性来访问
# print(tables.Tb游戏基本参数.getDataList()[0].小方块经验值)