

class LoginIsRequiredError(Exception):
    """Raises when login is required"""

class EmailIsRequiredError(Exception):
    """Raises when email is required"""

class WaitingCodeTimeExpiredError(Exception):
    """Raises when waiting for code time is expired"""

class SessionKeyMissMatch(Exception):
    """Raises when endpoint key does not match with current"""

class AuthFailedError(Exception):
    """Raises when authenticating was failed"""

class TwoFactorCodeIsRequiredError(Exception):
    """Raises when 2fa is required"""
