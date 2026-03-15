"""
可视化辅助模块 - 课堂互动分析图表
"""
from pyecharts.charts import Pie, Bar, Line, Radar, WordCloud as EchartsWordCloud
from pyecharts import options as opts
from pyecharts.globals import ThemeType


def create_talk_ratio_pie(teacher_ratio: float, student_ratio: float, by: str = "字数"):
    """师生话语比例饼图"""
    pie = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="500px", height="400px"))
        .add(
            series_name=f"话语比例（{by}）",
            data_pair=[
                ("教师", round(teacher_ratio * 100, 1)),
                ("学生", round(student_ratio * 100, 1))
            ],
            radius=["35%", "65%"],
            label_opts=opts.LabelOpts(formatter="{b}: {c}% ({d}%)"),
        )
        .set_colors(["#5470c6", "#91cc75"])
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"师生话语比例（{by}）"),
            legend_opts=opts.LegendOpts(pos_bottom="0%")
        )
    )
    return pie


def create_bloom_bar(bloom_counts: dict):
    """Bloom认知层次分布柱状图"""
    levels = ['记忆', '理解', '应用', '分析', '评价', '创造']
    values = [bloom_counts.get(l, 0) for l in levels]
    colors = ['#ee6666', '#fac858', '#91cc75', '#5470c6', '#73c0de', '#9a60b4']

    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="700px", height="400px"))
        .add_xaxis(levels)
        .add_yaxis(
            "提问数量", values,
            label_opts=opts.LabelOpts(is_show=True, position="top"),
            itemstyle_opts=opts.ItemStyleOpts(color=None),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="教师提问 Bloom 认知层次分布",
                                       subtitle="从低到高：记忆→理解→应用→分析→评价→创造"),
            xaxis_opts=opts.AxisOpts(name="认知层次"),
            yaxis_opts=opts.AxisOpts(name="提问数量"),
        )
    )
    return bar


def create_ire_bar(ire_count: int, irf_count: int, ir_count: int):
    """IRE/IRF模式分布柱状图"""
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="500px", height="400px"))
        .add_xaxis(['IRE（发起-回应-评价）', 'IRF（发起-回应-反馈）', 'IR（发起-回应）'])
        .add_yaxis(
            "次数", [ire_count, irf_count, ir_count],
            label_opts=opts.LabelOpts(is_show=True, position="top"),
        )
        .set_colors(["#5470c6"])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="课堂互动模式分布"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=15)),
            yaxis_opts=opts.AxisOpts(name="次数"),
        )
    )
    return bar


def create_comparison_line(sessions: list, metrics: dict):
    """
    历史对比折线图
    sessions: ["课次1", "课次2", ...]
    metrics: {"指标名": [值1, 值2, ...]}
    """
    line = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="800px", height="450px"))
        .add_xaxis(sessions)
    )

    for name, values in metrics.items():
        line.add_yaxis(
            series_name=name,
            y_axis=values,
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=True),
            linestyle_opts=opts.LineStyleOpts(width=2),
        )

    line.set_global_opts(
        title_opts=opts.TitleOpts(title="课堂互动指标历史趋势"),
        xaxis_opts=opts.AxisOpts(name="课次"),
        yaxis_opts=opts.AxisOpts(name="数值"),
        legend_opts=opts.LegendOpts(pos_top="8%"),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
    )
    return line


def create_interaction_radar(metrics: dict, session_name: str = ""):
    """课堂互动综合雷达图"""
    schema = [
        opts.RadarIndicatorItem(name="学生参与度", max_=100),
        opts.RadarIndicatorItem(name="提问层次", max_=100),
        opts.RadarIndicatorItem(name="互动频率", max_=100),
        opts.RadarIndicatorItem(name="反馈质量", max_=100),
        opts.RadarIndicatorItem(name="认知深度", max_=100),
    ]
    values = [
        metrics.get('student_participation', 50),
        metrics.get('question_depth', 50),
        metrics.get('interaction_frequency', 50),
        metrics.get('feedback_quality', 50),
        metrics.get('cognitive_depth', 50),
    ]

    radar = (
        Radar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="600px", height="450px"))
        .add_schema(schema=schema)
        .add(
            series_name=session_name or "课堂互动",
            data=[values],
            areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
            linestyle_opts=opts.LineStyleOpts(width=2),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="课堂互动综合评估"),
        )
    )
    return radar


def generate_wordcloud_image(word_freq: list, width=800, height=400):
    """
    生成词云图（使用 pyecharts WordCloud，支持中文，返回 pyecharts 图表对象）
    word_freq: [(word, count), ...]
    """
    if not word_freq:
        return None

    wc = (
        EchartsWordCloud(
            init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px")
        )
        .add(
            series_name="关键词",
            data_pair=word_freq,
            word_size_range=[14, 80],
            shape="circle",
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="课堂关键词词云"),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
    )
    return wc
