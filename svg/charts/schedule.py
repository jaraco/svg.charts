import re

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from lxml import etree
from more_itertools.recipes import grouper
from tempora import divide_timedelta_float, date_range, divide_timedelta

from .graph import Graph
from .util import reverse_mapping, flatten_mapping

__all__ = ('Schedule',)


class TimeScale:
    "Describes a scale factor based on time instead of a scalar"

    def __init__(self, width, range):
        self.width = width
        self.range = range

    def __mul__(self, delta):
        scale = divide_timedelta(delta, self.range)
        return scale * self.width


class Schedule(Graph):
    """
    Represents SVG plots of scalar temporal data

    Synopsis::

        from svg.charts import schedule

        # Data sets are label, start, end triples.
        data1 = [
            "Housesitting", "6/17/04", "6/19/04",
            "Summer Session", "6/15/04", "8/15/04",
        ]

        sched = schedule.Schedule(dict(
            width = 640,
            height = 480,
            graph_title = "My Schedule",
            show_graph_title = True,
            no_css = True,
            scale_x_integers = True,
            scale_y_integers = True,
            min_x_value = 0,
            min_y_value = 0,
            show_data_labels = True,
            show_x_guidelines = True,
            show_x_title = True,
            x_title = "Time",
            stagger_x_labels = True,
            stagger_y_labels = True,
            x_label_format = "%m/%d/%y",
        ))

        sched.add_data(dict(
            data = data1,
            title = 'Data',
        ))

        print(sched.burn())

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

    Note that multiple data sets within the same chart can differ in
    length, and that the data in the datasets needn't be in order;
    they will be ordered by the plot along the X-axis.

    The dates must be parseable by ParseDate, but otherwise can be
    any order of magnitude (seconds within the hour, or years)
    """

    x_label_format = '%Y-%m-%d %H:%M:%S'
    "The format string to be used to format the X axis labels"

    timescale_divisions = None
    r"""
    Use this to set the spacing between dates on the axis.  The value
    must be of the form
    "\d+ ?((year|month|week|day|hour|minute|second)s?)?"

    e.g.

        graph.timescale_divisions = '2 weeks'
        graph.timescale_divisions = '1 month'
        graph.timescale_divisions = '3600 seconds'  # easier would be '1 hour'
    """

    popup_format = '%Y-%m-%d %H:%M:%S'
    "The formatting used for the popups.  See x_label_format"

    _min_x_value = None
    scale_x_divisions = False
    scale_x_integers = False
    bar_gap = True

    stylesheet_names = Graph.stylesheet_names + ['bar.css']

    def add_data(self, data):
        """
        Add data to the plot::

            # A data set with 1 point: Lunch from 12:30 to 14:00
            d1 = [ "Lunch", "12:30", "14:00" ]

            # A data set with 2 points: "Cats" runs from 5/11/03 to 7/15/04, and
            #                           "Henry V" runs from 6/12/03 to 8/20/03
            d2 = [
                "Cats",    "5/11/03", "7/15/04",
                "Henry V", "6/12/03", "8/20/03",
            ]

            sched.add_data(dict(
                data = d1,
                title = 'Meetings',
            ))
            sched.add_data(dict(
                data = d2,
                title = 'Plays',
            ))

        Note that the data must be in time,value pairs, and that the date format
        may be any date that is parseable by dateutil.
        Also note that, in this example, we're mixing scales; the data from d1
        will probably not be discernable if both data sets are plotted on the same
        graph, since d1 is too granular.
        """
        # The ruby version does something different here, throwing out
        #  any previously added data.
        super(Schedule, self).add_data(data)

    # copied from Bar
    # TODO, refactor this into a common base class (or mix-in)
    def get_bar_gap(self, field_size):
        bar_gap = 10  # default gap
        if field_size < 10:
            # adjust for narrow fields
            bar_gap = field_size / 2
        # the following zero's out the gap if bar_gap is False
        bar_gap = int(self.bar_gap) * bar_gap
        return bar_gap

    def validate_data(self, conf):
        super(Schedule, self).validate_data(conf)
        msg = "Data supplied must be (title, from, to) tripples!"
        assert len(conf['data']) % 3 == 0, msg

    def process_data(self, conf):
        super(Schedule, self).process_data(conf)
        data = conf['data']
        triples = grouper(data, 3)

        labels, begin_dates, end_dates = zip(*triples)

        begin_dates = map(self.parse_date, begin_dates)
        end_dates = map(self.parse_date, end_dates)

        # reconstruct the triples in a new order
        reordered_triples = list(zip(begin_dates, end_dates, labels))

        # because of the reordering, this will sort by begin_date
        #  then end_date, then label.
        reordered_triples.sort()

        conf['data'] = reordered_triples

    def parse_date(self, date_string):
        return parse(date_string)

    def set_min_x_value(self, value):
        if isinstance(value, str):
            value = self.parse_date(value)
        self._min_x_value = value

    def get_min_x_value(self):
        return self._min_x_value

    min_x_value = property(get_min_x_value, set_min_x_value)

    def format(self, x, y):
        return x.strftime(self.popup_format)

    def get_x_labels(self):
        def format(x):
            return x.strftime(self.x_label_format)

        return list(map(format, self.get_x_values()))

    def y_label_offset(self, height):
        return height / -2.0

    def get_y_labels(self):
        # ruby version uses the last data supplied
        last = -1
        data = self.data[last]['data']
        begin_dates, start_dates, labels = zip(*data)
        return labels

    def draw_data(self):
        bar_gap = self.get_bar_gap(self.get_field_height())

        subbar_height = self.get_field_height() - bar_gap

        # y_mod = (subbar_height / 2) + (self.font_size / 2)
        x_min, x_max, div = self._x_range()
        x_range = x_max - x_min
        width = float(self.graph_width) - self.font_size * 2
        # time_scale
        # scale /= x_range
        scale = TimeScale(width, x_range)

        # reference implementation uses the last data supplied
        last = -1
        data = self.data[last]['data']

        for index, (x_start, x_end, label) in enumerate(data):
            count = index + 1  # index is 0-based, count is 1-based
            y = self.graph_height - (self.get_field_height() * count)
            bar_width = scale * (x_end - x_start)
            bar_start = scale * (x_start - x_min)

            etree.SubElement(
                self.graph,
                'rect',
                {
                    'x': str(bar_start),
                    'y': str(y),
                    'width': str(bar_width),
                    'height': str(subbar_height),
                    'class': 'fill%s' % (count + 1),
                },
            )

    def _x_range(self):
        # ruby version uses teh last data supplied
        last = -1
        data = self.data[last]['data']

        start_dates, end_dates, labels = zip(*data)
        all_dates = start_dates + end_dates
        max_value = max(all_dates)
        if self.min_x_value is not None:
            all_dates.append(self.min_x_value)
        min_value = min(all_dates)
        range = max_value - min_value
        right_pad = divide_timedelta_float(range, 20.0) or relativedelta(days=10)
        scale_range = (max_value + right_pad) - min_value

        # scale_division = self.scale_x_divisions or (scale_range / 10.0)
        # todo, remove timescale_x_divisions and use scale_x_divisions only
        # but as a time delta
        scale_division = divide_timedelta_float(scale_range, 10.0)

        # this doesn't make sense, because x is a timescale
        # if self.scale_x_integers:
        #  scale_division = min(round(scale_division), 1)

        return min_value, max_value, scale_division

    def get_x_values(self):
        x_min, x_max, scale_division = self._x_range()
        if self.timescale_divisions:
            pattern = re.compile(r'(\d+) ?(\w+)')
            m = pattern.match(self.timescale_divisions)
            if not m:
                raise ValueError(
                    "Invalid timescale_divisions: %s" % self.timescale_divisions
                )

            magnitude = int(m.group(1))
            units = m.group(2)

            parameter = self.lookup_relativedelta_parameter(units)

            delta = relativedelta(**{parameter: magnitude})

            scale_division = delta

        return date_range(x_min, x_max, scale_division)

    @classmethod
    def lookup_relativedelta_parameter(cls, unit_string):
        """
        >>> lrp = Schedule.lookup_relativedelta_parameter
        >>> lrp('Years')
        'years'
        >>> lrp('yr')
        'years'
        >>> lrp('s')
        'seconds'
        """
        try:
            return cls._rdp_map()[unit_string.lower()]
        except KeyError:
            raise ValueError("%s doesn't match any supported time/date unit")

    @staticmethod
    def _rdp_map():
        years = 'years', 'year', 'yrs', 'yr'
        months = 'months', 'month', 'mo'
        weeks = 'weeks', 'week', 'wks', 'wk'
        days = 'days', 'day'
        hours = 'hours', 'hour', 'hr', 'hrs', 'h'
        minutes = 'minutes', 'minute', 'min', 'mins', 'm'
        seconds = 'seconds', 'second', 'sec', 'secs', 's'
        return flatten_mapping(reverse_mapping(locals()))
