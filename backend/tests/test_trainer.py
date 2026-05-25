import pandas as pd
import importlib.util
import pathlib

# Load trainer module directly to avoid package import side-effects during tests
trainer_path = pathlib.Path(__file__).resolve().parents[1] / 'app' / 'ml' / 'trainer.py'
spec = importlib.util.spec_from_file_location('ml_trainer', str(trainer_path))
trainer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trainer)


def test_feature_engineer():
    df = pd.DataFrame([{'opened_at':'2020-01-01','short_description':'a','description':'b','reopen_count':0,'priority':'2 - High'}])
    out = trainer._feature_engineer(df)
    assert 'age_days' in out.columns
