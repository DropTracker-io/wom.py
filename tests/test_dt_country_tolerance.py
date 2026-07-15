# DropTracker fork regression test.
#
# WOM's API emits country codes this pinned client's ``Country`` enum does not
# know — notably subdivision codes like ``GB_ENG`` (England) — and msgspec
# strict enum decoding failed the WHOLE response on any unknown value, breaking
# group member sync for any group containing such a player. The player
# ``country`` field is now typed ``CountryValue`` (== str), so unknown codes
# pass through instead of raising. This test decodes a player whose country is
# deliberately NOT in the enum, so it keeps protecting even as the enum grows.

from wom.models.players.enums import Country
from wom.models.players.enums import CountryValue
from wom.models.players.models import Player
from wom.serializer import Serializer

_UNKNOWN = "GB_ENG"


def test_countryvalue_is_str() -> None:
    assert CountryValue is str
    # The test only means something while GB_ENG is genuinely unknown.
    assert _UNKNOWN not in {c.value for c in Country}


def test_player_decodes_unknown_country_without_raising() -> None:
    payload = (
        b'{"id":1,"username":"test","displayName":"Test","type":"regular",'
        b'"build":"main","country":"' + _UNKNOWN.encode() + b'","status":"active",'
        b'"exp":1,"ehp":0.0,"ehb":0.0,"ttm":0.0,"tt200m":0.0,'
        b'"registeredAt":"2020-01-01T00:00:00.000Z","updatedAt":null,'
        b'"lastChangedAt":null,"lastImportedAt":null}'
    )
    player = Serializer().decode(payload, Player)
    # Unknown/subdivision country survives as its raw string.
    assert player.country == _UNKNOWN
    assert isinstance(player.country, str)
