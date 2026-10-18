import pytest
from lxml import etree

from svg.charts.pie import Pie


@pytest.mark.parametrize('data', [(0, 13), (13, 0), (0, 0, 13), (13,), (0, 0.7)])
@pytest.mark.parametrize(
    'options',
    [
        {},
        {'show_shadow': False},
        {'expanded': True},
        {'expand_greatest': True, 'show_data_labels': True},
    ],
)
def test_single_nonzero_slice(data, options):
    graph = Pie(dict(fields=[str(index) for index in range(len(data))], **options))
    graph.add_data({'data': data})
    root = etree.fromstring(graph.burn().encode())
    index = next(index for index, value in enumerate(data) if value)
    wedge = root.xpath(f'//*[local-name()="path" and @class="fill{index + 1}"]')[0]

    # A full circle needs two arcs with distinct endpoints (issue #29).
    assert wedge.get('d').count('A') == 2
    copies = root.xpath('//*[local-name()="path" and not(@class)]')
    if graph.show_shadow:
        assert sum(copy.get('d') == wedge.get('d') for copy in copies) == 2
    else:
        assert not copies
    if graph.expanded or graph.expand_greatest:
        assert wedge.get('transform').startswith('translate(')
    if graph.show_data_labels:
        assert root.xpath('//*[local-name()="text" and contains(text(), "100%")]')


def test_multiple_nonzero_slices():
    graph = Pie({'fields': ['A', 'B']})
    graph.add_data({'data': [1, 13]})
    root = etree.fromstring(graph.burn().encode())
    wedges = root.xpath('//*[local-name()="path" and @class]')
    assert [wedge.get('class') for wedge in wedges] == ['fill1', 'fill2']
    assert all(wedge.get('d').count('A') == 1 for wedge in wedges)
