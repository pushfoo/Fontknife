from unittest.mock import Mock


def test_uses_lru_cache_to_replace_cache(monkeypatch):

    # Setup fake lru cache
    mock_lru_cache = Mock(return_value=lambda a: a)
    monkeypatch.setattr('fontknife.utils._lru_cache', mock_lru_cache)

    # Import cache & 'decorate' the function
    from fontknife.utils import cache

    @cache
    def increment(a) -> int:
        return a + 1

    mock_lru_cache.assert_called_with(maxsize=None)
    assert increment(0) == 1
