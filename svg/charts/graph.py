"""
svg.charts.graph

The base module for `svg.charts` classes.
"""

import collections.abc
import functools
import importlib.resources
import itertools
from operator import itemgetter

import cssutils
from lxml import etree

# cause the SVG profile to be loaded
__import__('svg.charts.css')


class Graph:
    """
    Base object for generating SVG Graphs

    Synopsis

        This class is only used as a superclass of specialized charts.  Do not
        attempt to use this class directly, unless creating a new chart type.

        For examples of how to subclass this class, see the existing specific
        subclasses, such as svn.charts.Pie.

    * svg.charts.bar
    * svg.charts.line
    * svg.charts.pie
    * svg.charts.plot
    * svg.charts.time_series

    """

    width = 500
    height = 300
    show_x_guidelines = False
    show_y_guidelines = True
    show_data_values = True
    min_scale_value = None
    show_x_labels = True
    stagger_x_labels = False
    rotate_x_labels = False
    step_x_labels = 1
    step_include_first_x_label = True
    show_y_labels = True
    rotate_y_labels = False
    stagger_y_labels = False
    step_include_first_y_label = True
    step_y_labels = 1
    scale_integers = False
    show_x_title = False
    x_title = 'X Field names'
    show_y_title = False
    # 'bt' for bottom to top; 'tb' for top to bottom
    y_title_text_direction = 'bt'
    y_title = 'Y Scale'
    show_graph_title = False
    graph_title = 'Graph Title'
    show_graph_subtitle = False
    graph_subtitle = 'Graph Subtitle'
    key = True
    key_position = 'right'  # 'bottom' or 'right',

    font_size = 12
    title_font_size = 16
    subtitle_font_size = 14
    x_label_font_size = 12
    x_title_font_size = 14
    y_label_font_size = 12
    y_title_font_size = 14
    key_font_size = 10

    css_inline = False

    top_align = top_font = right_align = right_font = 0

    stylesheet_names = ['graph.css']

    def __init__(self, config=None):
        """Initialize the graph object with the graph settings."""
        if config is None:
            config = {}
        if self.__class__ is Graph:
            raise NotImplementedError("Graph is an abstract base class")
        self.load_config(config)
        self.clear_data()
        self.style = {}

    def load_config(self, config):
        self.__dict__.update(config)

    def add_data(self, conf):
        """
        Add data to the graph object. May be called several times to add
        additional data sets.

        conf should be a dictionary including 'data' and 'title' keys
        """
        self.validate_data(conf)
        self.process_data(conf)
        self.data.append(conf)

    def validate_data(self, conf):
        data = conf.get('data')
        if isinstance(data, collections.abc.Sequence):
            return

        if data is None:
            raise TypeError("conf must be a dictionary with 'data'")

        if not hasattr(data, '__iter__'):
            raise TypeError("conf[data] must be iterable")

        # materialize an iterable data
        conf['data'] = tuple(data)

    def process_data(self, data):
        pass

    def clear_data(self):
        """
        This method removes all data from the object to create a new graph
        with the same config options.
        """
        self.data = []

    def burn(self):
        """
        Process the template with the data and
        config which has been set and return the resulting SVG.

        Raises ValueError when no data set has
        been added to the graph object.
        """
        if not self.data:
            raise ValueError("No data available")

        if hasattr(self, 'calculations'):
            self.calculations()

        self.start_svg()
        self.calculate_graph_dimensions()
        self.foreground = etree.Element("g")
        self.draw_graph()
        self.draw_titles()
        self.draw_legend()
        self.draw_data()
        self.graph.append(self.foreground)
        self.render_inline_styles()

        return self.render(self.root)

    @staticmethod
    def render(tree):
        return etree.tostring(tree, encoding='unicode')

    KEY_BOX_SIZE = 12

    def calculate_left_margin(self):
        """
        Calculates the margin to the left of the plot area, setting
        border_left.
        """
        bl = 7
        # Check for Y labels
        if self.rotate_y_labels:
            max_y_label_height_px = self.y_label_font_size
        else:
            label_lengths = map(len, self.get_y_labels())
            max_y_label_len = max(label_lengths)
            max_y_label_height_px = 0.6 * max_y_label_len * self.y_label_font_size
        if self.show_y_labels:
            bl += max_y_label_height_px
        if self.stagger_y_labels:
            bl += max_y_label_height_px + 10
        if self.show_y_title:
            bl += self.y_title_font_size + 5
        self.border_left = bl

    def max_y_label_width_px(self):
        """
        Calculate the width of the widest Y label.  This will be the
        character height if the Y labels are rotated.
        """
        if self.rotate_y_labels:
            return self.font_size

    def calculate_right_margin(self):
        """
        Calculate the margin in pixels to the right of the plot area,
        setting border_right.
        """
        br = 7
        if self.key and self.key_position == 'right':
            max_key_len = max(map(len, self.keys()))
            br += max_key_len * self.key_font_size * 0.6
            br += self.KEY_BOX_SIZE
            br += 10  # Some padding around the box
        self.border_right = br

    def calculate_top_margin(self):
        """
        Calculate the margin in pixels above the plot area, setting
        border_top.
        """
        self.border_top = 5
        if self.show_graph_title:
            self.border_top += self.title_font_size
        self.border_top += 5
        if self.show_graph_subtitle:
            self.border_top += self.subtitle_font_size

    @staticmethod
    def _w3c_name(name):
        """
        Generate a W3C Name from a string.
        """
        # for now, fake it by replacing known bad characters with good ones.
        name = name.replace(':', '-')
        name = name.replace(' ', '_')

    def add_popup(self, x, y, label):
        """
        Add pop-up information to a point on the graph.
        """
        txt_width = len(label) * self.font_size * 0.6 + 10
        tx = x + [5, -5][int(x + txt_width > self.width)]
        anchor = ['start', 'end'][x + txt_width > self.width]
        style = 'fill: #000; text-anchor: %s;' % anchor
        id = 'label-%s' % self._w3c_name(label)
        attrs = {
            'x': str(tx),
            'y': str(y - self.font_size),
            'visibility': 'hidden',
            'style': style,
            'text': label,
            'id': id,
        }
        etree.SubElement(self.foreground, 'text', attrs)

        # add the circle element to the foreground
        vis_tmpl = "document.getElementById('{id}').setAttribute('visibility', {val})"
        attrs = {
            'cx': str(x),
            'cy': str(y),
            'r': str(10),
            'style': 'opacity: 0;',
            'onmouseover': vis_tmpl.format(val='visible', id=id),
            'onmouseout': vis_tmpl.format(val='hidden', id=id),
        }
        etree.SubElement(self.foreground, 'circle', attrs)

    def calculate_bottom_margin(self):
        """
        Calculate the margin in pixels below the plot area, setting
        border_bottom.
        """
        bb = 7
        if self.key and self.key_position == 'bottom':
            bb += len(self.data) * (self.font_size + 5)
            bb += 10
        if self.show_x_labels:
            max_x_label_height_px = self.x_label_font_size
            if self.rotate_x_labels:
                label_lengths = map(len, self.get_x_labels())
                max_x_label_len = functools.reduce(max, label_lengths)
                max_x_label_height_px *= 0.6 * max_x_label_len
            bb += max_x_label_height_px
            if self.stagger_x_labels:
                bb += max_x_label_height_px + 10
        if self.show_x_title:
            bb += self.x_title_font_size + 5
        self.border_bottom = bb

    def draw_graph(self):
        """
        The central logic for drawing the graph.

        Sets self.graph (the 'g' element in the SVG root)
        """
        transform = f'translate ({self.border_left} {self.border_top})'
        self.graph = etree.SubElement(self.root, 'g', transform=transform)

        etree.SubElement(
            self.graph,
            'rect',
            {
                'x': '0',
                'y': '0',
                'width': str(self.graph_width),
                'height': str(self.graph_height),
                'class': 'graphBackground',
            },
        )

        # Axis
        etree.SubElement(
            self.graph,
            'path',
            {'d': 'M 0 0 v%s' % self.graph_height, 'class': 'axis', 'id': 'xAxis'},
        )
        etree.SubElement(
            self.graph,
            'path',
            {
                'd': f'M 0 {self.graph_height} h{self.graph_width}',
                'class': 'axis',
                'id': 'yAxis',
            },
        )

        self.draw_x_labels()
        self.draw_y_labels()

    def x_label_offset(self, width):
        """
        Return an offset for drawing the x label. Currently returns 0.
        """
        # consider width/2 for centering the labels
        return 0

    def make_datapoint_text(self, x, y, value, style=None):
        """
        Add text for a datapoint
        """
        if not self.show_data_values:
            # do nothing
            return
        # first lay down the text in a wide white stroke to
        #  differentiate it from the background
        e = etree.SubElement(
            self.foreground,
            'text',
            {
                'x': str(x),
                'y': str(y),
                'class': 'dataPointLabel',
                'style': '{style} stroke: #fff; stroke-width: 2;'.format(**vars()),
            },
        )
        e.text = str(value)
        # then lay down the text in the specified style
        e = etree.SubElement(
            self.foreground,
            'text',
            {'x': str(x), 'y': str(y), 'class': 'dataPointLabel'},
        )
        e.text = str(value)
        if style:
            e.set('style', style)

    def draw_x_labels(self):
        "Draw the X axis labels"
        if self.show_x_labels:
            labels = self.get_x_labels()
            count = len(labels)

            labels = enumerate(iter(labels))
            start = int(not self.step_include_first_x_label)
            labels = itertools.islice(labels, start, None, self.step_x_labels)
            list(map(self.draw_x_label, labels))
            self.draw_x_guidelines(self.field_width(), count)

    def draw_x_label(self, label):
        label_width = self.field_width()
        index, label = label
        text = etree.SubElement(self.graph, 'text', {'class': 'xAxisLabels'})
        text.text = label

        x = index * label_width + self.x_label_offset(label_width)
        y = self.graph_height + self.x_label_font_size + 3

        if self.stagger_x_labels and (index % 2):
            stagger = self.x_label_font_size + 5
            y += stagger
            move = f'M{x} {self.graph_height} v{stagger}'
            path = {'d': move, 'class': 'staggerGuideLine'}
            etree.SubElement(self.graph, 'path', path)

        text.set('x', str(x))
        text.set('y', str(y))

        if self.rotate_x_labels:
            transform = 'rotate(90 %d %d) translate(0 -%d)' % (
                x,
                y - self.x_label_font_size,
                self.x_label_font_size / 4,
            )
            text.set('transform', transform)
            text.set('style', 'text-anchor: start')
        else:
            text.set('style', 'text-anchor: middle')

    def y_label_offset(self, height):
        """
        Return an offset for drawing the y label. Currently returns 0.
        """
        # Consider height/2 to center within the field.
        return 0

    def get_field_width(self):
        return float(self.graph_width - self.font_size * 2 * self.right_font) / (
            len(self.get_x_labels()) - self.right_align
        )

    field_width = get_field_width

    def get_field_height(self):
        return float(self.graph_height - self.font_size * 2 * self.top_font) / (
            len(self.get_y_labels()) - self.top_align
        )

    field_height = get_field_height

    def draw_y_labels(self):
        "Draw the Y axis labels"
        if not self.show_y_labels:
            # do nothing
            return

        labels = self.get_y_labels()
        count = len(labels)

        labels = enumerate(iter(labels))
        start = int(not self.step_include_first_y_label)
        labels = itertools.islice(labels, start, None, self.step_y_labels)
        list(map(self.draw_y_label, labels))
        self.draw_y_guidelines(self.field_height(), count)

    def get_y_offset(self):
        result = self.graph_height + self.y_label_offset(self.field_height())
        if not self.rotate_y_labels:
            result += self.font_size / 1.2
        return result

    y_offset = property(get_y_offset)

    def draw_y_label(self, label):
        label_height = self.field_height()
        index, label = label
        text = etree.SubElement(self.graph, 'text', {'class': 'yAxisLabels'})
        text.text = label

        y = self.y_offset - (label_height * index)
        x = {True: 0, False: -3}[self.rotate_y_labels]

        if self.stagger_y_labels and (index % 2):
            stagger = self.y_label_font_size + 5
            x -= stagger
            etree.SubElement(
                self.graph,
                'path',
                {
                    'd': 'M%(x)f %(y)f h%(stagger)d' % vars(),
                    'class': 'staggerGuideLine',
                },
            )

        text.set('x', str(x))
        text.set('y', str(y))

        if self.rotate_y_labels:
            transform = 'translate(-%d 0) rotate (90 %d %d)' % (self.font_size, x, y)
            text.set('transform', transform)
            text.set('style', 'text-anchor: middle')
        else:
            text.set('y', str(y - self.y_label_font_size / 2))
            text.set('style', 'text-anchor: end')

    def draw_x_guidelines(self, label_height, count):
        "Draw the X-axis guidelines"
        if not self.show_x_guidelines:
            return
        # skip the first one
        for count in range(1, count):
            move = f'M {label_height * count} 0 v{self.graph_height}'
            path = {'d': move, 'class': 'guideLines'}
            etree.SubElement(self.graph, 'path', path)

    def draw_y_guidelines(self, label_height, count):
        "Draw the Y-axis guidelines"
        if not self.show_y_guidelines:
            return
        for count in range(1, count):
            move = f'M 0 {self.graph_height - label_height * count} h{self.graph_width}'
            path = {'d': move, 'class': 'guideLines'}
            etree.SubElement(self.graph, 'path', path)

    def draw_titles(self):
        "Draws the graph title and subtitle"
        if self.show_graph_title:
            self.draw_graph_title()
        if self.show_graph_subtitle:
            self.draw_graph_subtitle()
        if self.show_x_title:
            self.draw_x_title()
        if self.show_y_title:
            self.draw_y_title()

    def draw_graph_title(self):
        text = etree.SubElement(
            self.root,
            'text',
            {
                'x': str(self.width / 2),
                'y': str(self.title_font_size),
                'class': 'mainTitle',
            },
        )
        text.text = self.graph_title

    def draw_graph_subtitle(self):
        y_subtitle_options = [self.subtitle_font_size, self.title_font_size + 10]
        y_subtitle = y_subtitle_options[self.show_graph_title]
        text = etree.SubElement(
            self.root,
            'text',
            {'x': str(self.width / 2), 'y': str(y_subtitle), 'class': 'subTitle'},
        )
        text.text = self.graph_subtitle

    def draw_x_title(self):
        y = self.graph_height + self.border_top + self.x_title_font_size
        if self.show_x_labels:
            y_size = self.x_label_font_size + 5
            if self.stagger_x_labels:
                y_size *= 2
            y += y_size
        x = self.width / 2

        text = etree.SubElement(
            self.root, 'text', {'x': str(x), 'y': str(y), 'class': 'xAxisTitle'}
        )
        text.text = self.x_title

    def draw_y_title(self):
        x = self.y_title_font_size
        if self.y_title_text_direction == 'bt':
            x += 3
            rotate = -90
        else:
            x -= 3
            rotate = 90
        y = self.height / 2
        text = etree.SubElement(
            self.root, 'text', {'x': str(x), 'y': str(y), 'class': 'yAxisTitle'}
        )
        text.text = self.y_title
        transform = f'rotate({rotate}, {x}, {y})'
        text.set('transform', transform)

    def keys(self):
        return map(itemgetter('title'), self.data)

    def draw_legend(self):
        if not self.key:
            # do nothing
            return

        group = etree.SubElement(self.root, 'g')

        for key_count, key_name in enumerate(self.keys()):
            y_offset = (self.KEY_BOX_SIZE * key_count) + (key_count * 5)
            etree.SubElement(
                group,
                'rect',
                {
                    'x': '0',
                    'y': str(y_offset),
                    'width': str(self.KEY_BOX_SIZE),
                    'height': str(self.KEY_BOX_SIZE),
                    'class': 'key%s' % (key_count + 1),
                },
            )
            text = etree.SubElement(
                group,
                'text',
                {
                    'x': str(self.KEY_BOX_SIZE + 5),
                    'y': str(y_offset + self.KEY_BOX_SIZE),
                    'class': 'keyText',
                },
            )
            text.text = key_name

        if self.key_position == 'right':
            x_offset = self.graph_width + self.border_left + 10
            y_offset = self.border_top + 20
        if self.key_position == 'bottom':
            x_offset, y_offset = self.calculate_offsets_bottom()
        group.set('transform', 'translate(%(x_offset)d %(y_offset)d)' % vars())

    def calculate_offsets_bottom(self):
        x_offset = self.border_left + 20
        y_offset = self.border_top + self.graph_height + 5
        if self.show_x_labels:
            max_x_label_height_px = self.x_label_font_size
            if self.rotate_x_labels:
                longest_label_length = max(map(len, self.get_x_labels()))
                # note: I think 0.6 is the ratio of width to height of characters
                max_x_label_height_px *= longest_label_length * 0.6
            y_offset += max_x_label_height_px
            if self.stagger_x_labels:
                y_offset += max_x_label_height_px + 5
        if self.show_x_title:
            y_offset += self.x_title_font_size + 5
        return x_offset, y_offset

    def render_inline_styles(self):
        "Hard-code the styles into the SVG XML if style sheets are not used."
        if not self.css_inline:
            # do nothing
            return

        styles = self.parse_css()
        for node in self.root.xpath('//*[@class]'):
            cl = '.' + node.attrib['class']
            if cl not in styles:
                continue
            style = styles[cl]
            if 'style' in node.attrib:
                style += node.attrib['style']
            node.attrib['style'] = style

    def parse_css(self):
        """
        Take a .css file (classes only please) and parse it into a dictionary
        of class/style pairs.
        """
        # todo: save the prefs for use later
        # orig_prefs = cssutils.ser.prefs
        cssutils.ser.prefs.useMinified()
        pairs = (
            (r.selectorText, r.style.cssText)
            for r in self.get_stylesheet()
            if not isinstance(r, cssutils.css.CSSComment)
        )
        return dict(pairs)

    def add_defs(self, defs):
        """
        Override and place code to add defs here. TODO: what are defs?
        """

    def _get_root_attributes(self):
        ADOBE_EXT_NS = '{http://ns.adobe.com/AdobeSVGViewerExtensions/3.0/}'
        return {
            'width': str(self.width),
            'height': str(self.height),
            'viewBox': f'0 0 {self.width} {self.height}',
            ADOBE_EXT_NS + 'scriptImplementation': 'Adobe',
        }

    def start_svg(self):
        "Base SVG Document Creation"
        SVG_NAMESPACE = 'http://www.w3.org/2000/svg'
        SVG = '{%s}' % SVG_NAMESPACE
        NSMAP = {
            None: SVG_NAMESPACE,
            'xlink': 'http://www.w3.org/1999/xlink',
            'a3': 'http://ns.adobe.com/AdobeSVGViewerExtensions/3.0/',
        }
        root_attrs = self._get_root_attributes()
        self.root = etree.Element(SVG + "svg", attrib=root_attrs, nsmap=NSMAP)
        if hasattr(self, 'style_sheet_href'):
            pi = etree.ProcessingInstruction(
                'xml-stylesheet', 'href="%s" type="text/css"' % self.style_sheet_href
            )
            self.root.addprevious(pi)

        comment_strings = (
            ' Created with SVG.Graph ',
            ' SVG.Graph by Jason R. Coombs ',
            ' Based on SVG::Graph by Sean E. Russel ',
            ' Based on Perl SVG:TT:Graph by Leo Lapworth & Stephan Morgan ',
            ' ' + '/' * 66,
        )
        list(map(self.root.append, map(etree.Comment, comment_strings)))

        defs = etree.SubElement(self.root, 'defs')
        self.add_defs(defs)

        if not hasattr(self, 'style_sheet_href') and not self.css_inline:
            self.root.append(
                etree.Comment(' include default stylesheet if none specified ')
            )
            style = etree.SubElement(defs, 'style', type='text/css')
            # TODO: the text was previously escaped in a CDATA declaration... how
            #  to do that with etree?
            style.text = self.get_stylesheet().cssText

        self.root.append(etree.Comment('SVG Background'))
        etree.SubElement(
            self.root,
            'rect',
            {
                'width': str(self.width),
                'height': str(self.height),
                'x': '0',
                'y': '0',
                'class': 'svgBackground',
            },
        )

    def calculate_graph_dimensions(self):
        self.calculate_left_margin()
        self.calculate_right_margin()
        self.calculate_bottom_margin()
        self.calculate_top_margin()
        self.graph_width = self.width - self.border_left - self.border_right
        self.graph_height = self.height - self.border_top - self.border_bottom

    @staticmethod
    def load_resource_stylesheet(name, subs=None):
        if subs is None:
            subs = dict()
        template = importlib.resources.read_text('svg.charts', name)
        source = template % subs
        return cssutils.parseString(source)

    def get_stylesheet_resources(self):
        "Get the stylesheets for this instance"
        # allow css to include class variables
        class_vars = class_dict(self)
        loader = functools.partial(self.load_resource_stylesheet, subs=class_vars)
        sheets = list(map(loader, self.stylesheet_names))
        return sheets

    def get_stylesheet(self):
        cssutils.log.setLevel(30)  # disable INFO log messages

        def merge_sheets(s1, s2):
            list(map(s1.add, s2))
            return s1

        return functools.reduce(merge_sheets, self.get_stylesheet_resources())


class DrawHooks:
    """
    Mix-in for Graph subclasses providing hooks at
    various points in the rendering of a Graph.

    Use with any Graph subclass like so::

        class MyVerticalBar(DrawHooks, VerticalBar):
            def after_draw_data(self):
                self.root.append(...)
    """

    def draw_data(self):
        self.before_draw_data()
        super().draw_data()
        self.after_draw_data()

    def before_draw_data(self):
        pass

    def after_draw_data(self):
        pass


class class_dict:
    "Emulates a dictionary, but retrieves class attributes"

    def __init__(self, obj):
        self.__obj__ = obj

    def __getitem__(self, item):
        return getattr(self.__obj__, item)

    def keys(self):
        # dir returns a good guess of what attributes might be available
        return dir(self.__obj__)
