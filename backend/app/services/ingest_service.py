import pandas as pd
from typing import List
from datetime import datetime


def _has_value(value) -> bool:
    if value is None:
        return False
    try:
        if pd.isna(value):
            return False
    except Exception:
        pass
    text = str(value).strip().lower()
    return bool(text and text not in {'nan', 'none', 'null'})


def _parse_datetime(val):
    if pd.isna(val):
        return None
    if isinstance(val, datetime):
        return val
    try:
        return pd.to_datetime(val)
    except Exception:
        return None


def normalize_row(row: dict) -> dict:
    # Normalize keys from ServiceNow exports to our defect schema
    lowered = {str(key).strip().lower(): value for key, value in row.items()}

    def get(*names):
        for name in names:
            if name in lowered:
                value = lowered[name]
                if _has_value(value):
                    return value
        return None

    opened_value = get('opened', 'opened at', 'created')
    closed_value = get('closed', 'closed date', 'resolved', 'resolved at')
    state_value = get('state.1', 'state', 'status')
    status_value = str(state_value).strip() if state_value is not None else None
    if closed_value is not None:
        status_value = 'Closed'

    return {
        'defect_id': str(get('number', 'effective number', 'top task', 'task') or '').strip(),
        'short_description': get('short description', 'short_desc', 'title'),
        'description': get('description', 'details'),
        'work_notes': get('work notes', 'comments and work notes', 'comments'),
        'priority': get('priority', 'impact', 'urgency'),
        'sla_due': _parse_datetime(get('sla due', 'sla due date', 'target resolution date')),
        'assignment_group': get('assignment group', 'group assigned', 'service now apps group'),
        'opened_at': _parse_datetime(opened_value),
        'closed_at': _parse_datetime(closed_value),
        'reopen_count': int(get('reopen count') or 0),
        'state': status_value,
        'service_offering': get('service offering', 'service'),
        'business_mapping': get('business mapping', 'business', 'domain'),
        'comments': get('comments and work notes', 'comments'),
        'close_notes': get('close notes'),
        'metadata': {},
    }


def parse_file(file_path: str) -> List[dict]:
    if file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path, dtype=str)
    else:
        df = pd.read_excel(file_path, dtype=str)
    df = df.fillna('')
    records = df.to_dict(orient='records')
    normalized = [normalize_row(r) for r in records if any(_has_value(value) for value in r.values())]
    return normalized
