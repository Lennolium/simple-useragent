<!--- Logo -->

<div align="center">  
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Lennolium/simple-useragent/main/img/banner_dark.png" width="750vw">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Lennolium/simple-useragent/main/img/banner_light.png" width="750vw">
  <img alt="Application Banner" src="https://raw.githubusercontent.com/Lennolium/simple-useragent/main/img/banner_light.png" width="750vw">
</picture>
</div>
<br>

<!--- Badges -->

<div align="center"> 
  <a href="https://github.com/Lennolium/simple-useragent/branches" > 
    <img src="https://img.shields.io/github/last-commit/Lennolium/simple-useragent?label=Last%20Updated&color=orange" alt="last updated" >
  <a></a>  
   <a href="https://app.codacy.com/gh/Lennolium/swiftGuard/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade" > 
    <img src="https://app.codacy.com/project/badge/Grade/7e4271efc8894c9fab80e2f27f896a87" alt="code quality" >
    <a></a>
   <a href="https://github.com/Lennolium/simple-useragent/commits/main" > 
    <img src="https://img.shields.io/github/commit-activity/m/Lennolium/simple-useragent?label=Commit%20Activity" 
alt="commit activity" >
     <a></a>
  <a href="https://github.com/Lennolium/simple-useragent/releases" > 
    <img src="https://img.shields.io/badge/Version-0.1.0-brightgreen" 
alt="stable version" >
     <br>
  <a href="https://github.com/Lennolium/simple-useragent/issues" > 
    <img src="https://img.shields.io/github/issues-raw/Lennolium/simple-useragent?label=Open%20Issues&color=critical" alt="open issues" >
  <a href="https://github.com/Lennolium/simple-useragent/issues?q=is%3Aissue+is%3Aclosed" > 
    <img src="https://img.shields.io/github/issues-closed-raw/Lennolium/simple-useragent?label=Closed%20Issues&color=inactive" alt="closed issues" > 
     <a href="#" > 
    <img src="https://img.shields.io/github/repo-size/Lennolium/simple-useragent?label=Repo%20Size&color=yellow" alt="repo size" >
  <a href="https://github.com/Lennolium/simple-useragent/blob/main/LICENSE" > 
    <img src="https://img.shields.io/github/license/Lennolium/simple-useragent?label=License&color=blueviolet" alt="License" > 
  <a></a> </a> </a> </a> </a> </a> </a> </a> </a>
</div>

<!--- Title Line -->

<div align="center">
  <h1></h1> 
</div>

<!--- Description -->

<div align="center">
Fetches real world, up-to-date user agents for use in web scraping to avoid bot detection.
No more fake or outdated user agents, only user agents of real users.
You can either get random or usage-weighted user agents. It caches
the user agents locally to avoid unnecessary API calls, and refreshes them automatically every 24 hours
from the public API of <a href="https://useragents.me/">useragents.me</a>.

<br><br>

