from ..regression_model import prediction

import pandas as pd

X_test = pd.DataFrame([
  {
    "case": 4,
    "site": 1,
    "Pop": "Vic",
    "sex": "m",
    "hdlngth": 93.5,
    "skullw": 58.0,
    "totlngth": 90.0,
    "taill": 36.5,
    "footlgth": 73.0,
    "earconch": 53.0,
    "eye": 15.0,
    "chest": 28.5,
    "belly": 33.5
  }
])

print(
  prediction(
    model_id="e724abfa-36e9-4e62-bb16-38dba95d7817",
    X_test=X_test
  )
)

