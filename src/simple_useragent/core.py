#!/usr/bin/env python3

"""
core.py: Responsible for the core functionality of the package.

This module contains the UserAgent and UserAgents classes, which are
responsible for parsing and fetching user agents from the public
'useragents.me' API and caching them locally. You can use the UserAgent
class to parse a single, custom user agent string and gain access to its
parsed attributes. 
"""
from __future__ import annotations

# Header.
__author__ = "Lennart Haack"
__email__ = "simple-useragent@lennolium.dev"
__license__ = "GNU GPLv3"
__version__ = "0.1.4"
__date__ = "2024-02-14"
__status__ = "Development"
__github__ = "https://github.com/Lennolium/simple-useragent"

# Imports.
import json
import logging
import os.path
import pathlib
import time
import random

import platformdirs
import requests
from bs4 import BeautifulSoup
from ua_parser import user_agent_parser

# Logging.
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# Fallback user agents if API is not reachable and no cached version
# is available.
_FALLBACK_DESKTOP = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/110.0.0.0 Safari/537.36"]
_FALLBACK_MOBILE = ["Mozilla/5.0 (Linux; Android 10; K) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Mobile Safari/537.3"]

_FALLBACK_JSON = pathlib.Path(os.path.dirname(__file__),
                              "data",
                              "fallback.json"
                              )

_SUPPORTED_BROWSERS = ["Chrome", "Firefox", "Safari", "Opera", "Edge",
                       "IE", "Samsung Browser", "Whale", "QQ Browser"]
_SUPPORTED_OS = ["Windows", "macOS", "Linux", "Android", "iOS"]


