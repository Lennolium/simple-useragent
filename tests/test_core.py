#!/usr/bin/env python3

"""
test_core.py: Test core functionality of the simple-useragent package.

This file contains the test cases for the core functionality of the
simple-useragent package. It tests the UserAgent and UserAgents classes
and their methods. It also tests the private methods of the UserAgents
class. The tests are written using the unittest module and the responses
library for mocking the API and website responses. We try to cover as
many edge cases as possible to ensure the stability of the package.

The tests can be run with the following command:
    $ python -m unittest tests.test_core
"""

# Header.
__author__ = "Lennart Haack"
__email__ = "simple-useragent@lennolium.dev"
__license__ = "GNU GPLv3"
__version__ = "0.1.1"
__date__ = "2024-02-08"
__status__ = "Development"
__github__ = "https://github.com/Lennolium/simple-useragent"

# Imports.
import json
import os.path
import pathlib
import time
from requests.models import Response
import unittest
from unittest.mock import Mock, patch, mock_open
from simple_useragent.core import (UserAgent, UserAgents, _FALLBACK_DESKTOP,
                                   _FALLBACK_MOBILE, user_agent_parser)
import responses


# Convenience function to load fake api and website response.
def load_fake_responses():
    # Open fake api response json file.
    fp_api = pathlib.Path(os.path.dirname(__file__),
                          "data", "fake_api_resp.json"
                          )
    fp_web = pathlib.Path(os.path.dirname(__file__),
                          "data", "fake_website_resp.html"
                          )

    with open(fp_api, 'r') as fh:
        fake_api_response = json.load(fh)

    with open(fp_web, 'r') as fh:
        fake_website_response = fh.read()

    return fake_api_response, fake_website_response


