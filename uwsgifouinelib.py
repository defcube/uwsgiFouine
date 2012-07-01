import collections
from importlib import import_module
import itertools
import logging
try:
    from numpy import average
except ImportError:
    def average(data):
        return sum(data) / len(data)
import re


logger = logging.getLogger('uwsgiFouine')


def add_parse_options(parser):
    parser.add_option('--num_results', action='store',
                      dest='num_results', default=30, type='int')
    parser.add_option('--path_map_function', action='store',
                      dest='path_map_function', default=False,
                      help='A python function to rename paths'),


class LineParser(object):
    def __init__(self, path_map_function=None):
        if path_map_function:
            self.path_map_function = string_to_symbol(path_map_function)
        else:
            self.path_map_function = None

    def parse_line(self, line):
        res = re.match(r'.* (GET|POST) (\S+) .* in (\d+) msecs .*', line)
        if not res:
            if logger.isEnabledFor(logger.warn):
                logger.warn("Can't parse line: {0}".format(line.strip()))
            return None
        path = res.group(2).split('?')[0]
        if self.path_map_function:
            path = self.path_map_function(path)
        return path, int(res.group(3))


def condense_parsed_data(data):
    res = collections.defaultdict(list)
    for row in data:
        if row:
            res[row[0]].append(row[1])
    return res


def condensed_data_to_summary(data, aggregator):
    return dict(itertools.imap(lambda (a,b): (a, aggregator(b)), data.iteritems()))


def string_to_symbol(str):
    parts = str.split('.')
    module = import_module('.'.join(parts[:-1]))
    return getattr(module, parts[-1])


def print_data(data, num_results):
    import locale
    locale.setlocale(locale.LC_ALL, 'en_US')
    row_count = iter(xrange(1, 999999))
    def print_row(row):
        details = data[row[0]]
        args = {'path': row[0],
                'row_count': row_count.next(),
                'total_msecs':
                    locale.format('%d', sum(details), grouping=True),
                'avg_msecs':
                    locale.format('%d', average(details), grouping=True),
                'max_msecs':
                    locale.format('%d', max(details), grouping=True),
                'num_calls':
                    locale.format('%d', len(details), grouping=True),}
        print "{row_count}. {path} | {total_msecs} total ms | {avg_msecs} avg ms | " \
              "{max_msecs} max ms | {num_calls} calls".format(**args)
    print "Where was the most time spent?"
    print "=============================="
    for row in  collections.Counter(
        condensed_data_to_summary(data, sum)).most_common(num_results):
        print_row(row)
    for i in xrange(3):
        print ""
    row_count = iter(xrange(1, 999999))
    print "What were the slowest pages (max page load time)?"
    print "=============================="
    for row in  collections.Counter(
        condensed_data_to_summary(data, max)).most_common(num_results):
        print_row(row)
    for i in xrange(3):
        print ""
    row_count = iter(xrange(1, 999999))
    print "What were the slowest pages (avg page load time)?"
    print "=============================="
    for row in  collections.Counter(
        condensed_data_to_summary(data, average))\
        .most_common(num_results):
        print_row(row)


def parse_log(logfile, options):
    f = open(logfile, 'r')
    logger.info("opened " + logfile)
    parser = LineParser(options.path_map_function)
    data = condense_parsed_data(itertools.imap(parser.parse_line, f))
    print_data(data, options.num_results)
