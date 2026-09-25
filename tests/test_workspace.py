import pandas as pd
from workspace_helpers import normalize_country, metric_mask, resolve_page


def test_country_aliases_merge_without_inventing_missing_locations():
    assert {normalize_country(x) for x in ['USA', ' United State ', 'United States', 'us']} == {'United States'}
    assert normalize_country('BD') == 'Bangladesh'
    assert normalize_country('Phillipines') == 'Philippines'
    for value in [None, float('nan'), 'Unknown', 'ALL', 'Global', 'n/a', '4200']:
        assert normalize_country(value) == ''
    assert normalize_country('South Africa') == 'South Africa'


def test_default_filters_keep_unknown_metrics_but_explicit_limits_do_not():
    frame = pd.DataFrame({'_dr_num': [None, 0, 65, 75], '_price_num': [None, 0, 150, 500]})
    assert metric_mask(frame).tolist() == [True, True, True, True]
    assert metric_mask(frame, min_dr=60).tolist() == [False, False, True, True]
    assert metric_mask(frame, max_price=200).tolist() == [False, True, True, False]
    assert metric_mask(frame, min_dr=60, max_price=200).tolist() == [False, False, True, False]


def test_deep_links_allow_only_known_pages():
    assert resolve_page('search') == 'Search Websites'
    assert resolve_page('saved') == 'Favorites'
    assert resolve_page('outreach') == 'Outreach Generator'
    assert resolve_page('Private Contacts') == 'Private Contacts'
    assert resolve_page('../private') == 'Dashboard'
