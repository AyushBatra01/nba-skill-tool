from src.nba_api_wrapper import session as nba_session


class FakeResponse:
    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.requests = []

    def get(self, url, timeout):
        self.requests.append((url, timeout))
        return FakeResponse()


def test_browser_session_is_warmed_and_installed(monkeypatch):
    fake = FakeSession()
    installed = []
    monkeypatch.setattr(nba_session, "_session", None)
    monkeypatch.setattr(nba_session.requests, "Session", lambda **kwargs: fake)
    monkeypatch.setattr(nba_session.NBAStatsHTTP, "set_session", installed.append)

    result = nba_session.configure_nba_session(timeout=12)

    assert result is fake
    assert installed == [fake]
    assert fake.requests == [(nba_session.NBA_STATS_PAGE, 12)]
