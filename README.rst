Call uwsgiFouine with a uswgi log file, and you will be given reports
telling you where uwsgi is spending it's time.

Currently we only show output in text format, but this can be upgraded to html,
CSV, etc.

Inspired by pgFouine, a postgres log analyser.

Call uwsgiFounie -h to see all available options.

Features include:

 * --path_map_function=some.python.function: The python function you specify
     will be used to map all paths. This is useful if you want to use custom
     logic to rename paths like /index.html to / so there aren't 2 entries
     in your final report.