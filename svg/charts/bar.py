import itertools

from lxml import etree
from svg.charts.graph import Graph

__all__ = 'Bar', 'VerticalBar', 'HorizontalBar'


class Bar(Graph):
    """
    Create presentation quality SVG bar graphs easily.

    Synopsis::

        from svg.charts import bar


        fields = 'Jan Feb Mar'.split()
        data_sales_02 = [12, 45, 21]

        bc = bar.VerticalBar(fields, {'width': 300, 'height': 500})

        bc.add_data({'data': data_sales_02, 'title': 'Sales 2002'})

        print("Content-type: image/svg+xml\\r\\n\\r\\n")
        print(bc.burn())

    Description

    This object aims to allow you to easily create high quality
    `SVG <http://www.w3c.org/tr/svg>`_ bar graphs. You can either use the default
    style sheet or supply your own. Either way there are many options which
    can be configured to give you control over how the graph is generated -
    with or without a key, data elements at each point, title, subtitle etc.

    Notes

    The default stylesheet handles upto 12 data sets, if you
    use more you must create your own stylesheet and add the
    additional settings for the extra data sets. You will know
    if you go over 12 data sets as they will have no style and
    be in black.

    Examples

    See the example usage in tests/samples.py

    See also

    * svg.charts.graph
    * svg.charts.line
    * svg.charts.pie
    * svg.charts.plot
    * svg.charts.time_series
    """

    bar_gap = True
    """gap between bars"""

    stack = 'overlap'
    """
    how to stack adjacent dataset series

    overlap - overlap bars with transparent colors
    top - stack bars on top of one another
    side - stack bars side-by-side
    """

    scale_divisions = None

    stylesheet_names = Graph.stylesheet_names + ['bar.css']

    def __init__(self, fields, *args, **kargs):
        self.fields = fields
        super(Bar, self).__init__(*args, **kargs)

    # adapted from Plot
    def get_data_values(self):
        min_value, max_value, scale_division = self.data_range()
        result = tuple(
            float_range(min_value, max_value + scale_division, scale_division)
        )
        if self.scale_integers:
            result = map(int, result)
        return result

    # adapted from plot (very much like calling data_range('y'))
    def data_range(self):
        min_value = self.data_min()
        max_value = self.data_max()
        range = max_value - min_value

        data_pad = range / 20 or 10
        scale_range = (max_value + data_pad) - min_value

        scale_division = self.scale_divisions or (scale_range / 10)

        if self.scale_integers:
            scale_division = round(scale_division) or 1

        return min_value, max_value, scale_division

    def get_field_labels(self):
        return self.fields

    def get_data_labels(self):
        return list(map(str, self.get_data_values()))

    def data_max(self):
        return max(
            itertools.chain.from_iterable(map(lambda set: set['data'], self.data))
        )
        # above is same as
        # return max(map(lambda set: max(set['data']), self.data))

    def data_min(self):
        if not getattr(self, 'min_scale_value') is None:
            return self.min_scale_value
        min_value = min(
            itertools.chain.from_iterable(map(lambda set: set['data'], self.data))
        )
        min_value = min(min_value, 0)
        return min_value

    def get_bar_gap(self, field_size):
        bar_gap = 10  # default gap
        if field_size < 10:
            # adjust for narrow fields
            bar_gap = field_size / 2
        # the following zero's out the gap if bar_gap is False
        bar_gap = int(self.bar_gap) * bar_gap
        return bar_gap

    def _fill_class(self, dataset_index, field_index):
        """
        Return the CSS class for the indicated data parameters.

        dataset_index is the index into the current dataset.
        field_index is the index into the current field set.
        """
        return 'fill%s' % (dataset_index + 1)


def float_range(start=0, stop=None, step=1):
    "Much like the built-in function range, but accepts floats"
    while start < stop:
        yield float(start)
        start += step


class VerticalBar(Bar):
    top_align = top_font = 1

    def get_x_labels(self):
        return self.get_field_labels()

    def get_y_labels(self):
        return self.get_data_labels()

    def x_label_offset(self, width):
        return width / 2

    def draw_data(self):
        min_value = self.data_min()
        unit_size = self.graph_height - self.font_size * 2 * self.top_font
        unit_size /= max(self.get_data_values()) - min(self.get_data_values())

        bar_gap = self.get_bar_gap(self.get_field_width())

        bar_width = self.get_field_width() - bar_gap
        if self.stack == 'side':
            bar_width //= len(self.data)

        x_mod = (self.graph_width - bar_gap) // 2
        if self.stack == 'side':
            x_mod -= bar_width // 2

        bottom = self.graph_height

        for field_count, field in enumerate(self.fields):
            for dataset_count, dataset in enumerate(self.data):
                # cases (assume 0 = +ve):
                #   value  min  length
                #    +ve   +ve  value - min
                #    +ve   -ve  value - 0
                #    -ve   -ve  value.abs - 0
                value = dataset['data'][field_count]

                left = self.get_field_width() * field_count

                length = (abs(value) - max(min_value, 0)) * unit_size
                # top is 0 if value is negative
                top = bottom - ((max(value, 0) - min_value) * unit_size)
                if self.stack == 'side':
                    left += bar_width * dataset_count

                etree.SubElement(
                    self.graph,
                    'rect',
                    {
                        'x': str(left),
                        'y': str(top),
                        'width': str(bar_width),
                        'height': str(length),
                        'class': self._fill_class(dataset_count, field_count),
                    },
                )

                self.make_datapoint_text(left + bar_width / 2, top - 6, value)


class HorizontalBar(Bar):
    rotate_y_labels = True
    show_x_guidelines = True
    show_y_guidelines = False
    right_align = right_font = True

    def get_x_labels(self):
        return self.get_data_labels()

    def get_y_labels(self):
        return self.get_field_labels()

    def y_label_offset(self, height):
        return height / -2

    def draw_data(self):
        min_value = self.data_min()

        unit_size = self.graph_width
        unit_size -= self.font_size * 2 * self.right_font
        unit_size /= max(self.get_data_values()) - min(self.get_data_values())

        bar_gap = self.get_bar_gap(self.get_field_height())

        bar_height = self.get_field_height() - bar_gap
        if self.stack == 'side':
            bar_height //= len(self.data)

        y_mod = (bar_height // 2) + (self.font_size // 2)

        for field_count, field in enumerate(self.fields):
            for dataset_count, dataset in enumerate(self.data):
                value = dataset['data'][field_count]

                top = self.graph_height - (self.get_field_height() * (field_count + 1))
                if self.stack == 'side':
                    top += bar_height * dataset_count
                # cases (assume 0 = +ve):
                #   value  min  length          left
                #    +ve   +ve  value.abs - min minvalue.abs
                #    +ve   -ve  value.abs - 0   minvalue.abs
                #    -ve   -ve  value.abs - 0   minvalue.abs + value
                length = (abs(value) - max(min_value, 0)) * unit_size
                # left is 0 if value is negative
                left = (abs(min_value) + min(value, 0)) * unit_size

                etree.SubElement(
                    self.graph,
                    'rect',
                    {
                        'x': str(left),
                        'y': str(top),
                        'width': str(length),
                        'height': str(bar_height),
                        'class': self._fill_class(dataset_count, field_count),
                    },
                )

                self.make_datapoint_text(
                    left + length + 5, top + y_mod, value, "text-anchor: start; "
                )
