from collections import defaultdict
try:
    from collections import Counter
except ImportError:
    from counter import Counter
try:
    from importlib import import_module
except ImportError:
    import_module = None
import itertools
import logging
try:
    from numpy import average
except ImportError:
    def average(data):
        return sum(data) / len(data)
import re
import sys


logger = logging.getLogger('uwsgiFouine')


def add_parse_arguments(parser):
    parser.add_argument('--num_results', default=30, type=int)
    parser.add_argument('--path_map_function', default=None,
                        help='A python function to rename paths')
    parser.add_argument('--locale', default='en_US',
                        help='locale used for printing report')


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
    res = defaultdict(list)
    for row in data:
        if row:
            res[row[0]].append(row[1])
    return res


def condensed_data_to_summary(data, aggregator):
    return dict(itertools.imap(lambda (a,b): (a, aggregator(b)), data.iteritems()))


def string_to_symbol(str):
    parts = str.split('.')
    if import_module:
        module = import_module('.'.join(parts[:-1]))
    else:
        module = __import__('.'.join(parts[:-1]), globals(), locals(), [parts[-1]], 0)
    return getattr(module, parts[-1])


def print_data(data, num_results, locale_name):
    import locale
    locale.setlocale(locale.LC_ALL, locale_name)
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
    for row in Counter(
        condensed_data_to_summary(data, sum)).most_common(num_results):
        print_row(row)
    for i in xrange(3):
        print ""
    row_count = iter(xrange(1, 999999))
    print "What were the slowest pages (max page load time)?"
    print "=============================="
    for row in Counter(
        condensed_data_to_summary(data, max)).most_common(num_results):
        print_row(row)
    for i in xrange(3):
        print ""
    row_count = iter(xrange(1, 999999))
    print "What were the slowest pages (avg page load time)?"
    print "=============================="
    for row in Counter(
        condensed_data_to_summary(data, average))\
        .most_common(num_results):
        print_row(row)


def parse_log(logfile, args):
    if not logfile:
        import select
        if select.select((sys.stdin,), (), (), 0.0)[0]:
            f = sys.stdin
        else:
            return False
        logfile = 'stdin'
    else:
        f = open(logfile, 'r')
    logger.info("opened " + logfile)
    parser = LineParser(args.path_map_function)
    data = condense_parsed_data(itertools.imap(parser.parse_line, f))
    print_data(data, args.num_results, args.locale)
