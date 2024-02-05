#!/usr/bin/env python3

"""
__init__.py: Init file for simple_useragent package.

Fetch real world user agents from the public API of the website
'https://useragents.me/' for fetching up-to-date user agents for use in
a web scraping process to avoid bot detection.

You can either fetch random or usage weighted user agents. It caches
the user agents locally to avoid unnecessary API calls. The cached
user agents are refreshed every 24 hours.
"""

# Header.
__author__ = "Lennart Haack"
__email__ = "simple-useragent@lennolium.dev"
__license__ = "GNU GPLv3"
__version__ = "0.1.0"
__date__ = "2024-01-31"
__status__ = "Development"
__github__ = "https://github.com/Lennolium/simple-useragent"

# Imports.
from simple_useragent.core import (UserAgents, UserAgent, get_dict, get_list,
                                   get, parse)
