import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait as Wait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

import abc

from settings import settings


class Base(metaclass=abc.ABCMeta):

    __slots__ = ('_driver', '_action', '_wait', '_base_timeout',)

    def __init__(self, base_timeout: int = 15, **browsers_params) -> None:
        if 'options' not in browsers_params:
            browsers_params['options'] = settings.set_driver_options((f'user-agent={settings.user_agent}', '--disable-dev-shm-usage'))
        self._driver: WebDriver = uc.Chrome(language='en-US', **browsers_params)
        self._action = ActionChains(self._driver)
        self._base_timeout = base_timeout
        self._wait = Wait(self._driver, self._base_timeout)
        
    def __del__(self) -> None:
        if self._driver:
            self._driver.close()
            self._driver.quit()

    def set_session(self, cookies: list[dict], url: str) -> None:
        self._driver.get(url)
        self._driver.implicitly_wait(self._base_timeout)
        for cookie in cookies:
            self._driver.add_cookie({
                'name': cookie['name'],
                'value': cookie['value'],
                'path': cookie['path'],
                'domain': cookie['domain'],
                'httpOnly': cookie['httpOnly'],
                'secure': cookie['secure'],
                'sameSite': str(cookie['sameSite']),
            })
        self._driver.refresh()

    @abc.abstractmethod
    def sign_up(self, *args, **kwargs) -> ...:
        raise NotImplementedError(
            'Implement me please!'
        )
    
    def find_by_selector(self, selector: str, one: bool = True, timeout: int | None = None) -> WebElement:
        if isinstance(timeout, (int, float)):
            self._wait._timeout = timeout
        if one:
            return self._wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, selector))
        return self._wait.until(lambda driver: driver.find_elements(By.CSS_SELECTOR, selector))
    
