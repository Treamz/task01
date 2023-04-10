import time, uuid, re
from typing import Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from .base import Base
# from .utils.password import get_password_hash
from .utils.selectors import FaceBookSelector
from db.connection import DatabaseConnection
from utils.errors import LoginIsRequiredError
from .utils.requests import SignUpRequest
from settings import settings




class Facebook(Base):

    __slots__ = ('_base_login_url', 'db', '_cookies', '_key',)

    def __init__(self, key: str | None, **browsers_params) -> None:
        super().__init__(**browsers_params)
        self._key = key
        self._base_login_url = 'https://www.facebook.com/login'
        self.db = DatabaseConnection()
        self._cookies = None
        if self._key:
            self._cookies = self.db.get_session(key=self._key)

    @property
    def cookies(self) -> list[dict]:
        return self._cookies

    def sign_up(self, login: str, password: str, email: str | None = None) -> str | None | dict[str, Callable]:
        request = SignUpRequest(self, login=login, password=password)
        return request.sign_up(email)
        
    def get_apps_id(self, base_url: str = 'https://developers.facebook.com/apps/?show_reminder=true') -> list[int] | None:
        self.set_session(self._cookies, url=base_url)
        try:
            app_ids = self.find_by_selector(FaceBookSelector.app_id, one=False)
        except TimeoutException:
            raise LoginIsRequiredError('Apps doesnt exists or login is required')
        ids = []
        for app_id in app_ids:
            if app_id.get_attribute('value').isnumeric():
                ids.append(int(app_id.get_attribute('value')))
                
        return ids

    def _is_acc_added(self, added_accs: list[str]) -> bool:
        self._driver.execute_script('document.querySelector("body").scrollIntoView(0);')
        self._driver.implicitly_wait(self._base_timeout)
        try:
            all_ids = self.find_by_selector(FaceBookSelector.check_accs, one=False)
        except TimeoutException:
            return False
        if not all_ids:
            return False
        count = 0
        for _id in all_ids:
            if count == len(added_accs):
                return True
            if _id.text.strip() in tuple(map(str, added_accs)):
                count += 1
        if count == len(added_accs):
            return True
        return False
    
    def _is_acc_deleted(self, deleted_accs: list[str]) -> bool:
        self._driver.execute_script('document.querySelector("body").scrollIntoView(0);')
        self._driver.implicitly_wait(self._base_timeout)
        try:
            all_ids = self.find_by_selector(FaceBookSelector.check_accs, one=False)
        except TimeoutException:
            return True
        if not all_ids:
            return True
        for _id in all_ids:
            if _id.text.strip() in tuple(map(str, deleted_accs)):
                return False

        return True

    def add_accounts_id(self, accs: list[str | int], app_id: int | str) -> bool:
        url = f'https://developers.facebook.com/apps/{app_id}/settings/advanced/'
        self.set_session(self._cookies, url=url)
        try:
            form = self.find_by_selector(FaceBookSelector.input_accounts)
        except TimeoutException:
            raise LoginIsRequiredError('Login is required')
        self._driver.execute_script('document.querySelector("body").scrollIntoView(0);')
        for elem in form.find_elements(By.CSS_SELECTOR, 'div'):
            if 'Authorized ad account IDs' in elem.text.strip():
                input_accounts = elem.find_element(By.CSS_SELECTOR, 'input')
                break
        for acc in accs:
            self._action.send_keys_to_element(input_accounts, str(acc) + Keys.ENTER).perform()
            time.sleep(0.01)
        time.sleep(0.5)
        save_changes = self.find_by_selector(FaceBookSelector.save_changes_button)
        self._action.move_to_element(save_changes).click().perform()
        time.sleep(3)

        return self._is_acc_added(added_accs=accs)
    
    def delete_accounts_id(self, accs: list[str | int], app_id: int | str) -> bool:
        url = f'https://developers.facebook.com/apps/{app_id}/settings/advanced/'
        self.set_session(self._cookies, url=url)
        time.sleep(1)
        self._driver.save_screenshot(settings.path(('png_logs', '1-del.png')))
        # self._driver.execute_script('document.querySelector("body").scrollIntoView(0);')
        try:
            all_ids = self.find_by_selector(FaceBookSelector.check_accs, one=False)
        except TimeoutException:
            raise LoginIsRequiredError('Login is required')
        self._driver.save_screenshot(settings.path(('png_logs', '2-del.png')))
        if not all_ids:
            return False
    
        flag = True
        deleted_count = 0
        to_delete_tuple = tuple(map(str, accs))
        scroll = 0
        while flag:
            if scroll == 1500:
                scroll = -1
            self._driver.execute_script(f'window.scroll(0, {scroll});')
            for _id in all_ids:
                if _id.text.strip() in to_delete_tuple:
                    to_del = _id.find_element(By.CSS_SELECTOR, FaceBookSelector.element_to_delete)
                    self._action.move_to_element(to_del).click().perform()
                    time.sleep(0.01)
            all_ids = self.find_by_selector(FaceBookSelector.check_accs, one=False)
            if not all_ids:
                flag = False
            for _id in to_delete_tuple:
                if not re.search(fr'(?<=\>){_id}(?=\<)', self._driver.page_source):
                    deleted_count += 1
            if deleted_count == len(to_delete_tuple):
                flag = False
            else:
                deleted_count = 0
            scroll += 500
            
        self._driver.save_screenshot(settings.path(('png_logs', '3-del.png')))
        time.sleep(0.5)
        save_changes = self.find_by_selector(FaceBookSelector.save_changes_button)
        self._action.move_to_element(save_changes).click().perform()
        time.sleep(3)
        self._driver.save_screenshot(settings.path(('png_logs', '4-del.png')))

        return self._is_acc_deleted(deleted_accs=accs)
    
    def get_app_accounts(self, app_id: str | int) -> list[str | int]:
        url = f'https://developers.facebook.com/apps/{app_id}/settings/advanced/'
        self.set_session(self._cookies, url=url)
        self._driver.execute_script('document.querySelector("body").scrollIntoView(0);')
        try:
            all_ids = self.find_by_selector(FaceBookSelector.check_accs, one=False)
        except TimeoutException:
            return False
        if not all_ids:
            return False
        
        return [int(app_id) for _id in all_ids if (app_id := _id.text.strip()) and app_id.isnumeric()]
