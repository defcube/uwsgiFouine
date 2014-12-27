import itertools
import locale
import logging
import re
import sys

from collections import defaultdict, namedtuple

try:
    from collections import Counter
except ImportError:
    from counter import Counter

try:
    from importlib import import_module
except ImportError:
    import_module = None

try:
    from numpy import average
except ImportError:
    def average(data):
        return sum(data) / len(data)





__version__ = '1.7.dev0'

logger = logging.getLogger('uwsgiFouine')
if len(logger.handlers) == 0:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(levelname)s: %(message)s"
        )
    )
    logger.addHandler(handler)
    del handler

Result = namedtuple('Result', ('path', 'min', 'max', 'avg', 'sum', 'cnt'))





class LineParser(object):
    _re = re.compile(r'(?:POST|GET|DELETE|PUT) (\S*?) => generated .*? in (\d+) msecs')

    def __init__(self, path_map_function=None):
        if path_map_function:
            self.path_map_function = string_to_symbol(path_map_function)
        else:
            self.path_map_function = None


    def parse_line(self, line):
        try:
            res = self._re.search(line).groups()
        except AttributeError:
            logger.debug("Can't parse line: %s", line.strip())
            return None
        path = res[0].split('?')[0]
        if self.path_map_function:
            path = self.path_map_function(path)
        return path, int(res[1])



class Formats(dict):
    def register(self, name=None):
        '''a decorator used to register output formaters

        Example::

            FORMATS = Formats()

            @FORMATS.register('py')
            def output_as_python(data, args):
                return data
        '''
        def decorator(func):
            self[name or func.func_name] = func
            return func
        return decorator



FORMATS = Formats()



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


@FORMATS.register('text')
def print_data(data, args):
    num_results = args.num_results

    def print_title(value):
        print value
        print '=' * len(value)

    def print_row():
        details = data[row[0]]
        print locale.format_string(
            '%(count)d. %(path)s | %(total_msecs)d total ms | %(avg_msecs)d avg ms | %(max_msecs)d max ms | %(num_calls)d calls',
            {
                'count': count,
                'path': row[0],
                'total_msecs': sum(details),
                'avg_msecs': average(details),
                'max_msecs': max(details),
                'num_calls': len(details),
            },
            grouping=True,
        )

    print_title("Where was the most time spent?")
    for count, row in enumerate(
        Counter(condensed_data_to_summary(data, sum))
        .most_common(num_results)
        ):
        print_row()
    print "\n\n\n"

    print_title("What were the slowest pages (max page load time)?")
    for count, row in enumerate(
        Counter(condensed_data_to_summary(data, max))
        .most_common(num_results)
        ):
        print_row()
    print "\n\n\n"

    print_title("What were the slowest pages (avg page load time)?")
    for count, row in enumerate(
        Counter(condensed_data_to_summary(data, average))
        .most_common(num_results)
        ):
        print_row()


@FORMATS.register('dump_json')
def dump_json(data, args):
    import json
    print json.dumps(
        data
    )


def aggregate(data):
    '''
    return an iterator over a result of :func:`condense_parsed_data`;
    where each item is a :data:`Result`
    '''
    return (
        Result(
            k,
            min(v),
            max(v),
            average(v),
            sum(v),
            len(v),
        )
        for k, v in data.iteritems()
        if v
    )


@FORMATS.register('json')
def print_json(data, args):
    import json
    print json.dumps(
        dict(
            (
                row.path,
                dict(zip(row._fields[1:], row[1:])),
            )
            for row in aggregate(data)
        ),
        indent=2,
    )



def main():
    import argparse
    import select

    try:
        default_locale = '.'.join(locale.getdefaultlocale())
    except TypeError:
        default_locale = 'C'

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-q', '--quiet', action='store_const', const=0, dest='verbose')
    parser.add_argument('-v', '--verbose', action='count', default=1)
    parser.add_argument('-d', '--debug', action='store_const', const=3, dest='verbose')

    parser.add_argument('--format', default='text', choices=FORMATS,
        help='output format')
    parser.add_argument('--path_map_function', default=None, metavar='name',
        help='A python function to rename paths')

    group = parser.add_argument_group(
        'Text options',
        'Apply only when --format text; ignored on other formats.')
    group.add_argument('--num_results', default=30, type=int, metavar='N',
        help='limit output results')
    group.add_argument('--locale', default=default_locale,
        help='locale used for printing report')

    parser.add_argument('logfile', nargs='*', type=argparse.FileType('r'))

    args = parser.parse_args()

    if args.verbose == 0:
        logger.setLevel(logging.ERROR)
    elif args.verbose == 1:
        logger.setLevel(logging.WARNING)
    elif args.verbose == 2:
        logger.setLevel(logging.INFO)
    elif args.verbose >= 3:
        logger.setLevel(logging.DEBUG)

    try:
        locale.setlocale(locale.LC_ALL, args.locale)
    except locale.Error, error:
        logger.warn('unable to set locale: %s: %s', args.locale, error)

    if not args.logfile:
        if select.select((sys.stdin,), (), (), 0.0)[0]:
            args.logfile = (sys.stdin,)
        else:
            parser.error('Please feed me with at least a logfile or data on stdin.')

    maps = []
    parse_line = LineParser(args.path_map_function).parse_line
    for logfile in args.logfile:
        try:
            logger.info('parsing %s', logfile.name)
            maps.append(itertools.imap(parse_line, logfile))
        except KeyboardInterrupt, err:
            logger.warn('caught %s', err)
            break

    data = []
    try:
        data = condense_parsed_data(itertools.chain(*maps))
    except KeyboardInterrupt, err:
        logger.warn('caught %s while condensating', err)

    FORMATS[args.format](data, args)




if __name__ == '__main__':
    main()
