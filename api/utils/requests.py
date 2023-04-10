
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

import time, uuid, re
from typing import TYPE_CHECKING, Callable, NoReturn
from datetime import datetime

from .selectors import FaceBookSelector
from .password import get_password_hash
from utils.errors import (
    EmailIsRequiredError, 
    WaitingCodeTimeExpiredError, 
    AuthFailedError,
    TwoFactorCodeIsRequiredError
)
from settings import settings
from db.redis_db import redis


if TYPE_CHECKING:
    from api.facebook import Facebook


class SignUpRequest:
    
    __slots__ = ('fb', '_login', '_password', '_timeout', 'action_time',)

    def __init__(self, fb: 'Facebook', login: str, password: str, timeout: int = 3, action_time: int = 60*2) -> None:
        self.fb = fb
        self._login = login
        self._password = password
        self._timeout = timeout
        self.action_time = action_time

    def sign_up(self, email_or_code: str | None = None) -> str | dict[str, Callable] | NoReturn:
        driver = self.fb._driver
        # connecting to facebook
        driver.get(self.fb._base_login_url)
        driver.implicitly_wait(self.fb._base_timeout)
        # input login
        self.fb._driver.save_screenshot(settings.path(('png_logs', 'pre-login.png')))
        try:
            accept_cookies = self.fb.find_by_selector(FaceBookSelector.accept_cookies)
        except TimeoutException:
            print('No cookies banner')
        else:
            self.fb._action.move_to_element(accept_cookies).click().perform()
        self.fb._driver.save_screenshot(settings.path(('png_logs', 'after-banner.png')))
        time.sleep(2)
        input_login = self.fb.find_by_selector(FaceBookSelector.input_login)
        self.fb._action.send_keys_to_element(input_login, self._login).perform()
        self.fb._driver.save_screenshot(settings.path(('png_logs', 'after-entering-login.png')))
        time.sleep(2)
        # input password
        input_password = self.fb.find_by_selector(FaceBookSelector.input_password)
        self.fb._action.send_keys_to_element(input_password, self._password + Keys.ENTER).perform()
        self.fb._driver.save_screenshot(settings.path(('png_logs', 'after-entering-password.png')))
        
        driver.implicitly_wait(self._timeout)
        self.fb._driver.save_screenshot(settings.path(('png_logs', 'after-credentials.png')))
        # check is login success
        time.sleep(3)
        if not re.search(r'(?<=\>)Marketplace(?=\<)', driver.page_source):
            try:
                elem = self.fb.find_by_selector(FaceBookSelector.check_login)
                if not elem:
                    try:
                        self.fb.find_by_selector(FaceBookSelector.second_check_login)
                    except TimeoutException:
                        raise TimeoutException
            except TimeoutException:
                if self._check_2fa_needable():
                    if not email_or_code:
                        raise TwoFactorCodeIsRequiredError('Need to enter 2fa')
                    if '@' in email_or_code:
                        raise TwoFactorCodeIsRequiredError('Need to enter 2fa, not email')
                    return self._resolve_2fa(code=email_or_code)
                elif self._check_confirmation():
                    if not email_or_code:
                        raise EmailIsRequiredError('To confirm an account you should set an email')
                    return self._resolve_confirmation(email=email_or_code)
                else:
                    raise AuthFailedError('failed to auth')

        # saving sesison...
        time.sleep(4)
        self.fb._driver.save_screenshot(settings.path(('png_logs', 'to_save.png')))
        key = self.fb.db.add_session_to_account(login=self._login, hashed_password=get_password_hash(self._password), session=driver.get_cookies())

        return key

    def _resolve_2fa(self, code: str | int) -> str:
        input_code = self.fb.find_by_selector(FaceBookSelector.login_code)
        self.fb._action.send_keys_to_element(input_code, str(code)).perform()
        time.sleep(0.2)
        confirm_action = self.fb.find_by_selector(FaceBookSelector.checkpoint_continue)
        self.fb._action.move_to_element(confirm_action).click().perform()
        time.sleep(0.2)
        self.fb._driver.save_screenshot(settings.path(('png_logs', 'starts_resolving_2fa.png')))
        try:
            label = self.fb.find_by_selector('label')
            self.fb._action.move_to_element(label).click().perform()
        except TimeoutException:
            raise AuthFailedError('Failed to set 2fa code or code is invalid')
        self.fb._driver.save_screenshot(settings.path(('png_logs', 'after-label.png')))
        time.sleep(0.2)
        confirm_action = self.fb.find_by_selector(FaceBookSelector.checkpoint_continue)
        self.fb._action.move_to_element(confirm_action).click().perform()
        self.fb._driver.implicitly_wait(self.fb._base_timeout)
        self.fb._driver.save_screenshot(settings.path(('png_logs', 'after-confirming.png')))
        try:
            self.fb.find_by_selector(FaceBookSelector.check_login)
        except TimeoutException:
            self.fb._driver.save_screenshot(settings.path(('png_logs', 'after-error-when-need-confirmation.png')))
            if re.search(r'(?<=\>)Review Recent Login(?=\<)', self.fb._driver.page_source, flags=re.ASCII):
                confirm_action = self.fb.find_by_selector(FaceBookSelector.checkpoint_continue)
                self.fb._action.move_to_element(confirm_action).click().perform()
                self.fb._driver.save_screenshot(settings.path(('png_logs', 'after-confirmation.png')))
                time.sleep(1.5)
                submit = self.fb.find_by_selector(FaceBookSelector.submin_login)
                self.fb._action.move_to_element(submit).click().perform()
                self.fb._driver.save_screenshot(settings.path(('png_logs', 'after-submiting.png')))
                try:
                    label = self.fb.find_by_selector('label')
                    self.fb._action.move_to_element(label).click().perform()
                except TimeoutException:
                    raise AuthFailedError('Failed to set 2fa code or code is invalid')
                self.fb._driver.save_screenshot(settings.path(('png_logs', 'after-label2.png')))
                confirm_action = self.fb.find_by_selector(FaceBookSelector.checkpoint_continue)
                self.fb._action.move_to_element(confirm_action).click().perform()
                time.sleep(1)
                try:
                    self.fb.find_by_selector(FaceBookSelector.check_login)
                except TimeoutException:
                    raise AuthFailedError('Failed to set 2fa code or code is invalid')
                self.fb._driver.save_screenshot(settings.path(('png_logs', 'after-confirming-everyting.png')))
            else:
                raise AuthFailedError('Failed to set 2fa code or code is invalid')
        self.fb._driver.implicitly_wait(self.fb._base_timeout)
        time.sleep(2)
        key = self.fb.db.add_session_to_account(login=self._login, hashed_password=get_password_hash(self._password), session=self.fb._driver.get_cookies())
        return key        

    def _check_2fa_needable(self) -> bool:
        try:
            self.fb.find_by_selector(FaceBookSelector.login_code, timeout=self._timeout)
        except TimeoutException:
            return False
        return True

    def _confirming(self, text: str) -> None:
        continuing_btns = self.fb.find_by_selector(FaceBookSelector.continuing_btn, one=False, timeout=25)
        for btn in continuing_btns:
            time.sleep(0.1)
            if btn.text.strip() == text:
                self.fb._action.move_to_element(btn).click().perform()
                return
    
    def _resolve_confirmation(self, email: str) -> dict[str, Callable]:
        def second_step() -> str:
            start_time = datetime.now().timestamp()
            try:
                while True:
                    code = redis.get_single(session_key)
                    current_time = datetime.now().timestamp()
                    if (current_time - start_time) >= self.action_time:
                        raise WaitingCodeTimeExpiredError('Time to wait code is expired')
                    if code and code != 'false':
                        break
                    time.sleep(5)
                if not is_number:
                    send_code = self.fb.find_by_selector(FaceBookSelector.verify_code)
                    self.fb._action.send_keys_to_element(send_code, code[session_key]).perform()
                    self._confirming('Next')
                self.fb._action.send_keys_to_element(send_number, code[session_key]).perform()
                confirm_action = self.fb.find_by_selector(FaceBookSelector.checkpoint_continue)
                self.fb._action.move_to_element(confirm_action).click().perform()
                time.sleep(0.5)
                
                self.fb._driver.implicitly_wait(self.fb._base_timeout)
                try:
                    self.fb.find_by_selector(FaceBookSelector.check_login, timeout=self._timeout)
                except TimeoutException:
                    raise AuthFailedError('Failed to confirm account')
            finally:
                redis.delete(session_key)
            key = self.fb.db.add_session_to_account(login=self._login, hashed_password=get_password_hash(self._password), session=self.fb._driver.get_cookies())
            return key

        confirm_action = self.fb.find_by_selector(FaceBookSelector.checkpoint_continue)
        self.fb._action.move_to_element(confirm_action).click().perform()
        # check is label occurred
        try:
            label = self.fb.find_by_selector('label')
            self.fb._action.move_to_element(label).click().perform()
        except TimeoutException:
            raise AuthFailedError('Failed to confirm account')
        confirm_action = self.fb.find_by_selector(FaceBookSelector.checkpoint_continue)
        self.fb._action.move_to_element(confirm_action).click().perform()
        is_number = True
        try:
            send_number = self.fb.find_by_selector(FaceBookSelector.set_number, timeout=self._timeout)
        except TimeoutException:
            is_number = False
            self._confirming('Upload ID')
            time.sleep(0.5)
            self._confirming('Next')
            time.sleep(0.5)
            enter_email = self.fb.find_by_selector(FaceBookSelector.enter_email) 
            self.fb._action.send_keys_to_element(enter_email, email).perform()
            confirm_email = self.fb.find_by_selector(FaceBookSelector.confirm_email)
            self.fb._action.send_keys_to_element(confirm_email, email).perform()
            time.sleep(0.5)
            self._confirming('Send')
        else:
            try:
                label = self.fb.find_by_selector('label')
                self.fb._action.move_to_element(label).click().perform()
            except TimeoutException:
                raise AuthFailedError('Failed to confirm account')
            time.sleep(0.5)
            confirm_action = self.fb.find_by_selector(FaceBookSelector.checkpoint_continue)
            self.fb._action.move_to_element(confirm_action).click().perform()

        session_key = str(uuid.uuid4())
        redis.set_single(key=session_key, value='false')
       
        return {'second_step_key': session_key, 'second_step': second_step}
            
    def _check_confirmation(self) -> bool:
        try:
            self.fb.find_by_selector(FaceBookSelector.checkpoint_form, timeout=self._timeout)
        except TimeoutException:
            return False
        return True
