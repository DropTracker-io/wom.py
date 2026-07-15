# DropTracker fork regression test.
#
# WOM adds metrics (new bosses/skills) faster than this pinned client's enum,
# and msgspec strict enum decoding failed the WHOLE response on any unknown
# value. Metric-bearing response fields are now typed ``MetricValue`` (== str),
# so unknown metrics pass through instead of raising. This test uses a metric
# that is deliberately NOT in the enum, so it keeps protecting even when the
# enum is fully up to date.

import wom
from wom.enums import Metric, MetricValue
from wom.models.players.models import SnapshotData
from wom.serializer import Serializer

_UNKNOWN = "definitely_not_a_real_metric_9000"


def test_metricvalue_is_str() -> None:
    assert MetricValue is str
    assert _UNKNOWN not in {m.value for m in Metric}


def test_snapshot_decodes_unknown_metric_without_raising() -> None:
    payload = (
        b'{"skills":{"attack":{"metric":"attack","experience":1,"rank":1,'
        b'"level":1,"ehp":0.0}},'
        b'"bosses":{"' + _UNKNOWN.encode() + b'":{"metric":"' + _UNKNOWN.encode()
        + b'","kills":7,"rank":3,"ehb":0.0}},'
        b'"activities":{},"computed":{}}'
    )
    data = Serializer().decode(payload, SnapshotData)
    # Unknown metric survives as its slug string.
    assert _UNKNOWN in data.bosses
    assert data.bosses[_UNKNOWN].kills == 7
    # Known metrics still index by the enum constant (str hash/eq).
    assert data.skills[Metric.Attack].experience == 1
