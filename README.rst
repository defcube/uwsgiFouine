uwsgiFounie is a uwsgi log parser.

Call uwsgiFouine with a uswgi log file, and you will be given reports
telling you where uwsgi is spending it's time.

Currently we only show output in text format, but this can be upgraded to html,
CSV, etc.

Inspired by pgFouine, a postgres log analyser.

Call uwsgiFouine -h to see all available options.

Features include:

 * --path_map_function=some.python.function: The python function you specify
     will be used to map all paths. This is useful if you want to use custom
     logic to rename paths like /index.html to / so there aren't 2 entries
     in your final report.

Example output::

  Where was the most time spent?
  ==============================
  1. / | 75,246,898 total ms | 178 avg ms | 4,948 max ms | 422,340 calls
  2. /url1/ | 57,427,567 total ms | 66 avg ms | 4,168 max ms | 866,367 calls
  3. /url2/ | 40,187,454 total ms | 19 avg ms | 3,597 max ms | 2,062,704 calls
  4. /url4/... | 19,401,099 total ms | 662 avg ms | 10,356 max ms | 29,287 calls


Installation & usage
================
1. sudo easy_install uwsgiFouine
2. run ./uwsgiFouine logfilename
