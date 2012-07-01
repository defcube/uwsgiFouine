import unittest
import uwsgifouinelib as main

class MainTest(unittest.TestCase):
    def test_parse_line(self):
        line = "[pid: 24386|app: 0|req: 482950/4125645] 86.221.170.65 ()" \
               " {44 vars in 1322 bytes} [Tue Jan  3 05:01:31 2012] GET " \
               "/contest/log_presence/shhootter/?_=1325592089910 " \
               "=> generated 192 bytes in 21 msecs (HTTP/1.1 200) " \
               "4 headers in 188 bytes (1 switches on core 0)"
        res = main.LineParser().parse_line(line)
        self.assertEquals(res, ('/contest/log_presence/shhootter/', 21))

    def test_raise_error_on_bad_line(self):
        self.failUnlessRaises(lambda: main.parse_line('bad line'))

    def test_condense_parsed(self):
        data =  [
             ('/jsi18n/', 7),
             ('/jsi18n/', 3),
             ('/jsi18n/', 4),
             ('/contest/log_presence/tnt6969/?_=1325592111675', 12),
             ('/?join_overlay=1&_=1325592160697', 54),
             ('/demongirl/', 269),
             ('/next/lovers_xxo/', 32),
             ('/creative/im/1.js?track=track&tour=Qbun&c=0&wm=13uQy', 4),
        ]
        res = main.condense_parsed_data(data)
        self.failUnlessEqual(list(res['/jsi18n/']), [7, 3, 4])
        self.failUnlessEqual(list(res['/demongirl/']), [269])

    def test_condensed_data_aggregator(self):
        data = {'/123/': [4,3,2], '/b/': [2]}
        out = main.condensed_data_to_summary(data, sum)
        self.failUnlessEqual(out, {'/123/': 9, '/b/': 2})

if __name__ == '__main__':
    unittest.main()
