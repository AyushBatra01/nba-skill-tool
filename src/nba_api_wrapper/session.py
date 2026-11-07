"""Browser-like transport for stats.nba.com.

NBA.com filters requests using more than HTTP headers. ``curl_cffi`` supplies a
Chrome TLS fingerprint, while the warmup request obtains the Akamai cookies that
a normal visit to the NBA stats site would receive.
"""

from curl_cffi import requests
from nba_api.stats.library.http import NBAStatsHTTP


NBA_STATS_PAGE = "https://www.nba.com/stats/"
_session = None


def configure_nba_session(timeout: int = 30):
    """Install and return the shared browser-like session used by nba_api."""
    global _session
    if _session is None:
        _session = requests.Session(impersonate="chrome")
        NBAStatsHTTP.set_session(_session)
    refresh_nba_session(timeout=timeout)
    return _session


def refresh_nba_session(timeout: int = 30):
    """Refresh NBA.com bot-management cookies on the shared session."""
    if _session is None:
        return configure_nba_session(timeout=timeout)
    response = _session.get(NBA_STATS_PAGE, timeout=timeout)
    response.raise_for_status()
    return _session