class TestUserAgent(unittest.TestCase):
    def setUp(self):
        self.user_agent_string = (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 ('
                'KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 '
                'Edg/110.0.1587.63')
        self.user_agent = UserAgent(self.user_agent_string)

    def test_init(self):
        self.assertIsInstance(self.user_agent, UserAgent)
        self.assertEqual(hasattr(self.user_agent, 'string'), True)
        self.assertEqual(hasattr(self.user_agent, 'os'), True)
        self.assertEqual(hasattr(self.user_agent, 'os_version'), True)
        self.assertEqual(hasattr(self.user_agent, 'os_version_minor'), True)
        self.assertEqual(hasattr(self.user_agent, 'browser'), True)
        self.assertEqual(hasattr(self.user_agent, 'browser_version'), True)
        self.assertEqual(hasattr(self.user_agent, 'browser_version_minor'),
                         True
                         )
        self.assertEqual(hasattr(self.user_agent, 'mobile'), True)

    def test_init_with_empty_string(self):
        self.assertIsInstance(UserAgent(''), UserAgent)
        self.assertEqual(repr(UserAgent('')), "UserAgent(None)")

        self.assertIsInstance(UserAgent(' '), UserAgent)
        self.assertEqual(repr(UserAgent(' ')), "UserAgent(None)")

    def test_init_with_wrong_input_forrmat(self):
        self.assertIsInstance(UserAgent(None), UserAgent)
        self.assertEqual(repr(UserAgent(None)), "UserAgent(None)")
        self.assertIsInstance(UserAgent(123), UserAgent)
        self.assertEqual(repr(UserAgent(123)), "UserAgent(None)")
        self.assertIsInstance(UserAgent(True), UserAgent)
        self.assertEqual(repr(UserAgent(True)), "UserAgent(None)")
        self.assertIsInstance(UserAgent(False), UserAgent)
        self.assertEqual(repr(UserAgent(False)), "UserAgent(None)")
        self.assertIsInstance(UserAgent([]), UserAgent)
        self.assertEqual(repr(UserAgent([])), "UserAgent(None)")

    def test_str(self):
        str_output = ("OS: Windows 10, Browser: Edge 110.0, Mobile: False, "
                      "String: Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63")
        self.assertEqual(str(self.user_agent), str_output)

    def test_str_with_no_string(self):
        obj = UserAgent(
                "OS: Windows 10, Browser: Edge 110.0, Mobile: False, "
                "String: Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63"
                )
        obj.string = None
        expected_result = obj.__repr__()
        self.assertEqual(str(obj), expected_result)

        obj.string = ""
        expected_result = obj.__repr__()
        self.assertEqual(str(obj), expected_result)

    def test_repr(self):
        self.assertEqual(repr(self.user_agent),
                         f"UserAgent('{self.user_agent_string}')"
                         )

    def test_dict(self):
        ua_dict = self.user_agent.__dict__()
        self.assertIsInstance(ua_dict, dict)
        self.assertEqual(ua_dict['string'], self.user_agent_string)

    def test_eq(self):
        ua_same = UserAgent(self.user_agent_string)
        ua_diff = UserAgent(
                'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 ('
                'KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.3'
                )
        self.assertTrue(self.user_agent.__eq__(ua_same))
        self.assertFalse(self.user_agent.__eq__(ua_diff))
        self.assertRaises(TypeError, self.user_agent.__eq__, "StringClass")

    def test_getitem(self):
        self.assertEqual(self.user_agent.__getitem__('string'),
                         self.user_agent_string
                         )
        self.assertEqual(self.user_agent.__getitem__('os'), 'Windows')

        self.assertRaises(AttributeError, self.user_agent.__getitem__,
                          'NotAnAttribute'
                          )

    def test_setitem(self):
        new_ua_string = ('Mozilla/5.0 (Linux; Android 10; K) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/120.0.0.0 Mobile Safari/537.3')
        self.user_agent.__setitem__('string', new_ua_string)
        self.assertEqual(self.user_agent.string, new_ua_string)

        self.assertRaises(AttributeError, self.user_agent.__setitem__,
                          "NotAnAttribute", "12345"
                          )

    def test_delitem(self):
        self.user_agent.__delitem__('string')
        self.assertIsNone(self.user_agent.string)

        self.assertRaises(AttributeError, self.user_agent.__delitem__,
                          "NotAnAttribute"
                          )

    def test_parse_private_windows(self):
        parsed = user_agent_parser.Parse(self.user_agent_string)
        browser = self.user_agent._UserAgent__parse_browser(parsed)
        os = self.user_agent._UserAgent__parse_os(parsed)
        mobile = self.user_agent._UserAgent__parse_mobile(
                self.user_agent_string,
                os,
                browser
                )
        self.assertEqual(browser, 'Edge')
        self.assertEqual(os, 'Windows')
        self.assertEqual(mobile, False)

    def test_parse_private_macos(self):
        user_agent_string = ("Mozilla/5.0 (Macintosh; Intel Mac OS X "
                             "10_15_7) AppleWebKit/537.36 (KHTML, "
                             "like Gecko) Chrome/110.0.0.0 Safari/537.36")

        parsed = user_agent_parser.Parse(user_agent_string)
        browser = self.user_agent._UserAgent__parse_browser(parsed)
        os = self.user_agent._UserAgent__parse_os(parsed)
        mobile = self.user_agent._UserAgent__parse_mobile(user_agent_string,
                                                          os,
                                                          browser
                                                          )
        self.assertEqual(browser, 'Chrome')
        self.assertEqual(os, 'macOS')
        self.assertEqual(mobile, False)

    def test_parse_private_android(self):
        user_agent_string = ("Mozilla/5.0 (Linux; Android 10; K) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/117.0.0.0 Mobile Safari/537.3")
        parsed = user_agent_parser.Parse(user_agent_string)
        browser = self.user_agent._UserAgent__parse_browser(parsed)
        os = self.user_agent._UserAgent__parse_os(parsed)
        mobile = self.user_agent._UserAgent__parse_mobile(user_agent_string,
                                                          os,
                                                          browser
                                                          )
        self.assertEqual(browser, 'Chrome')
        self.assertEqual(os, 'Android')
        self.assertEqual(mobile, True)

    def test_parse_private_unsupported(self):
        user_agent_string = ("Mozilla/5.0 (UnsupportedOS; Unknown 11; Z) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "UnsupportedBrowser/111.0.0.0")
        parsed = user_agent_parser.Parse(user_agent_string)
        browser = self.user_agent._UserAgent__parse_browser(parsed)
        os = self.user_agent._UserAgent__parse_os(parsed)
        mobile = self.user_agent._UserAgent__parse_mobile(user_agent_string,
                                                          os,
                                                          browser
                                                          )
        self.assertEqual(browser, 'Other')
        self.assertEqual(os, 'Other')
        self.assertEqual(mobile, False)

    def test_parse_private_generic_samsung(self):
        user_agent_string = ("Mozilla/5.0 (UnsupportedOS; Unknown 11; Z) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "GenericMobile/222.0.0.0")
        parsed = user_agent_parser.Parse(user_agent_string)
        browser = self.user_agent._UserAgent__parse_browser(parsed)
        os = self.user_agent._UserAgent__parse_os(parsed)
        mobile = self.user_agent._UserAgent__parse_mobile(user_agent_string,
                                                          os,
                                                          browser
                                                          )
        self.assertEqual(mobile, True)

        user_agent_string = (
                "Mozilla/5.0 (Linux; Android 14; SAMSUNG SM-S918B) "
                "AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 "
                "Chrome/115.0.0.0 Mobile Safari/537.3")
        mobile = self.user_agent._UserAgent__parse_mobile(user_agent_string,
                                                          os,
                                                          browser
                                                          )
        self.assertEqual(mobile, True)

    def test_parse_mobile(self):
        # Test for mobile device with Samsung Browser
        ua_string = (
                "Mozilla/5.0 (Linux; GenericOS 14; Vendor) "
                "AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 "
                "Chrome/115.0.0.0 Safari/537.3")
        ua = UserAgent(ua_string)
        ua.browser = 'Samsung Browser'
        self.assertTrue(ua.mobile)

        # Test for mobile device with Chrome
        ua_string = ("Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 ("
                     "KHTML, like Gecko) Chrome/74.0.3729.157 Mobile "
                     "Safari/537.36")
        ua = UserAgent(ua_string)
        self.assertTrue(ua.mobile)

        # Test for non-mobile device with Chrome
        ua_string = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/74.0.3729.157 Safari/537.36")
        ua = UserAgent(ua_string)
        self.assertFalse(ua.mobile)

        # Test for non-mobile device with Firefox
        ua_string = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) "
                     "Gecko/20100101 Firefox/66.0")
        ua = UserAgent(ua_string)
        self.assertFalse(ua.mobile)

        # Test for mobile device with Safari on iOS
        ua_string = ("Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) "
                     "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                     "Version/13.0.5 Mobile/15E148 Safari/604.1")
        ua = UserAgent(ua_string)
        self.assertTrue(ua.mobile)

        # Test for non-mobile device with Safari on macOS
        ua_string = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) "
                     "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                     "Version/13.0.3 Safari/605.1.15")
        ua = UserAgent(ua_string)
        self.assertFalse(ua.mobile)

        # Test for non-mobile device with Safari on macOS
        ua_string = "Placeholder iPhone UA string"
        mobile = ua._UserAgent__parse_mobile(ua_string,
                                             "UnknownOS",
                                             "UnknownBrowser"
                                             )
        self.assertTrue(mobile)

    def test_parse_override(self):
        # Create object and override it with new parsed data.
        obj = UserAgent(self.user_agent_string)
        new_string = ("Mozilla/5.0 (Linux; Android 10; K) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/117.0.0.0 Mobile Safari/537.3")
        obj.parse(new_string)
        self.assertEqual(obj.__dict__(), {
                'string': new_string,
                'os': 'Android',
                'os_version': '10',
                'os_version_minor': '',
                'browser': 'Chrome',
                'browser_version': '117',
                'browser_version_minor': '0',
                'mobile': True
                }
                         )

    def test_parse_override_with_empty_string(self):
        obj = UserAgent(self.user_agent_string)
        wrong_obj = list()
        self.assertRaises(ValueError, obj.parse, '')
        self.assertRaises(ValueError, obj.parse, ' ')
        self.assertRaises(TypeError, obj.parse, None)
        self.assertRaises(TypeError, wrong_obj, self.user_agent_string)

    def test_user_agent_string_is_parsed_correctly(self):
        self.assertEqual(self.user_agent.string, self.user_agent_string)
        self.assertEqual(self.user_agent.os, 'Windows')
        self.assertEqual(self.user_agent.os_version, '10')
        self.assertEqual(self.user_agent.os_version_minor, '')
        self.assertEqual(self.user_agent.browser, 'Edge')
        self.assertEqual(self.user_agent.browser_version, '110')
        self.assertEqual(self.user_agent.browser_version_minor, '0')
        self.assertEqual(self.user_agent.mobile, False)

    def test_user_agent_string_with_unsupported_browser_is_parsed_correctly(
            self
            ):
        user_agent_string = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'UnsupportedBrowser/110.0.0.0 Safari/537.36')
        user_agent = UserAgent(user_agent_string)
        self.assertEqual(user_agent.browser, 'Other')

    def test_user_agent_string_with_unsupported_os_is_parsed_correctly(self):
        user_agent_string = ('Mozilla/5.0 (UnsupportedOS NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/110.0.0.0 Safari/537.36')
        user_agent = UserAgent(user_agent_string)
        self.assertEqual(user_agent.os, 'Other')

    @patch('simple_useragent.core.UserAgent._UserAgent__parse_mobile')
    def test_parse_with_occurring_exception(self, mock_parse_mobile):
        # Mock the __parse_mobile method to raise an exception
        mock_parse_mobile.side_effect = Exception(
                'Exception intentionally triggered by test mock: '
                'Could not parse mobile attribute.'
                )

        # Test that the exception is handled and the attributes are set to
        # empty string
        self.user_agent.parse(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 ('
                'KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
                )
        self.assertEqual(self.user_agent.browser_version, '')
        self.assertEqual(self.user_agent.browser_version_minor, '')
        self.assertEqual(self.user_agent.os_version, '')
        self.assertEqual(self.user_agent.os_version_minor, '')


class TestUserAgents(unittest.TestCase):
    @responses.activate
    def setUp(self):
        # Cleanup local cache before we start
        self.test_cache_path = pathlib.Path(os.path.dirname(__file__), "cache")
        self.test_cache_file = pathlib.Path(self.test_cache_path,
                                            "user_agents.json"
                                            )

        if os.path.exists(self.test_cache_file):
            os.remove(self.test_cache_file)

        # Create instance with test cache path.
        self.user_agents = UserAgents(cache_location=str(self.test_cache_path),
                                      timeout=1,
                                      max_retries=1,
                                      )

    def test_repr(self):
        expected_repr = (
                f"UserAgents(max_retries={self.user_agents._max_retries}, "
                f"timeout={self.user_agents._timeout}, "
                f"cache_duration={self.user_agents._cache_duration}, "
                f"cache_location='{self.test_cache_path}')")
        self.assertEqual(repr(self.user_agents), expected_repr)

    def test_convert_to_list_with_correct_data(self):
        # Define a mock response data
        response_data = [
                {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "pct": 0.2
                 },
                {
                        "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 "
                              "like Mac OS X)",
                        "pct": 0.1
                        },
                {"ua": "Mozilla/5.0 (Linux; Android 10; SM-G975F)", "pct": 0.3}
                ]

        # Call the private method __convert_to_list
        result = self.user_agents._UserAgents__convert_to_list(response_data)

        # Define the expected result
        expected_result = [
                "Mozilla/5.0 (Linux; Android 10; SM-G975F)",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X)"
                ]

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_convert_to_list_with_empty_data(self):
        response_data = []
        result = self.user_agents._UserAgents__convert_to_list(response_data)
        self.assertEqual(result, [])

    def test_convert_to_list_with_single_item(self):
        response_data = [{"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                          "pct": 0.2
                          }]
        result = self.user_agents._UserAgents__convert_to_list(response_data)
        self.assertEqual(result, ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"])

    def test_convert_to_list_with_incorrect_data_structure(self):
        response_data = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"]
        result = self.user_agents._UserAgents__convert_to_list(response_data)
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

    def test_convert_to_list_with_incorrect_data(self):
        response_data = [{"wrong": "SampleValue",
                          "key": "SampleValue"
                          }]
        result = self.user_agents._UserAgents__convert_to_list(response_data)
        self.assertEqual(result, [])

    @patch('builtins.open', new_callable=mock_open,
           read_data='{"desktop": ["Mozilla/5.0 (Windows NT 10.0; Win64; '
                     'x64)"], "mobile": ["Mozilla/5.0 (Linux; Android 10; '
                     'SM-G975F)"]}'
           )
    def test_fallback_with_existing_file(self, mock_file):
        result = self.user_agents._UserAgents__fallback()
        self.assertEqual(result, {
                "desktop": ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"],
                "mobile": ["Mozilla/5.0 (Linux; Android 10; SM-G975F)"]
                }
                         )

    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_fallback_with_non_existing_file(self, mock_file):
        result = self.user_agents._UserAgents__fallback()
        self.assertIsNone(result)

    @patch('builtins.open', side_effect=PermissionError())
    def test_fallback_with_unreadable_file(self, mock_file):
        result = self.user_agents._UserAgents__fallback()
        self.assertIsNone(result)

    @patch(
            'simple_useragent.core.UserAgents._UserAgents__useragents_api',
            return_value=None
            )
    @patch(
            'simple_useragent.core.UserAgents._UserAgents__useragents_cached',
            return_value=None
            )
    @patch(
            'simple_useragent.core.UserAgents._UserAgents__fallback',
            return_value=None
            )
    def test_fallback_with_no_api_and_no_cache(self, mock_api, mock_cache,
                                               mock_fallback
                                               ):
        result = self.user_agents.get_dict()
        expected_result = {"desktop": _FALLBACK_DESKTOP,
                           "mobile": _FALLBACK_MOBILE
                           }
        self.assertEqual(result, expected_result)

    @patch('requests.get')
    def test_response_data_with_successful_request(self, mock_get):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.user_agents._UserAgents__response_data(
                'https://www.useragents.me/api'
                )
        self.assertEqual(result, mock_response)

    @patch('requests.get', side_effect=Exception('API unreachable'))
    def test_response_data_with_unreachable_api(self, mock_get):
        result = self.user_agents._UserAgents__response_data(
                'https://www.useragents.me/api'
                )
        self.assertIsNone(result)

    @patch('requests.get')
    def test_response_data_with_non_successful_status_code(self, mock_get):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = self.user_agents._UserAgents__response_data(
                'https://www.useragents.me/api'
                )
        self.assertIsNone(result)

    @patch('requests.get', return_value=None)
    def test_response_data_with_no_response(self, mock_get):
        result = self.user_agents._UserAgents__response_data(
                'https://www.useragents.me/api'
                )
        self.assertIsNone(result)

    @patch('requests.get')
    def test_response_data_with_rate_limit_reached(self, mock_get):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        result = self.user_agents._UserAgents__response_data(
                'https://www.useragents.me/api'
                )
        self.assertIsNone(result)

    @patch('simple_useragent.core.UserAgents._UserAgents__response_data',
           return_value=None
           )
    def test_useragents_api_with_none_response(self, mock_response_data):
        result = self.user_agents._UserAgents__useragents_api()

        self.assertIsNone(result)

    # 'simple_useragent.core.UserAgent._UserAgent__parse_mobile'

    # patch bs4.BeautifulSoup.find function to return a mock object
    @patch('bs4.BeautifulSoup.find')
    @responses.activate
    def test_useragents_api_with_occurring_exception(self, mock_bs4_find):

        # Load fake api and website response to mock the requests.
        fake_api, fake_website = load_fake_responses()
        responses.add(responses.GET, 'https://www.useragents.me/api',
                      json=fake_api, status=200
                      )
        responses.add(responses.GET, 'https://www.useragents.me/',
                      body=fake_website, status=200
                      )

        # Mock the __parse_mobile method to raise an exception
        mock_bs4_find.side_effect = Exception(
                'Exception intentionally triggered by test mock:'
                'BeautifulSoup did not find the expected element'
                )

        # Test that the exception is handled.
        result = self.user_agents._UserAgents__useragents_api()
        self.assertIsNone(result)

    # @responses.activate
    # def test_useragents_api_finally_returns_none(self):
    #     # Load fake api and website response to mock the requests.
    #     fake_api, fake_website = load_fake_responses()
    #     responses.add(responses.GET, 'https://www.useragents.me/api',
    #                   json=fake_api, status=200
    #                   )
    #     responses.add(responses.GET, 'https://www.useragents.me/',
    #                   body=fake_website, status=200
    #                   )
    #
    #     user_agents = UserAgents(cache_location=str(self.test_cache_path),
    #                              timeout=1,
    #                              max_retries=1,
    #                              )
    #
    #     user_agents.endpoints = {}
    #
    #     result = user_agents._UserAgents__useragents_api()
    #     self.assertIsNone(result)

    @patch('requests.get')
    def test_useragents_api_with_rate_limit_error(self, mock_get):
        mock_response = Mock(spec=Response)
        # The API answers with 200, but json response contains an error.
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "Rate limit reached"}
        mock_get.return_value = mock_response

        result = self.user_agents._UserAgents__useragents_api()
        self.assertIsNone(result)

    @responses.activate
    def test_useragents_api_with_correct_response(self):
        # Load fake api and website response to mock the requests.
        fake_api, fake_website = load_fake_responses()
        responses.add(responses.GET, 'https://www.useragents.me/api',
                      json=fake_api, status=200
                      )
        responses.add(responses.GET, 'https://www.useragents.me/',
                      body=fake_website, status=200
                      )

        result = self.user_agents.get_dict(force_cached=False)
        result_time_delta = abs(int(time.time()) - int(result["cached"]))
        result_desktop = result["desktop"][0]
        result_mobile = result["mobile"][0]

        # Check the result
        self.assertLessEqual(result_time_delta, 10)
        self.assertEqual(result_desktop,
                         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/110.0.0.0 Safari/537.36"
                         )
        self.assertEqual(result_mobile, (
                "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 ("
                "KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.3")
                         )

    @patch('builtins.open', new_callable=mock_open,
           read_data='{"desktop": ["Mozilla/5.0"], "mobile": ["Mozilla/5.0"]}'
           )
    @patch('json.load')
    def test_useragents_cached_with_existing_file(self, mock_json_load,
                                                  mock_file
                                                  ):
        mock_json_load.return_value = {"desktop": ["Mozilla/5.0"],
                                       "mobile": ["Mozilla/5.0"]
                                       }
        result = self.user_agents._UserAgents__useragents_cached()
        self.assertEqual(result, {"desktop": ["Mozilla/5.0"],
                                  "mobile": ["Mozilla/5.0"]
                                  }
                         )

    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_useragents_cached_with_non_existing_file(self, mock_file):
        result = self.user_agents._UserAgents__useragents_cached()
        self.assertIsNone(result)

    @patch('builtins.open', side_effect=Exception('Unexpected error'))
    def test_useragents_cached_with_unexpected_error(self, mock_file):
        result = self.user_agents._UserAgents__useragents_cached()
        self.assertIsNone(result)

    # Test __check_num method.
    def test_check_num_with_valid_values(self):
        num, device = self.user_agents._UserAgents__check_num(5, True)
        self.assertEqual(num, 5)
        self.assertEqual(device, 'mobile')

    def test_check_num_with_invalid_num(self):
        num, device = self.user_agents._UserAgents__check_num(-1, True)
        self.assertEqual(num, 0)
        self.assertEqual(device, 'mobile')

        num, device = self.user_agents._UserAgents__check_num(0, True)
        self.assertEqual(num, 0)
        self.assertEqual(device, 'mobile')

        num, device = self.user_agents._UserAgents__check_num(50, True)
        self.assertEqual(num, 23)
        self.assertEqual(device, 'mobile')

    def test_check_num_with_invalid_type(self):
        num, device = self.user_agents._UserAgents__check_num('invalid', True)
        self.assertEqual(num, 0)
        self.assertEqual(device, 'mobile')

    # Test the get_dict method.
    @patch.object(UserAgents, '_UserAgents__useragents_api')
    def test_get_dict_with_api_success(self, mock_api):
        mock_api.return_value = {"desktop": ["Mozilla/5.0"],
                                 "mobile": ["Mozilla/5.0"]
                                 }
        result = self.user_agents.get_dict()
        self.assertEqual(result, {"desktop": ["Mozilla/5.0"],
                                  "mobile": ["Mozilla/5.0"]
                                  }
                         )

    @patch.object(UserAgents, '_UserAgents__useragents_api')
    @patch.object(UserAgents, '_UserAgents__useragents_cached')
    def test_get_dict_with_cache(self, mock_cache, mock_api):
        mock_cache.return_value = {"desktop": ["Mozilla/5.0"],
                                   "mobile": ["Mozilla/5.0"]
                                   }
        result = self.user_agents.get_dict(force_cached=True)
        self.assertEqual(result, {"desktop": ["Mozilla/5.0"],
                                  "mobile": ["Mozilla/5.0"]
                                  }
                         )
        mock_api.assert_not_called()

    @patch.object(UserAgents, '_UserAgents__useragents_cached')
    def test_get_dict_with_no_local_cache(self, mock_cache):
        # Set up the mock to return None
        mock_cache.return_value = None

        result = self.user_agents.get_dict(force_cached=True)

        # Check that the result is the fallback user agents
        self.assertEqual(result, {"desktop": _FALLBACK_DESKTOP,
                                  "mobile": _FALLBACK_MOBILE
                                  }
                         )

    @patch('simple_useragent.core.UserAgents._UserAgents__useragents_api',
           return_value="fake_api_return_data"
           )
    @patch('builtins.open', side_effect=PermissionError("Test Mock Permission"
                                                        "Error"
                                                        )
           )
    def test_get_dict_with_save_cache_failure(self, mock_file, mock_api):

        result = self.user_agents.get_dict(force_cached=False)

        # Check that the result is the fallback user agents
        self.assertEqual(result, "fake_api_return_data")

    @patch('simple_useragent.core.UserAgents._UserAgents__useragents_api',
           return_value=None
           )
    @patch('simple_useragent.core.UserAgents._UserAgents__fallback',
           return_value="fake_fallback_return_data"
           )
    def test_get_dict_with_fallback(self, mock_fallback, mock_api):

        result = self.user_agents.get_dict(force_cached=False)

        # Check that the result is the fallback user agents
        self.assertEqual(result, "fake_fallback_return_data"
                         )

    @patch.object(UserAgents, '_UserAgents__useragents_cached')
    @patch.object(UserAgents, '_UserAgents__check_cached')
    def test_get_dict_with_local_cache(self, mock_check_cached,
                                       mock_useragents_cached
                                       ):
        # Set up the mocks to return specific values
        mock_useragents_cached.return_value = {"desktop": ["Mozilla/5.0"],
                                               "mobile": ["Mozilla/5.0"]
                                               }
        mock_check_cached.return_value = True

        result = self.user_agents.get_dict(force_cached=True)

        # Check that the result is the mocked user agents
        self.assertEqual(result, {"desktop": ["Mozilla/5.0"],
                                  "mobile": ["Mozilla/5.0"]
                                  }
                         )

    @patch('simple_useragent.core.UserAgents._UserAgents__useragents_cached',
           return_value="fake_cached_return_data"
           )
    @patch('simple_useragent.core.UserAgents._UserAgents__check_cached',
           return_value=True
           )
    def test_get_dict_with_young_cache(self,
                                       mock_check_cached,
                                       mock_useragents_cached
                                       ):

        result = self.user_agents.get_dict()

        # Check that the result is the fallback user agents
        self.assertEqual(result, "fake_cached_return_data")

    # Test shuffle of get_list method.
    def test_get_list_shuffle(self):
        with patch.object(UserAgents, 'get_dict') as mock_get_dict:
            mock_get_dict.return_value = {
                    "desktop": ["Mozilla/1.0", "Mozilla/2.0", "Mozilla/3.0"],
                    "mobile": ["Mozilla/4.0", "Mozilla/5.0", "Mozilla/6.0"]
                    }
            result1 = self.user_agents.get_list(num=3, shuffle=True)
            result2 = self.user_agents.get_list(num=3, shuffle=True)
            self.assertNotEqual(result1, result2)

    # Test shuffle of get method.
    def test_get_shuffle(self):
        with patch.object(UserAgents, 'get_dict') as mock_get_dict:
            mock_get_dict.return_value = {
                    "desktop": ["Mozilla/1.0", "Mozilla/2.0", "Mozilla/3.0"],
                    "mobile": ["Mozilla/4.0", "Mozilla/5.0", "Mozilla/6.0"]
                    }
            result1 = self.user_agents.get(num=3, shuffle=True)
            result2 = self.user_agents.get(num=3, shuffle=True)
            self.assertNotEqual([ua.string for ua in result1],
                                [ua.string for ua in result2]
                                )

    # Test all public methods of the module with correct data.
    def test_user_agents_are_returned_in_correct_format(self):

        result_obj1 = self.user_agents.get(num=1)
        result_obj2 = self.user_agents.get(num=2)
        result_obj3 = self.user_agents.get()
        result_obj4 = self.user_agents.get(num=20, mobile=False)
        result_obj5 = self.user_agents.get(num=10, mobile=True)

        result_list1 = self.user_agents.get_list(num=1)
        result_list2 = self.user_agents.get_list(num=2)
        result_list3 = self.user_agents.get_list()
        result_list4 = self.user_agents.get_list(num=20, mobile=False)
        result_list5 = self.user_agents.get_list(num=10, mobile=True)

        result_dict = self.user_agents.get_dict()

        # Object.
        self.assertIsInstance(result_obj1, list)
        self.assertIsInstance(result_obj1[0], UserAgent)
        self.assertEqual(len(result_obj1), 1)
        self.assertIsInstance(result_obj2, list)
        self.assertIsInstance(result_obj2[0], UserAgent)
        self.assertEqual(len(result_obj2), 2)
        self.assertIsInstance(result_obj3, list)
        self.assertIsInstance(result_obj3[0], UserAgent)
        self.assertGreaterEqual(len(result_obj3), 10)

        for ua in result_obj4:
            self.assertEqual(ua.mobile, False)

        for ua2 in result_obj5:
            self.assertEqual(ua2.mobile, True)

        # List.
        self.assertIsInstance(result_list1, list)
        self.assertIsInstance(result_list1[0], str)
        self.assertEqual(len(result_list1), 1)
        self.assertIsInstance(result_list2, list)
        self.assertIsInstance(result_list2[0], str)
        self.assertEqual(len(result_list2), 2)
        self.assertIsInstance(result_list3, list)
        self.assertIsInstance(result_list3[0], str)
        self.assertGreaterEqual(len(result_list3), 10)
        self.assertEqual(len(result_list4), 20)
        self.assertEqual(len(result_list5), 10)

        # Dict (as get and get_list are getting the data from get_dict,
        # we do not test it as much).
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(len(result_dict), 3)
        self.assertEqual(result_dict.keys(), {"desktop", "mobile", "cached"})
        self.assertIsInstance(result_dict["desktop"], list)
        self.assertIsInstance(result_dict["desktop"][0], str)
        self.assertIsInstance(result_dict["mobile"], list)
        self.assertIsInstance(result_dict["mobile"][0], str)
        self.assertIsInstance(result_dict["cached"], int)
