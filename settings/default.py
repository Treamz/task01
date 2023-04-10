import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from pydantic import BaseSettings

import os, subprocess
from pathlib import Path
from utils.user_agent import get_latest_useragent



class Settings(BaseSettings):
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent # base root_dir and join. Clear work with Posix paths or any unix-like
    db_name: str = 'session.db'
    browser_headless = False
    port: int = 8002
    user_agent: str = get_latest_useragent()
    
    def __init__(self, module: BaseSettings = None, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        if module:
            self.__dict__.update(**module().__dict__)

    def path(self, *paths, base_path: str | Path | None = None) -> str:
        # str type joining to clear work with WindowsPath or any
        if not base_path:
            base_path = self.ROOT_DIR
        resolved = []
        for path in paths:
            if isinstance(path, (list, tuple)):
                resolved.extend(path)
            else:
                resolved.append(path)

        return os.path.join(base_path, *resolved)

    @property
    def db_path(self) -> str:
        os.makedirs(self.path('.session'), exist_ok=True)
        return self.path(('.session', self.db_name))

    @staticmethod
    def get_browser_version() -> str:
        if os.name == 'nt':
            version = subprocess.check_output('''powershell -command "&{(Get-Item '%s').VersionInfo.ProductVersion}"''' % uc.find_chrome_executable())
        else:
            version = subprocess.check_output('google-chrome --version | grep -iE "[0-9.]{10,20}"')

        return version.decode(encoding='utf-8').strip()

    def set_driver_options(self, *arguments: tuple) -> Options:
        options = Options()
        resolved = []
        for path in arguments:
            if isinstance(path, (list, tuple)):
                resolved.extend(path)
            else:
                resolved.append(path)
        for argument in resolved:
            options.add_argument(argument)
        
        return options
