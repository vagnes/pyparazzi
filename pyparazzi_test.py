#!/usr/bin/env python3
import logging
import unittest
import io

import pyparazzi

logging.basicConfig(level=logging.FATAL)

class MissingSchemaC(BaseException):
    pass


class MockExceptions(BaseException):
    MissingSchema = MissingSchemaC


class MockContent(object):
    def __init__(self, content):
        self.content = content


class MockRequests(object):
    exceptions = MockExceptions()

    def __init__(self, response):
        self.response = response

    def get(self, url):
        return MockContent(self.response.pop(0))

class PyparazziTest(unittest.TestCase):

    def test_simple_domain(self):
        req = MockRequests(["<a href=\"http://facebook.com\">"])
        pyp = pyparazzi.Pyparazzi(req)

        result = io.StringIO()
        pyp.main(['facebook', 'twitter'], ["vg.no"], False, result)

        expected = "facebook.com"
        actual = result.getvalue().strip()

        self.assertEqual(expected, actual)

    def test_simple_sitemap(self):
        req = MockRequests([
            "<loc>http://somepage.no</loc>",
            "<a href=\"http://twitter.com/uri\">"
        ])

        pyp = pyparazzi.Pyparazzi(req)

        result = io.StringIO()
        pyp.main(['twitter'], ["vg.no/sitemap"], True, result)

        expected = "twitter.com/uri"
        actual = result.getvalue().strip()

        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
