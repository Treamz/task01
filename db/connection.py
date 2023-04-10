import uuid

from sqlmodel import (
    select,
    update,
    delete,
)

from .core import get_session, Session as db_Session
from models.core import Account, Session


class DatabaseConnection:

    def __init__(self, session: db_Session | None = None) -> None:
        self._session = session if session else next(get_session())


    def _delete_existing_account(self, login: str) -> bool:
        qs = select(Account).where(Account.login==login)
        result = self._session.execute(qs).one_or_none()
        if not result:
            return False
        qs = delete(Session).where(Session.account_id==result.Account.id)
        self._session.execute(qs)
        qs = delete(Account).where(Account.login==login)
        self._session.execute(qs)
        self._session.commit()
        return True
        
    def check_session_exists(self, login: str) -> bool:
        qs = select(Account).where(Account.login==login)
        result = self._session.execute(qs).one_or_none()
        if not result:
            return False
            
        return True

    def add_session_to_account(self, login: str, hashed_password: str, session: list[dict]) -> str:
        self._delete_existing_account(login=login)
        account = Account(login=login, password=hashed_password, login_key=str(uuid.uuid4()))
        self._session.add(account)
        self._session.commit()
        self._session.refresh(account)
        instances = []
        for _dict in session:
            instances.append(Session(account_id=account.id, **_dict))
        self._session.add_all(instances=instances)
        self._session.commit()

        return account.login_key
    
    def get_session(self, key: str) -> list[dict] | None:
        qs = select(
            Session.name,
            Session.value,
            Session.path, 
            Session.httpOnly,
            Session.sameSite,
            Session.domain,
            Session.secure,
            Session.expiry
            ).join(Account, Session.account_id==Account.id)\
            .where(Account.login_key==key)
        result = self._session.execute(qs)
        if result:
            session = []
            for data in result:
                name, value, path, httpOnly, sameSite, domain, secure, expiry = data
                session.append({
                    'name': name,
                    'value': value,
                    'path': path,
                    'httpOnly': httpOnly,
                    'sameSite': sameSite,
                    'domain': domain,
                    'secure': secure, 
                    'expiry': expiry,
                })
            return session

