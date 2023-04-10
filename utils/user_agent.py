import requests
from bs4 import BeautifulSoup as BS

import sys
from random import choice



def get_random_useragent() -> str:
    """Getting random useragent at start"""
    user_agents_list = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    )  

    return choice(user_agents_list)


def get_latest_useragent() -> str:
        """
        Returns:
            str: Trying to get the latest useragent for your browser
            
        It's can be useful if site has cloudflare and checks your platform with useragent
        and compare it. But it may be not enough, check on cookies as well.
        Also it's just a way to get it faster. Better use selenium/any instead
        """
        
        linux_ua = 'Mozilla/5.0 (X11; Linux x86_64)'
        windows_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        response = requests.get('https://www.whatismybrowser.com/guides/the-latest-user-agent/windows')
        data = BS(response.content, 'lxml').select('table > tbody > tr')
        new_ua = None
        for col in data:
            chrome = col.select_one('td > b')
            if chrome and chrome.get_text(strip=True).lower() == 'chrome':
                ua = col.select_one('span.code')
                if ua:
                    new_ua = ua.get_text(strip=True)
                    break
        if new_ua:
            new_data = new_ua.split(')', 1)[-1]
            
            match sys.platform:
                case 'win32':
                    new_ua = f'{windows_ua}{new_data}'
                case 'linux' | 'linux2':
                    new_ua = f'{linux_ua}{new_data}'
                case _:
                    raise Exception(f'This function expected Linux or Windows platform, not {sys.platform}')
        
            return new_ua
            
        return get_random_useragent()
