import collections
import itertools
import logging
import numpy
import re


logger = logging.getLogger('uwsgiFouine')


def add_parse_options(parser):
    pass


def parse_line(line):
    res = re.match(r'.* (GET|POST) (\S+) .* in (\d+) msecs .*', line)
    if not res:
        logger.warn("Can't parse line: {0}".format(line.strip()))
        return None
    return (res.group(2), int(res.group(3)))


def condense_parsed_data(data):
    res = collections.defaultdict(list)
    for row in data:
        if row:
            res[row[0]].append(row[1])
    return res


def condensed_data_to_summary(data, aggregator):
    return dict(itertools.imap(lambda (a,b): (a, aggregator(b)), data.iteritems()))


def print_data(data):
    def print_row(row):
        details = data[row[0]]
        args = {'path': row[0],
                'total_msecs': sum(details),
                'avg_msecs': numpy.average(details),
                'max_msecs': max(details),
                'num_calls': len(details)}
        print "{path} | {total_msecs} total ms | {avg_msecs} avg ms | " \
              "{max_msecs} max ms | {num_calls} calls".format(**args)
    print "Where was the most time spent?"
    print "=============================="
    for row in  collections.Counter(
        condensed_data_to_summary(data, sum)).most_common(30):
        print_row(row)
    for i in xrange(3):
        print ""
    print "What were the slowest pages (max page load time)?"
    print "=============================="
    for row in  collections.Counter(
        condensed_data_to_summary(data, max)).most_common(30):
        print_row(row)
    for i in xrange(3):
        print ""
    print "What were the slowest pages (avg page load time)?"
    print "=============================="
    for row in  collections.Counter(
        condensed_data_to_summary(data, numpy.average)).most_common(30):
        print_row(row)


def parse_log(logfile, options):
    f = open(logfile, 'r')
    logger.info("opened " + logfile)
    data = condense_parsed_data(itertools.imap(parse_line, f))
    print_data(data)