class UserAgent:
    """
    A class to represent a single parsed user agent.
    """

    def __init__(self, user_agent: str) -> None:
        """
        Creates a new UserAgent object from the user agent string
        and saves and categorizes its information to their
        respecting class attributes.

        :param user_agent: The user agent string to parse.
        :type user_agent: str
        :return: UserAgent instance.
        :rtype: UserAgent
        """

        self.os = None
        self.os_version = None
        self.os_version_minor = None
        self.browser = None
        self.browser_version = None
        self.browser_version_minor = None
        self.mobile = None
        self.string = None

        # Validate user agent string.
        if not isinstance(user_agent, str):
            LOGGER.warning(f"User agent string must be of type str. "
                           f"No {self.__class__.__name__} instance created. "
                           f"Returning 'None'."
                           )
        elif not user_agent or user_agent.isspace():
            LOGGER.warning(f"User agent string must not be empty. "
                           f"No {self.__class__.__name__} instance created. "
                           f"Returning 'None'."
                           )
        # Input valid: Parse ua string and save to class attributes.
        else:
            self.parse(user_agent)

    def __str__(self) -> str:
        """
        Returns the UserAgent instance as a readable string.

        :return: The user agent instance as formatted string.
        :rtype: str
        """

        # Failed initialization, wrong input, probably.
        if not self.string:
            return self.__repr__()

        os_dot = "." if self.os_version_minor else ""
        browser_dot = "." if self.browser_version_minor else ""

        return (
                f"OS: {self.os} {self.os_version}{os_dot}"
                f"{self.os_version_minor}, "
                f"Browser: {self.browser} {self.browser_version}{browser_dot}"
                f"{self.browser_version_minor}, "
                f"Mobile: {self.mobile}, "
                f"String: {self.string}")

    def __repr__(self) -> str:
        """
        Returns the user agent instance as a representation for fast
        reconstruction.

        :return: The UserAgent instance as a shortened representation.
        :rtype: str
        """

        return f"{self.__class__.__name__}({self.string!r})"

    def __dict__(self) -> dict[str, str]:
        """
        Returns the user agent instance as a dictionary.

        :return: The user agent instance as a dictionary.
        :rtype: dict
        """

        return {
                "os": self.os,
                "os_version": self.os_version,
                "os_version_minor": self.os_version_minor,
                "browser": self.browser,
                "browser_version": self.browser_version,
                "browser_version_minor": self.browser_version_minor,
                "mobile": self.mobile,
                "string": self.string,
                }

    def __eq__(self, other) -> bool:
        """
        Returns True if the user agent strings are equal.

        :param other: The other user agent instance to compare.
        :type other: UserAgent
        :return: True if user agent strings are equal.
        :rtype: bool
        """

        if not isinstance(other, self.__class__):
            raise TypeError(
                    f"Can not compare {self.__class__.__name__} with other "
                    f"types than {self.__class__.__name__}."
                    )

        return self.string == other.string

    def __getitem__(self, item) -> str:
        """
        Returns the value of the given item.

        :param item: The item to get the value from.
        :type item: str
        :return: The value of the given item.
        :rtype: str
        """

        if hasattr(self, item):
            return getattr(self, item)
        else:
            raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '"
                    f"{item}'."
                    )

    def __setitem__(self, item, value) -> None:
        """
        Sets the value of the given item.

        :param item: The item to set the value for.
        :type item: str
        :param value: The value to set.
        :type value: str
        :return: None
        """
        if hasattr(self, item):
            setattr(self, item, value)
        else:
            raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '"
                    f"{item}'."
                    )

    def __delitem__(self, item) -> None:
        """
        Deletes the given item.

        :param item: The item to delete.
        :type item: str
        :return: None
        """
        if hasattr(self, item):
            setattr(self, item, None)
        else:
            raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '"
                    f"{item}'."
                    )

    @staticmethod
    def __parse_browser(parsed: user_agent_parser.Parse) -> str:
        """
        Parses the browser name from the parsed user agent data.

        :param parsed: The parsed user agent data.
        :type parsed: user_agent_parser.Parse
        :return: The parsed browser name.
        :rtype: str
        """

        # Convert and cleanup browser.
        browser_mapping = [
                ("chrome", "Chrome"),
                ("chromium", "Chrome"),
                ("huawei", "Chrome"),
                ("safari", "Safari"),
                ("opera", "Opera"),
                ("microsoft", "Edge"),
                ("edge", "Edge"),
                ("ie", "IE"),
                ("samsung", "Samsung Browser")
                ]

        browser = parsed["user_agent"]["family"]
        if browser not in _SUPPORTED_BROWSERS:
            browser_lower = browser.lower()
            for key, value in browser_mapping:
                if key in browser_lower:
                    browser = value
                    break
            else:
                browser = "Other"

        # Fix for Safari on Linux and Windows (not possible).
        if (browser == "Safari"
                and (parsed["os"]["family"] == "Linux"
                     or parsed["os"]["family"] == "Windows"
                     or parsed["os"]["family"] == "Android")):
            browser = "Other"

        return browser

    @staticmethod
    def __parse_os(parsed: user_agent_parser.Parse) -> str:
        """
        Parses the OS name from the parsed user agent data.

        :param parsed: The parsed user agent data.
        :type parsed: user_agent_parser.Parse
        :return: The parsed OS name.
        :rtype: str
        """

        # Convert and cleanup os.
        os_mapping = [
                ("mac", "macOS"),
                ("windows", "Windows"),
                ("linux", "Linux"),
                ("ubuntu", "Linux"),
                ("debian", "Linux"),
                ("fedora", "Linux"),
                ("android", "Android"),
                ("ios", "iOS")
                ]

        os = parsed["os"]["family"]
        if os not in _SUPPORTED_OS:
            os_lower = os.lower()
            for key, value in os_mapping:
                if key in os_lower:
                    os = value
                    break
            else:
                os = "Other"

        return os

    @staticmethod
    def __parse_mobile(
            string: str,
            os: str,
            browser: str
            ) -> bool:
        """
        Parses if the OS/device is mobile from the user agent string.

        :param string: User agent string.
        :type string: str
        :param os: OS name.
        :type os: str
        :param browser: Browser name.
        :type browser: str
        :return: True if OS/device is mobile.
        :rtype: bool
        """

        # Check if OS/device is mobile.
        string_lower = string.lower()
        if os in _SUPPORTED_OS[-2:]:
            return True

        return (browser == "Samsung Browser" or "android" in string_lower or
                "iphone" in string_lower or "mobile" in string_lower)

    def parse(self, string: str) -> None:
        """
        Parses the user agent string and saves the results to the
        class attributes.

        This function is called automatically during initialization.
        Just use it if you want to parse override an existing user
        agent instance with a new string.

        :param string: The user agent string to parse.
        :type string: str
        :return: None
        """

        if not isinstance(string, str):
            raise TypeError("User agent string must be of type str.")
        elif not string or string.isspace():
            raise ValueError("User agent string must not be empty.")

        self.string = string
        parsed = user_agent_parser.Parse(string)

        # Convert and cleanup browser and os.
        self.browser = self.__parse_browser(parsed)
        self.os = self.__parse_os(parsed)

        # Convert and cleanup version numbering of browser and os from
        # parsed data.
        try:
            for data in ["user_agent", "os"]:
                for key, value in parsed[data].items():
                    if data == "user_agent":
                        data = "browser"
                    if key == "major":
                        if value is not None:
                            setattr(self, f"{data}_version", value)
                        else:
                            setattr(self, f"{data}_version", "")

                    elif key == "minor":
                        if value is not None:
                            setattr(self, f"{data}_version_minor", value)
                        else:
                            setattr(self, f"{data}_version_minor", "")

            # Check if OS/device is mobile.
            self.mobile = self.__parse_mobile(
                    string=self.string,
                    os=self.os,
                    browser=self.browser
                    )

        except Exception as e:
            LOGGER.warning(f"Could not parse version numbering from "
                           f"'user_agent_parser' data: "
                           f"{str(e.__class__.__name__)}: {str(e)}"
                           )

            for attr in ["browser_version", "browser_version_minor",
                         "os_version", "os_version_minor"]:
                setattr(self, attr, "")


