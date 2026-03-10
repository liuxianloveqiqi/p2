"""
可视化辅助模块 - 使用 Pyecharts 生成图表
"""
import json
from pyecharts.charts import Radar, HeatMap, Bar, Pie, Line
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import pandas as pd
import numpy as np


def create_radar_chart(student_name: str, knowledge_scores: dict, full_score: float = 10):
    """
    生成学生知识点掌握雷达图
    knowledge_scores: {"知识点名": 得分率(0-1)}
    """
    points = list(knowledge_scores.keys())
    values = [round(v * 100, 1) for v in knowledge_scores.values()]

    schema = [opts.RadarIndicatorItem(name=p, max_=100) for p in points]

    radar = (
        Radar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="700px", height="500px"))
        .add_schema(schema=schema)
        .add(
            series_name=student_name,
            data=[values],
            areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
            linestyle_opts=opts.LineStyleOpts(width=2),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{student_name} - 知识点掌握情况", subtitle="得分率 (%)"),
            legend_opts=opts.LegendOpts(pos_bottom="0%")
        )
    )
    return radar


def create_heatmap(data: pd.DataFrame):
    """
    生成班级知识点热力图
    data: 包含 student_name, knowledge_point, score_rate 列
    """
    pivot = data.pivot_table(
        values='score_rate', index='student_name',
        columns='knowledge_point', aggfunc='mean'
    ).fillna(0)

    students = pivot.index.tolist()
    knowledge_points = pivot.columns.tolist()

    heat_data = []
    for i, student in enumerate(students):
        for j, kp in enumerate(knowledge_points):
            heat_data.append([j, i, round(pivot.loc[student, kp] * 100, 1)])

    heatmap = (
        HeatMap(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="800px", height="500px"))
        .add_xaxis(knowledge_points)
        .add_yaxis(
            series_name="得分率(%)",
            yaxis_data=students,
            value=heat_data,
            label_opts=opts.LabelOpts(is_show=True, position="inside", formatter="{c}%"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="班级知识点掌握热力图"),
            visualmap_opts=opts.VisualMapOpts(
                min_=0, max_=100,
                range_color=["#d73027", "#fee08b", "#1a9850"],
                orient="horizontal",
                pos_bottom="0%"
            ),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=15)),
        )
    )
    return heatmap


def create_score_distribution(scores: list):
    """生成成绩分布柱状图"""
    bins = [0, 20, 40, 60, 80, 100]
    labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
    counts = [0] * 5
    for s in scores:
        rate = s * 100 if s <= 1 else s
        for i in range(len(bins) - 1):
            if bins[i] <= rate < bins[i+1] or (i == len(bins)-2 and rate == bins[i+1]):
                counts[i] += 1
                break

    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="700px", height="400px"))
        .add_xaxis(labels)
        .add_yaxis("学生人数", counts, 
                    itemstyle_opts=opts.ItemStyleOpts(color="#5470c6"),
                    label_opts=opts.LabelOpts(is_show=True, position="top"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="班级成绩分布"),
            xaxis_opts=opts.AxisOpts(name="得分率区间"),
            yaxis_opts=opts.AxisOpts(name="学生人数"),
        )
    )
    return bar


def create_error_type_pie(error_counts: dict):
    """生成错误类型饼图"""
    data_pair = [(k, v) for k, v in error_counts.items() if v > 0]

    pie = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="600px", height="400px"))
        .add(
            series_name="错误类型",
            data_pair=data_pair,
            radius=["30%", "60%"],
            label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="高频错误类型分布"),
            legend_opts=opts.LegendOpts(pos_bottom="0%", orient="horizontal")
        )
    )
    return pie


def create_knowledge_bar(knowledge_mastery: dict):
    """知识点达标率柱状图"""
    points = list(knowledge_mastery.keys())
    values = [round(v * 100, 1) for v in knowledge_mastery.values()]

    # 根据达标率设置颜色
    colors = []
    for v in values:
        if v >= 80:
            colors.append("#91cc75")
        elif v >= 60:
            colors.append("#fac858")
        else:
            colors.append("#ee6666")

    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="700px", height="400px"))
        .add_xaxis(points)
        .add_yaxis(
            "达标率(%)", values,
            label_opts=opts.LabelOpts(is_show=True, position="top", formatter="{c}%"),
            itemstyle_opts=opts.ItemStyleOpts(color=None),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="各知识点班级达标率"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=15)),
            yaxis_opts=opts.AxisOpts(name="达标率(%)", max_=100),
        )
    )
    return bar
