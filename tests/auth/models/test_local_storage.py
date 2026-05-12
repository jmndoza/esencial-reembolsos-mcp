import json

from esencial.auth.models import LocalStorage


def test_parses_dd_session_directly():
    ls = LocalStorage.model_validate({"ddSession": "abc"})
    assert ls.dd_session == "abc"


def test_parses_omnitok_affiliate_json_string():
    ls = LocalStorage.model_validate({"omnitok-affiliate": json.dumps({"rut": "12345678-9"})})
    assert ls.omnitok_affiliate is not None
    assert ls.omnitok_affiliate.rut == "12345678-9"


def test_parses_selected_affiliate_json_string():
    ls = LocalStorage.model_validate({"SELECTED_AFFILIATE": json.dumps({"rutPar": "98765432-1"})})
    assert ls.selected_affiliate is not None
    assert ls.selected_affiliate.rutPar == "98765432-1"


def test_invalid_json_in_field_results_in_none():
    ls = LocalStorage.model_validate({"omnitok-affiliate": "not-valid-json"})
    assert ls.omnitok_affiliate is None


def test_ignores_unknown_localstorage_keys():
    ls = LocalStorage.model_validate({"some-other-key": "value", "ddSession": "x"})
    assert ls.dd_session == "x"


def test_affiliate_rut_prefers_omnitok_over_selected():
    ls = LocalStorage.model_validate(
        {
            "omnitok-affiliate": json.dumps({"rut": "primary"}),
            "SELECTED_AFFILIATE": json.dumps({"rutPar": "fallback"}),
        }
    )
    assert ls.affiliate_rut == "primary"


def test_affiliate_rut_falls_back_to_selected_when_omnitok_missing():
    ls = LocalStorage.model_validate(
        {
            "SELECTED_AFFILIATE": json.dumps({"rutPar": "fallback"}),
        }
    )
    assert ls.affiliate_rut == "fallback"


def test_affiliate_rut_is_none_when_no_source_present():
    ls = LocalStorage.model_validate({})
    assert ls.affiliate_rut is None
