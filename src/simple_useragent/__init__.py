#!/usr/bin/env python3

"""
Fetch real world user agents from the public API of the website
'https://useragents.me/' for getting up-to-date user agents for use in
a web scraping process to avoid bot detection.

You can either fetch random or usage weighted user agents. It caches
the user agents locally to avoid unnecessary API calls. The cached
user agents are refreshed every 24 hours.

# Initialize the class to set custom settings:
import simple_useragent as sua
user_agents = sua.UserAgents(max_retries=5, timeout=10, ...)

# Fetch two random mobile user agent instances:
user_agents.get(num=2, shuffle=True, mobile=True)
>> [UserAgent('Mozilla/5.0 (iPhone ...'), UserAgent(
'Mozilla/5.0 (iPhone; ...')]

# The functions have a convenience counterpart:
obj = sua.get(num=1, force_cached=True)
obj[0].string  >>  'Mozilla/5.0 (Windows ...'
obj[0].os  >>  'Windows'

# Fetch the 3 most common desktop user agents as str in a list:
sua.get_list(num=3)
>> ['Mozilla/5.0 (Windows ...', '...', '...']

# Get all desktop and mobile user agents in a dict sorted by usage:
sua.get_dict()
>> {'desktop': ['Mozilla/5.0 (Windows ...', '...'],
'mobile': ['Mozilla/5.0 (Android ...', '...']}

# Parse single user agent string and create a UserAgent object.
ua = sua.UserAgent('Mozilla/5.0 (Windows, Chrome ...')
ua.browser  >>  'Chrome'
ua.browser_version  >>  '91'

# Parse a single user agent string and create UserAgent object.
sua.parse('Mozilla/5.0 (iPhone, Safari ...')
>> UserAgent('Mozilla/5.0 (iPhone, Safari ...')
"""

# Header.
__author__ = "Lennart Haack"
__email__ = "simple-useragent@lennolium.dev"
__license__ = "GNU GPLv3"
__version__ = "0.1.4"
__date__ = "2024-02-14"
__status__ = "Development"
__github__ = "https://github.com/Lennolium/simple-useragent"

# Imports.
from .core import UserAgents, UserAgent, get_dict, get_list, get, parse
