from svg.charts.graph import Graph
from svg.charts.pie import Pie


def test_load_resource_stylesheet_without_subs():
    sheet = Graph.load_resource_stylesheet('plot.css')
    assert sheet.cssRules


def test_pie_show_actual_values():
    graph = Pie(
        dict(fields=['Jan', 'Feb'], show_data_labels=True, show_actual_values=True)
    )
    graph.add_data({'data': [12, 45], 'title': 'Sales'})
    svg = graph.burn()
    assert 'Jan [12] 21%' in svg
    assert 'Feb [45] 79%' in svg
