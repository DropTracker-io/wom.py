# DropTracker fork regression test.
#
# WOM competitions can measure several metrics at once (live on the WOM API
# since 2026-10-07). Responses carry a ``metrics`` array (with weights) and,
# per participant, ``deltas`` broken down by metric; the single ``metric``
# field is deprecated there and slated for removal. Requests send
# ``metrics: [...]`` instead of ``metric``.

from __future__ import annotations

import json
import typing as t
from datetime import datetime
from unittest import mock

import pytest

import wom
from wom import CompetitionService
from wom.serializer import Serializer

_PROGRESS = {"start": 872, "end": 918, "gained": 46}
_UNRANKED = {"start": -1, "end": -1, "gained": 0}

# Trimmed from the live GET /competitions/163803 (2026-11-02).
_MULTI = {
    "id": 163803,
    "title": "Bounty #22 - Nightmare",
    "type": "classic",
    "startsAt": "2026-10-31T18:00:00.000Z",
    "endsAt": "2026-11-07T18:00:00.000Z",
    "groupId": 201,
    "score": 100,
    "visible": True,
    "createdAt": "2026-10-31T17:56:43.051Z",
    "updatedAt": "2026-11-01T10:00:00.000Z",
    "metric": "nightmare",
    "metrics": [
        {"weight": 1, "metric": "nightmare", "createdAt": "2026-10-31T17:56:43.051Z"},
        {"weight": 1, "metric": "phosanis_nightmare", "createdAt": "2026-10-31T17:56:43.051Z"},
    ],
    "participantCount": 1,
    "participations": [
        {
            "playerId": 1,
            "competitionId": 163803,
            "teamName": None,
            "createdAt": "2026-10-31T17:56:43.051Z",
            "updatedAt": "2026-10-31T17:56:43.051Z",
            "player": {
                "id": 1,
                "username": "zezima",
                "displayName": "Zezima",
                "type": "regular",
                "build": "main",
                "status": "active",
                "country": None,
                "patron": False,
                "exp": 0,
                "ehp": 0.0,
                "ehb": 0.0,
                "ttm": 0.0,
                "tt200m": 0.0,
                "registeredAt": "2020-01-01T00:00:00.000Z",
                "updatedAt": "2026-11-01T00:00:00.000Z",
                "lastChangedAt": None,
                "lastImportedAt": None,
            },
            "progress": _PROGRESS,
            "levels": _UNRANKED,
            "deltas": [
                {"metric": "total", "values": _PROGRESS, "levels": _UNRANKED},
                {"metric": "nightmare",
                 "values": {"gained": 0, "start": 476, "end": 476}, "levels": _UNRANKED},
                {"metric": "phosanis_nightmare",
                 "values": {"gained": 46, "start": 396, "end": 442}, "levels": _UNRANKED},
            ],
        }
    ],
}


def _decode(payload: t.Dict[str, t.Any]) -> wom.CompetitionDetail:
    return Serializer().decode(json.dumps(payload).encode(), wom.CompetitionDetail)


def test_multi_metric_detail_decodes() -> None:
    comp = _decode(_MULTI)
    assert comp.metric_values == ["nightmare", "phosanis_nightmare"]
    assert comp.is_multi_metric
    assert comp.metrics[1].weight == 1.0
    part = comp.participations[0]
    assert part.progress.gained == 46
    by_metric = {d.metric: d.values.gained for d in part.deltas}
    assert by_metric == {"total": 46, "nightmare": 0, "phosanis_nightmare": 46}


def test_detail_without_legacy_metric_field_decodes() -> None:
    # WOM plans to drop ``metric``; the decode must not depend on it.
    payload = {k: v for k, v in _MULTI.items() if k != "metric"}
    comp = _decode(payload)
    assert comp.metric is None
    assert comp.metric_values == ["nightmare", "phosanis_nightmare"]


def test_legacy_single_metric_response_decodes() -> None:
    # Pre-2025 shape: no ``metrics`` array, no ``deltas``.
    payload = {k: v for k, v in _MULTI.items() if k != "metrics"}
    payload["participations"] = [
        {k: v for k, v in p.items() if k != "deltas"} for p in _MULTI["participations"]
    ]
    comp = _decode(payload)
    assert comp.metric_values == ["nightmare"]
    assert not comp.is_multi_metric
    assert comp.participations[0].deltas == []


def test_metric_params() -> None:
    params = CompetitionService._metric_params
    assert params(wom.Metric.Zulrah, None) == {"metric": "zulrah"}
    assert params(None, [wom.Metric.Zulrah, "vorkath", "zulrah"]) == {
        "metrics": ["zulrah", "vorkath"]
    }
    # metrics wins over the deprecated single metric.
    assert params(wom.Metric.Zulrah, ["vorkath"]) == {"metrics": ["vorkath"]}
    # A bare string is one metric, not its characters.
    assert params(None, "brand_new_boss") == {"metrics": ["brand_new_boss"]}
    assert params(None, None) == {}
    with pytest.raises(ValueError):
        params(None, None, required=True)
    with pytest.raises(ValueError):
        params(None, [])


@mock.patch("wom.services.base.BaseService._ok_or_err")
async def test_create_competition_sends_metrics(_ok_or_err: mock.Mock) -> None:
    http = mock.Mock()
    http.fetch = mock.AsyncMock(return_value=b"{}")
    service = CompetitionService(http, mock.Mock())
    starts, ends = datetime(2027, 1, 1), datetime(2027, 1, 8)

    await service.create_competition(
        "Nightmare week", None, starts, ends,
        group_id=1, group_verification_code="111-111-111",
        metrics=[wom.Metric.Nightmare, "phosanis_nightmare"],
    )

    payload = http.fetch.await_args.kwargs["payload"]
    assert payload["metrics"] == ["nightmare", "phosanis_nightmare"]
    assert "metric" not in payload

    with pytest.raises(ValueError):
        await service.create_competition("No metric", None, starts, ends)


@mock.patch("wom.services.base.BaseService._ok_or_err")
async def test_edit_competition_sends_metrics(_ok_or_err: mock.Mock) -> None:
    http = mock.Mock()
    http.fetch = mock.AsyncMock(return_value=b"{}")
    service = CompetitionService(http, mock.Mock())

    await service.edit_competition(1, "111-111-111", metrics=["zulrah", "vorkath"])
    assert http.fetch.await_args.kwargs["payload"]["metrics"] == ["zulrah", "vorkath"]

    # Untouched metrics are not sent at all.
    await service.edit_competition(1, "111-111-111", title="Renamed")
    payload = http.fetch.await_args.kwargs["payload"]
    assert "metrics" not in payload and "metric" not in payload
