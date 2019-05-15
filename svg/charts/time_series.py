import re
from time import mktime
import datetime

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

import svg.charts.plot
from .util import float_range


fromtimestamp = datetime.datetime.fromtimestamp


class Plot(svg.charts.plot.Plot):
    """
    For creating SVG plots of scalar temporal data

    Synopsis::

        from svg.charts import time_series

        # Data sets are x,y pairs
        data1 = ["6/17/72", 11,  "1/11/72", 7,  "4/13/04 17:31", 11,
            "9/11/01", 9,  "9/1/85", 2,  "9/1/88", 1,  "1/15/95", 13]
        data2 = ["8/1/73", 18,  "3/1/77", 15,  "10/1/98", 4,  "5/1/02", 14,
            "3/1/95", 6,  "8/1/91", 12,  "12/1/87", 6,  "5/1/84", 17,
            "10/1/80", 12]

        ts = time_series.Plot(dict(
            width = 640,
            height = 480,
            graph_title = "TS Title",
            show_graph_title = True,
            no_css = True,
            key = True,
            scale_x_integers = True,
            scale_y_integers = True,
            min_x_value = 0,
            min_y_value = 0,
            show_data_labels = True,
            show_x_guidelines = True,
            show_x_title = True,
            x_title = "Time",
            show_y_title = True,
            y_title = "Ice Cream Cones",
            y_title_text_direction = 'bt',
            stagger_x_labels = True,
            x_label_format = "%m/%d/%y",
        ))

        ts.add_data(dict(
            data = projection,
            title = 'Projected',
        ))

        ts.add_data(dict(
            data = actual,
            title = 'Actual',
        ))

        print(ts.burn())

    Description

    Produces a graph of temporal scalar data.

    Examples

    See tests/samples.py for an example.

    Notes

    The default stylesheet handles upto 10 data sets, if you
    use more you must create your own stylesheet and add the
    additional settings for the extra data sets. You will know
    if you go over 10 data sets as they will have no style and
    be in black.

    Unlike the other types of charts, data sets must contain x,y pairs::

        # A data set with 1 point: ("12:30", 2)
        ["12:30", 2]
        # A data set with 2 points: ("01:00", 2) and
        #                           ("14:20", 6)
        ["01:00", 2, "14:20", 6]

    Note that multiple data sets within the same chart can differ in length,
    and that the data in the datasets needn't be in order; they will be ordered
    by the plot along the X-axis.

    The dates must be parseable by ParseDate, but otherwise can be
    any order of magnitude (seconds within the hour, or years)
    """

    popup_format = x_label_format = '%Y-%m-%d %H:%M:%S'
    "The formatting usped for the popups.  See x_label_format"
    __doc_x_label_format_ = (
        "The format string used to format the X axis labels.  See strftime."
    )

    timescale_divisions = None
    r"""
    Use this to set the spacing between dates on the axis.  The value
    must be of the form
    "\d+ ?(days|weeks|months|years|hours|minutes|seconds)?"

    For example:

    ts.timescale_divisions = "2 weeks"

    will cause the chart to try to divide the X axis up into segments of
    two week periods.
    """

    def add_data(self, data):
        """
        Add data to the plot::

            # A data set with 1 point: ("12:30", 2)
            d1 = ["12:30", 2]

            # A data set with 2 points: ("01:00", 2) and
            #                           ("14:20", 6)
            d2 = ["01:00", 2, "14:20", 6]

            graph.add_data(
                data = d1,
                title = 'One',
            )
            graph.add_data(
                data = d2,
                title = 'Two',
            )

        Note that the data must be in (time, value) pairs, and
        the date format
        may be any date that is parseable by dateutil.
        """
        super(Plot, self).add_data(data)

    def process_data(self, data):
        super(Plot, self).process_data(data)
        # the date should be in the first axis;
        # replace value with parsed date.
        series = data['data']
        data['data'] = [(self.parse_date(p[0]),) + tuple(p[1:]) for p in series]

    _min_x_value = svg.charts.plot.Plot.min_x_value

    def get_min_x_value(self):
        return self._min_x_value

    def set_min_x_value(self, date):
        self._min_x_value = self.parse_date(date)

    min_x_value = property(get_min_x_value, set_min_x_value)

    def format(self, x, y):
        return fromtimestamp(x).strftime(self.popup_format)

    def get_x_labels(self):
        return list(
            map(
                lambda t: fromtimestamp(t).strftime(self.x_label_format),
                self.get_x_values(),
            )
        )

    def get_x_values(self):
        result = self.get_x_timescale_division_values()
        if result:
            return result
        return tuple(float_range(*self.x_range()))

    def get_x_timescale_division_values(self):
        if not self.timescale_divisions:
            return
        min, max, scale_division = self.x_range()
        m = re.match(
            r'(?P<amount>\d+) '
            '?(?P<division_units>days|weeks|months|years|hours|minutes|seconds)?',
            self.timescale_divisions,
        )
        # copy amount and division_units into the local namespace
        division_units = m.groupdict()['division_units'] or 'days'
        amount = int(m.groupdict()['amount'])
        if not amount:
            return
        delta = relativedelta(**{division_units: amount})
        result = tuple(self.get_time_range(min, max, delta))
        return result

    def get_time_range(self, start, stop, delta):
        start, stop = map(fromtimestamp, (start, stop))
        current = start
        while current <= stop:
            yield mktime(current.timetuple())
            current += delta

    def parse_date(self, date_string):
        return mktime(parse(date_string).timetuple())
