"""Passwords (Argon2id), server-side sessions, CSRF and simple login throttling."""
import hashlib
import re
import secrets
import threading
import time
from collections import defaultdict, deque
from datetime import timedelta

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from backend.config import REMEMBER_ME_DAYS, SESSION_HOURS
from backend.models import now

SESSION_COOKIE = 'hb_session'
CSRF_COOKIE = 'hb_csrf'
CSRF_HEADER = 'X-CSRF-Token'
PASSWORD_MIN, PASSWORD_MAX = 8, 128

_hasher = PasswordHasher()  # argon2-cffi defaults: Argon2id, RFC 9106 low-memory profile


# ---- passwords -------------------------------------------------------------------------------
PASSWORD_RULES = [
    ('length', f'At least {PASSWORD_MIN} characters', lambda p: len(p) >= PASSWORD_MIN),
    ('upper', 'One uppercase letter (A-Z)', lambda p: re.search(r'[A-Z]', p)),
    ('lower', 'One lowercase letter (a-z)', lambda p: re.search(r'[a-z]', p)),
    ('number', 'One number (0-9)', lambda p: re.search(r'\d', p)),
    ('special', 'One special character (e.g. !@#$%)', lambda p: re.search(r'[^A-Za-z0-9]', p)),
]


def password_problems(password):
    if len(password) > PASSWORD_MAX:
        return [f'At most {PASSWORD_MAX} characters']
    return [label for _, label, check in PASSWORD_RULES if not check(password)]


def hash_password(password):
    return _hasher.hash(password)


def verify_password(password_hash, password):
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


# Used to spend similar time when the email does not exist (reduces account enumeration by timing).
_DUMMY_HASH = _hasher.hash('not-a-real-password-Aa1!')


def burn_verify(password):
    verify_password(_DUMMY_HASH, password)


# ---- sessions --------------------------------------------------------------------------------
def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def new_session_values(remember):
    token = secrets.token_urlsafe(32)
    lifetime = timedelta(days=REMEMBER_ME_DAYS) if remember else timedelta(hours=SESSION_HOURS)
    return token, secrets.token_urlsafe(24), now() + lifetime, lifetime


# ---- throttling (in-memory, per process; fine for a single local server) ----------------------
class Throttle:
    def __init__(self, limit, window_seconds):
        self.limit, self.window = limit, window_seconds
        self.hits = defaultdict(deque)
        self.lock = threading.Lock()

    def _trim(self, key, t):
        q = self.hits[key]
        while q and q[0] <= t - self.window:
            q.popleft()
        return q

    def blocked(self, key):
        with self.lock:
            q = self._trim(key, time.monotonic())
            return len(q) >= self.limit

    def retry_after(self, key):
        with self.lock:
            q = self._trim(key, time.monotonic())
            return int(self.window - (time.monotonic() - q[0])) + 1 if q else 0

    def hit(self, key):
        with self.lock:
            self._trim(key, time.monotonic()).append(time.monotonic())

    def reset(self, key):
        with self.lock:
            self.hits.pop(key, None)


login_throttle = Throttle(limit=5, window_seconds=15 * 60)       # failed logins per email+IP
password_throttle = Throttle(limit=5, window_seconds=15 * 60)    # failed password changes per user
signup_throttle = Throttle(limit=10, window_seconds=60 * 60)     # signups per IP
