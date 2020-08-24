# -*- coding:UTF-8 -*-

# pyecharts 动态散点图
from pyecharts import EffectScatter

# example1 EffectScatter
es = EffectScatter("动态散点图示例")

#带有涟漪特效动画的散点图
es.add("buy signal", [10],[10],symbol_size=20,effect_scale=3.5,effect_period=3,symbol="pin")
es.add("buy signal", [30],[30],symbol_size=30,effect_scale=5.5,effect_period=5,symbol="roundRect")
es.add("sell signal", [20],[20],symbol_size=12,effect_scale=4.5,effect_period=4,symbol="rect")
es.add("sell signal", [50],[50],symbol_size=16,effect_scale=5.5,effect_period=3,symbol="arrow")

es.show_config()
es.render(r'signal.html')