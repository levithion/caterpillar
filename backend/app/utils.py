import math

import pandas as pd


def _clean(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def records(df: pd.DataFrame) -> list[dict]:
    # `df.where(df.notnull(), None)` looks like the obvious way to swap NaN
    # for JSON-safe None, but it silently fails to do so for some
    # object-dtype columns depending on pandas version, so a row with any
    # missing value (e.g. an operator with no certifications) crashes
    # response serialization. Clean each value directly instead.
    return [{k: _clean(v) for k, v in row.items()} for row in df.to_dict(orient="records")]
