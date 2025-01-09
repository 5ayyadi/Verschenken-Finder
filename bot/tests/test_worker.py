import pytest
from workers.offer_finder import get_offers

@pytest.mark.parametrize("expected", [True])
def test_get_offers(expected):
    assert get_offers() == expected