[![Donate](https://img.shields.io/badge/Donate-Paypal-blue?style=flat-square&logo=paypal)](https://www.paypal.me/smogg)
[![BuyMeACoffee](https://img.shields.io/badge/Buy%20me%20a-Coffee-f5d132?style=flat-square&logo=buymeacoffee)](https://buymeacoffee.com/lennolium)
</div>
<div align="center">
  <h3></h3>  
    </div>     
&nbsp;

<!--- Table of contents -->

## Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Quickstart](#quickstart)
  - [Advanced Usage](#advanced-usage)
  - [Settings and Parameters](#settings-and-parameters)
- [Development](#development)
- [Contributors](#contributors)
- [Credits](#credits)
- [License](#license)

&nbsp;

<!--- Features -->

## Features

- __Up-to-date:__ No fake or outdated user agents, only real world data. Refreshed every 24 hours.
- __Wide Support:__ User Agents for Windows, macOS, Linux, Android and iOS devices: Google Chrome, Firefox, Safari, Edge, Opera, Whale and QQ browsers.
- __Lightweight:__ Designed to consume minimal system resources and caches user agents locally.
- __Simple:__ Easy to use and understand with a clean and simple API.
- __Compatible:__ Supports Python 3.8 and above. Runs on Windows, macOS and Linux.
- __Privacy:__ Protects the user by not collecting or sending any personal data.
- __Open Source:__ Provides transparency and allows community contributions for continuous development.

&nbsp;

<!--- Installation -->

## Installation

Just install the package from [PyPi](https://pypi.org/project/simple-useragent/) using pip:

   ```bash
    pip install simple-useragent
   ```

&nbsp;

<!--- Usage -->

## Usage

#### Quickstart

Just import the package and use the convenience functions. For more advanced usage, you can initialize the class to set custom settings.

   ```python
    import simple_useragent as sua

    sua.get(num=2, force_cached=True, mobile=True)
    # [UserAgent('Mozilla/5.0 (Android ...'), UserAgent('Mozilla/5.0 (iPhone; ...')]
    sua.get_list()  # Returns a list of 45 or 23 (desktop/mobile) user agents as strings.
    # ['Mozilla/5.0 ...', 'Mozilla/5.0 (iPhone ...', 'Mozilla/5.0 (iPhone ...', ...]
    sua.get_dict()  # Returns a dictionary with all desktop and mobile user agents.
    # {'desktop': ['Mozilla/5.0 ...', ...] 'mobile': ['Mozilla/5.0 (iPhone ...', ...]}
   ```
&nbsp;

#### Advanced Usage

Import the package.
   ```python
    from simple_useragent import UserAgents, get, get_list, get_dict, parse
   ```
&nbsp;

Initialize the class to set custom settings.
   ```python
    user_agents = UserAgents(max_retries=3, timeout=5, cache_duration=86400, cache_location='var/cache/simple-useragent')
   ```
&nbsp;

Fetching User Agents.
   ```python
    # Fetch a specified number of random mobile user agent instances.
    user_agents.get(num=2, shuffle=True, mobile=True)
    # [UserAgent('Mozilla/5.0 (iPhone ...'), UserAgent('Mozilla/5.0 (iPhone; ...')]
   ```  
&nbsp;

You can also use the convenience functions to get user agents without initializing the class.
   ```python
    get(num=2, force_cached=True, mobile=True)
    # [UserAgent('Mozilla/5.0 (Android ...'), UserAgent('Mozilla/5.0 (iPhone; ...')]
    get_list()  # Returns a list of 45 or 23 (desktop/mobile) user agents as strings.
    # ['Mozilla/5.0 ...', 'Mozilla/5.0 (iPhone ...', 'Mozilla/5.0 (iPhone ...', ...]
    get_dict()  # Returns a dictionary with all desktop and mobile user agents.
    # {'desktop': ['Mozilla/5.0 ...', ...] 'mobile': ['Mozilla/5.0 (iPhone ...', ...]}
    
    
   ```
&nbsp;

The instance offers attributes for the user agent properties. You can also parse a custom string directly to the UserAgent class.
   ```python
    obj = parse('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')
    obj.string  # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit ...'
    obj.browser  # 'Chrome', 'Firefox', 'Safari', 'Edge', 'IE', 'Opera', 'Whale', 'QQ Browser', 'Samsung Browser', 'Other'
    obj.browser_version  # '110'
    obj.browser_version_minor  # '0'

    # You can also access the attributes with square brackets.
    obj['os']  # Output: 'Windows', 'macOS', 'Linux', 'Android', 'iOS', 'Other'
    obj['os_version']  # '10'
    obj['os_version_minor']  # '0'
    obj['mobile']  # True / False

   ```
&nbsp;

#### Settings and Parameters

You can set custom settings when initializing the class.

- __max_retries:__ The maximum number of retries to reach the API, before falling back to local cache (default: _3_).
- __timeout:__ The timeout in seconds for the API request (default: _5_).
- __cache_duration:__ The duration in seconds for the user agents to be cached (default: _86400_ = 1 day).
- __cache_location:__ The folder in which the user agents are cached, specific to the OS. You can see the default location with `UserAgents._cache_location`.

&nbsp;

Most functions can take the following parameters:
- __num:__ The number of user agents to fetch (default: _None_ = gets you all user agents available).
- __mobile:__ Fetch mobile or desktop user agents (default: _False_ = desktop).
- __shuffle:__ Whether to shuffle/randomize the order of user agents (default: _False_ = ordered by usage).
- __force_cached:__ Force the use of memory or file cached user agents (default: _None_ = fetches new user agents if cache is outdated, _False_ = always call the API, _True_ = always use the cache).

&nbsp;

> __Notes:__
> 
> - The user agents are cached locally to avoid unnecessary API calls, and are refreshed automatically every 24 hours.
> - During runtime the user agents are stored in memory and written to a cache file for persistence and performance.
> - Every time you invoke a simple-useragent function, it is automatically checked for outdated user agents.

&nbsp;

<!--- Development -->

## Development

As an open-source project, I strive for transparency and collaboration in my development process. I greatly 
appreciate any contributions members of our community can provide. Whether you are fixing bugs, proposing features, 
improving documentation, or spreading awareness - your involvement strengthens the project. Please review the 
[code of conduct](https://github.com/Lennolium/simple-useragent/blob/main/.github/CODE_OF_CONDUCT.md) to understand how we work together 
respectfully.

- __Bug Report:__ If you are experiencing an issue while using the package, please [create an issue](https://github.com/Lennolium/simple-useragent/issues/new/choose).
- __Feature Request:__ Make this project better by [submitting a feature request](https://github.com/Lennolium/simple-useragent/discussions/2).
- __Documentation:__ Improve our documentation by [adding a wiki page](https://github.com/Lennolium/simple-useragent/wiki).
- __Community Support:__ Help others on [GitHub Discussions](https://github.com/Lennolium/simple-useragent/discussions/new/choose).
- __Security Report:__ Report critical security issues via our [template](https://github.com/Lennolium/simple-useragent/blob/main/.github/SECURITY.md).

&nbsp;

<!-- Contributors -->

## Contributors

Thank you so much for giving feedback, implementing features and improving the code and project!

<a href = "https://github.com/Lennolium/simple-useragent/graphs/contributors">
  <img src = "https://contrib.rocks/image?repo=Lennolium/simple-useragent" alt="Contributors"/> 
</a>

&nbsp;

<!--- Credits -->

## Credits

Full credits are in the [acknowledgments](https://github.com/Lennolium/simple-useragent/blob/main/ACKNOWLEDGMENTS) file.

&nbsp;

<!--- License -->

## License

Provided under the terms of the [GNU GPL3 License](https://www.gnu.org/licenses/gpl-3.0.en.html) © Lennart Haack 2024.

See [LICENSE](https://github.com/Lennolium/simple-useragent/blob/main/LICENSE) file for details.
For the licenses of used third party libraries and software, please refer to the [ACKNOWLEDGMENTS](https://github.com/Lennolium/simple-useragent/blob/main/ACKNOWLEDGMENTS) file.