class UserAgents:
    """
    Fetch real world user agents from the public 'useragents.me' API for
    use in a web scraping process to avoid bot detection.

    You can either fetch random or usage weighted user agents. It caches
    the user agents locally to avoid unnecessary API calls. The cached
    user agents are refreshed every 24 hours.

    :var max_retries: Maximum number of retries to fetch the user
        agents from the API (default=3).XXX
    :type max_retries: int
    :var timeout: Timeout in seconds for the API request (default=5).
    :type timeout: int
    :var cache_duration: The duration in seconds after which the
        cached user agents are refreshed (default=86400).
    :type cache_duration: int
    :var cache_location: The folder to save the cached user agents in.
    :type cache_location: str
    """

    _user_agents_cached = None

    def __init__(
            self,
            max_retries: int = 3,
            timeout: int = 5,
            cache_duration: int = 86400,
            cache_location: str = platformdirs.user_cache_dir(
                    appname="simple-useragent",
                    appauthor="Lennolium",
                    ensure_exists=True,
                    ),
            ) -> None:
        """
        Create a new UserAgents object, which can be used to fetch user
        agents from the public useragents.me API, cache them locally and
        return them as a string/list, dict or object (see examples).

        - Initialize the class to set custom settings:
        import simple_useragent as sua \n
        user_agents = sua.UserAgents(max_retries=5, timeout=10, ...)

        - Fetch two random mobile user agent instances:
        user_agents.get(num=2, shuffle=True, mobile=True) \n
        >> [UserAgent('Mozilla/5.0 (iPhone ...'), UserAgent(
        'Mozilla/5.0 (iPhone; ...')]

        - The functions have a convenience counterpart:
        obj = sua.get(num=1, force_cached=True) \n
        obj[0].string  >>  'Mozilla/5.0 (Windows ...' \n
        obj[0].os  >>  'Windows'

        - Fetch the 3 most common desktop user agents as str in a list:
        sua.get_list(num=3) \n
        >> ['Mozilla/5.0 (Windows ...', '...', '...']

        - Get all desktop and mobile user agents in a dict sorted by
          usage percentage:
        sua.get_dict() \n
        >> {'desktop': ['Mozilla/5.0 (Windows ...', '...'],
        'mobile': ['Mozilla/5.0 (Android ...', '...']} \n

        - Parse single user agent string and create a UserAgent object.
        ua = sua.UserAgent('Mozilla/5.0 (Windows, Chrome ...') \n
        ua.browser  >>  'Chrome' \n
        ua.browser_version  >>  '91' \n

        - Parse a single user agent string and create UserAgent object.
        sua.parse('Mozilla/5.0 (iPhone, Safari ...') \n
        >> UserAgent('Mozilla/5.0 (iPhone, Safari ...')

        :param max_retries: Maximum number of retries to fetch the user
            agents from the API (default=3).
        :type max_retries: int
        :param timeout: Timeout in seconds for the API request
            (default=5).
        :type timeout: int
        :param cache_duration: The duration in seconds after which the
            cached user agents are refreshed (default=86400 -> 24h).
        :type cache_duration: int
        :param cache_location: Folder path to save the cached user
            agents in (default=os-specific user cache).
        :type cache_location: str
        :return: None
        """

        # Settings for the API request and local cache.
        self._max_retries = max_retries
        self._timeout = timeout
        self._cache_duration = cache_duration
        self._cache_location = cache_location

    def __repr__(self) -> str:
        """
        Returns the UserAgents instance as a representation for fast
        reconstruction.
        """

        return (f"{self.__class__.__name__}"
                f"(max_retries={self._max_retries!r}, "
                f"timeout={self._timeout!r}, "
                f"cache_duration={self._cache_duration!r}, "
                f"cache_location={self._cache_location!r})")

    @staticmethod
    def __convert_to_list(response_data: list[dict]) -> list[str]:
        """
        Converts the response data from API to a list of user agents,
        sorted by usage percentage.

        :param response_data: The response data from the API.
        :type response_data: list[dict]
        :return: A list of user agents sorted by usage percentage.
        :rtype: list[str]
        """

        try:
            sorted_data = sorted(response_data, key=lambda x: x['pct'],
                                 reverse=True
                                 )
            ua_list = [entry['ua'] for entry in sorted_data]

        except Exception as e:
            LOGGER.warning(f"Could not convert response data from "
                           f"'useragents.me' to list. Maybe the API changed "
                           f"its response format? "
                           f"{str(e.__class__.__name__)}: {str(e)}"
                           )
            return []

        return ua_list

    @staticmethod
    def __fallback() -> dict[str, list[str]] | None:
        """
        Uses fallback user agents placed in the module root, if API is
        not reachable and no cached version is available eventually due
        to exceptions. At the next run, we will try to reach the API
        again.

        :return: A dictionary containing historic user agents.
        :rtype: dict or None
        """

        # Load cached user agents from json file.
        try:

            with open(_FALLBACK_JSON, "r") as fh:
                response_data = json.load(fh)

            return response_data

        except Exception as e:
            LOGGER.error(f"Could not find fallback file, that is shipped "
                         f"with the package! Verify that the file exists "
                         f"and if it does, report the issue please.\n"
                         f"{str(e.__class__.__name__)}: {str(e)}"
                         )
            return

    def __response_data(
            self,
            url: str
            ) -> requests.Response | None:
        """
        Tries to reach the API for maximum of _max_retries times and
        returns the response data or None if API could not be reached.

        :param url: The url to reach.
        :type url: str
        :return: The response data or None if API could not be reached.
        :rtype: requests.Response or None
        """

        # Try to reach API for maximum 3 times (default).
        for i in range(1, self._max_retries + 1):
            try:
                response = requests.get(url=url,
                                        timeout=self._timeout,
                                        allow_redirects=True
                                        )

            # If connection fails with exception, retry after delay.
            except Exception as e:
                LOGGER.warning(
                        f"({i}/{self._max_retries}) Try to reach "
                        f"'useragents.me' API failed with exception: "
                        f"{str(e.__class__.__name__)}: {str(e)}. Retrying in "
                        f"{i * self._timeout} seconds ..."
                        )
                time.sleep(i * self._timeout)
                continue

            if not response:
                LOGGER.warning(
                        f"({i}/{self._max_retries}) Try to reach "
                        f"'useragents.me' API failed. Retrying in "
                        f"{i * self._timeout} seconds ..."
                        )
                time.sleep(i * self._timeout)
                continue

            if response.status_code == 429:
                LOGGER.warning(
                        f"({i}/{self._max_retries}) Rate limit reached for "
                        f"'useragents.me' (15 requests/h)."
                        )
                return

            # If status code indicates no success or maybe a rate-limit,
            # retry after delay.
            if response.status_code != 200:
                LOGGER.warning(
                        f"({i}/{self._max_retries}) Try to reach "
                        f"'useragents.me' API failed with status code: "
                        f"{response.status_code}. Retrying in "
                        f"{i * self._timeout} seconds ..."
                        )
                time.sleep(i * self._timeout)
                continue

            # Success.
            else:
                return response

        return

    def __useragents_api(
            self,
            ) -> dict | None:
        """
        Fetches user agents from the public useragents.me API.

        :return: A dictionary containing the user agents fetched from
            the API or None if the API could not be reached after
            _max_retries.
        :rtype: dict or None
        """

        # For mobile user agents, we can not use the api endpoint.
        endpoints = {
                "desktop": "https://www.useragents.me/api",
                "mobile": "https://www.useragents.me/",
                }
        response_data = {"desktop": None, "mobile": None, "cached": None}

        # Fetch desktop and mobile user agents from API.
        for device, endpoint in endpoints.items():

            response = self.__response_data(endpoint)

            if not response:
                return

            # For desktop UA, we can use the json response of the API.
            if device == "desktop":

                # Rate limit reached.
                for key in response.json():
                    if "error" in key:
                        LOGGER.warning(
                                "Rate limit reached for 'useragents.me' "
                                "(15 requests/h)."
                                )
                        return

                response_data["desktop"] = \
                    self.__convert_to_list(response.json()["data"])

            # For mobile UA, we need to parse the HTML response and
            # extract the user agents from the textarea.
            else:
                try:
                    soup = BeautifulSoup(response.text, "html.parser")
                    row = soup.find(
                            "div", id="most-common-mobile-useragents-json-csv",
                            class_="row"
                            )
                    content = row.find("textarea", class_="form-control").text

                    # Remove newlines and whitespaces.
                    content = content.replace("\n", "").replace("  ", "")

                    response_data["mobile"] = \
                        self.__convert_to_list(json.loads(content))

                except Exception as e:
                    LOGGER.warning(f"Could not parse HTML response from "
                                   f"'useragents.me': "
                                   f"{str(e.__class__.__name__)}: {str(e)}"
                                   )
                    return

        if response_data["desktop"] and response_data["mobile"]:
            # Add current unix timestamp to response data.
            response_data["cached"] = int(time.time())
            return response_data

        LOGGER.warning(
                f"Could not reach 'useragents.me' API after "
                f"{self._max_retries} failed retries."
                )
        return

    def __useragents_cached(self) -> dict[str, list[str] | int] | None:
        """
        Fetches user agents from the local cache.

        :return: A dictionary containing the user agents fetched from
            the local cache or None if local cache could not be read.
        :rtype: dict or None
        """

        # Load cached user agents from json file.
        try:
            fp = pathlib.Path(self._cache_location,
                              "user_agents.json"
                              )

            with open(fp, "r") as fh:
                response_data = json.load(fh)

                return response_data

        except FileNotFoundError:
            LOGGER.info(
                    "No cached 'user_agents.json' found. Maybe your first run?"
                    )
            return

        except Exception as e:
            LOGGER.warning(
                    f"Could not load cached 'user_agents.json': "
                    f"{str(e.__class__.__name__)}: {str(e)}"
                    )
            return

    def __check_cached(self) -> bool:
        """
        Checks if the cached user agents are young enough.

        :return: True if cached user agents are young enough.
        :rtype: bool
        """

        if self._user_agents_cached:
            if ((int(time.time()) - self._user_agents_cached["cached"]) <
                    self._cache_duration):
                return True

        return False

    @staticmethod
    def __check_num(num: int,
                    mobile: bool
                    ) -> tuple[int, str]:
        """
        Checks if the requested number of user agents is valid.

        :param num: Requested number of user agents.
        :type num: int
        :param mobile: Mobile or desktop user agents requested.
        :return:
        """

        # Catch invalid num parameter.
        if num is not None:
            try:
                num = int(num)
            except (TypeError, ValueError):
                LOGGER.warning(f"Could not convert '{num}' to int. "
                               "Returning empty list ..."
                               )
                return 0, "mobile"

        if num and num < 1:
            LOGGER.warning(f"You requested '{num}' user agents. "
                           "Returning empty list ..."
                           )
            return 0, "mobile"  # Device type does not matter.

        # Enforce maximum of 45 (23 for mobile) retrievable user agents.
        if mobile:
            device = "mobile"
            num_max = 23

        else:
            device = "desktop"
            num_max = 45

        if num is None:
            num = num_max

        elif num > num_max:
            LOGGER.warning(
                    f"Maximal number of {device} user agents is {num_max}. "
                    f"Requested: {num}. Enforcing {num_max} user agents "
                    f"..."
                    )
            num = num_max

        return num, device

    def get_dict(
            self,
            force_cached: bool = None,
            ) -> dict[str, list[str] | int]:
        """
        Collects a dict of all available user agents as strings in a
        list for each desktop and mobile device. The user agents are
        sorted by usage percentage.

        :param force_cached: If True, forces the use of local file
            cached user agents, if False, forces the use of the API
            (default=None).
        :type force_cached: bool
        :return: A dict of desktop and mobile user agents.
        :rtype: dict[str, list[str]]
        """

        # 1. Check for memory cached user agents (class attributes).
        if (self._user_agents_cached
                and self._user_agents_cached["desktop"]
                and self._user_agents_cached["mobile"]
                and force_cached is not False):

            # Check if the cached uas are young enough.
            if self.__check_cached():
                return self._user_agents_cached

        # 1.5. Forced use of local file cached user agents.
        if force_cached:
            LOGGER.info("Forcing the use of local cached user agents ...")
            self._user_agents_cached = self.__useragents_cached()

            if self._user_agents_cached:
                return self._user_agents_cached

            # If no local cached user agents are available.
            LOGGER.warning("Falling back to historic user agent."
                           )
            return {"desktop": _FALLBACK_DESKTOP,
                    "mobile": _FALLBACK_MOBILE
                    }

        # 2. Check for local file cached user agents.
        if force_cached is not False:
            self._user_agents_cached = self.__useragents_cached()

            # Check if the cached uas are young enough and return them.
            if self.__check_cached():
                return self._user_agents_cached

        # 3. Call API to fetch user agents and save them to local cache.
        if force_cached is False:
            LOGGER.info("Forcing the use of 'useragents.me' API instead "
                        "of local cached user agents first ..."
                        )

        self._user_agents_cached = self.__useragents_api()

        if self._user_agents_cached:
            try:
                fp = pathlib.Path(self._cache_location,
                                  "user_agents.json"
                                  )

                # Save user agents to local file cache.
                with open(fp, "w") as fh:
                    json.dump(self._user_agents_cached, fh)

            except Exception as e:
                LOGGER.warning(
                        f"Could not save user agents to local cache. Maybe "
                        f"got no write permission for "
                        f"'{self._cache_location}'? "
                        f"{str(e.__class__.__name__)}: {str(e)}"
                        )

            return self._user_agents_cached

        # 4. Fall back to historic local file user agents.
        LOGGER.error("Falling back to historic file user agents.")
        self._user_agents_cached = self.__fallback()
        if self._user_agents_cached:
            return self._user_agents_cached

        # 5. Final fall back to historic hard-coded user agents.
        LOGGER.critical("Falling back to historic hard-coded user agents."
                        "These are not up to date and limited in number."
                        "This should never happen. Please report this issue."
                        )
        return {"desktop": _FALLBACK_DESKTOP,
                "mobile": _FALLBACK_MOBILE
                }

    def get_list(
            self,
            num: int = None,
            mobile: bool = False,
            shuffle: bool = False,
            force_cached: bool = None,
            ) -> list[str]:

        """
        Fetches a list of usage weighted user agents as strings.

        :param num: The number of user agents to fetch (desktop=45,
            mobile=23).
        :type num: int
        :param mobile: Fetches mobile user agents (default=False).
        :type mobile: bool
        :param shuffle: Shuffles the list of user agents
            (default=False).
        :type shuffle: bool
        :param force_cached: If True, forces the use of local file
            cached user agents, if False, forces the use of the API
            (default=None).
        :type force_cached: bool
        :return: A list of user agents as strings.
        :rtype: list[str]
        """

        # Check if the requested number of user agents is valid.
        num, device = self.__check_num(num, mobile)

        # Get the user agents list.
        uas = self.get_dict(
                force_cached=force_cached,
                )[device]

        if shuffle:
            uas = random.SystemRandom().choices(uas, k=num)

        return uas[:num]

    def get(
            self,
            num: int = None,
            mobile: bool = False,
            shuffle: bool = False,
            force_cached: bool = None,
            ) -> list[UserAgent]:
        """
        Fetches a list of usage weighted user agents as instances.

        :param num: The number of user agents to fetch (default:
            desktop=45, mobile=23).
        :type num: int
        :param mobile: Fetches mobile user agents (default=False).
        :type mobile: bool
        :param shuffle: Shuffles the list of user agents
            (default=False).
        :type shuffle: bool
        :param force_cached: If True, forces the use of local file
            cached user agents, if False, forces the use of the API
            (default=None).
        :return: A list of UserAgent instances.
        :rtype: list[UserAgent]
        """

        # Check if the requested number of user agents is valid.
        num, device = self.__check_num(num, mobile)

        uas = self.get_dict(
                force_cached=force_cached,
                )[device]

        if shuffle:
            uas = random.SystemRandom().choices(uas, k=num)

        return [UserAgent(ua) for ua in uas[:num] if ua]


# Convenience functions (for more settings, initialize the class).
get_list = UserAgents().get_list
get_dict = UserAgents().get_dict
get = UserAgents().get
parse = UserAgent
