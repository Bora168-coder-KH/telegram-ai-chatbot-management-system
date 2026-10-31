"""Rate limit, spam detection and content moderation (prototypes, in memory).

  Rate limit   more than RATE_LIMIT messages in RATE_WINDOW seconds -> "please slow down"
  Spam         the same text 3 times in a row within a minute, or many links -> ignored
               after SPAM_STRIKES spam warnings in an hour the user is Suspended
  Moderation   messages with blocked words get a polite refusal and are not routed

Counters live in memory, so they reset when the bot restarts. That is enough for
one bot process; several processes would need a shared store such as Redis.
"""
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from app.services.text import normalize

RATE_LIMIT, RATE_WINDOW = 8, 10.0  # messages per seconds
REPEAT_LIMIT, REPEAT_WINDOW = 3, 60.0
MAX_LINKS = 3
SPAM_STRIKES, STRIKE_WINDOW = 3, 3600.0

URL_RE = re.compile(r"(https?://|www\.|t\.me/)\S+", re.IGNORECASE)
# Small example lists; admins would manage these from the dashboard in a full product.
BLOCKED_WORDS = {
    "en": ["fuck", "shit", "bitch", "kill yourself"],
    "km": ["អាឆ្កែ", "អាឆ្កួត"],
}


@dataclass
class Verdict:
    allowed: bool
    reason: str = ""  # "rate_limit", "spam", "moderation"
    suspend: bool = False  # too many spam strikes
    notify: bool = True  # False: already warned in this window, stay silent


class Guard:
    def __init__(self):
        self.times: dict[int, deque] = defaultdict(deque)
        self.recent: dict[int, deque] = defaultdict(deque)  # (time, normalized text)
        self.strikes: dict[int, deque] = defaultdict(deque)

    def reset(self) -> None:
        self.__init__()

    def _strike(self, user_id: int, now: float) -> bool:
        strikes = self.strikes[user_id]
        strikes.append(now)
        while strikes and now - strikes[0] > STRIKE_WINDOW:
            strikes.popleft()
        return len(strikes) >= SPAM_STRIKES

    def check(self, user_id: int, text: str | None, now: float | None = None) -> Verdict:
        now = time.monotonic() if now is None else now

        times = self.times[user_id]
        times.append(now)
        while times and now - times[0] > RATE_WINDOW:
            times.popleft()
        if len(times) > RATE_LIMIT:
            return Verdict(False, "rate_limit", notify=len(times) == RATE_LIMIT + 1)

        if not text:
            return Verdict(True)
        norm = normalize(text)

        recent = self.recent[user_id]
        recent.append((now, norm))
        while recent and now - recent[0][0] > REPEAT_WINDOW:
            recent.popleft()
        last = [t for _, t in list(recent)[-REPEAT_LIMIT:]]
        repeated = len(last) == REPEAT_LIMIT and len(set(last)) == 1 and len(norm) > 0
        if repeated or len(URL_RE.findall(text)) > MAX_LINKS:
            return Verdict(False, "spam", suspend=self._strike(user_id, now))

        if contains_blocked_word(norm):
            return Verdict(False, "moderation")
        return Verdict(True)


def contains_blocked_word(norm: str) -> bool:
    words = set(norm.split())
    for word in (w for lang in BLOCKED_WORDS.values() for w in lang):
        if (" " in word or not word.isascii()) and word in norm:
            return True
        if word in words:
            return True
    return False


guard = Guard()
