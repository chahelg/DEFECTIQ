import pytest
from app.services.ingest_service import normalize_row


def test_normalize_row_basic():
    row = {'sys_id':'1','short_desc':'Short','description':'Desc','opened_at':'2020-01-01'}
    out = normalize_row(row)
    assert out['defect_id'] == '1'
    assert 'short' in out['short_description'].lower()
