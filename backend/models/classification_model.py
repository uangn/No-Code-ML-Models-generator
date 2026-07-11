import json
import uuid
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
import os

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

DB_PATH = "/Users/minhquang/Desktop/SS 2026/No-Code-ML-Models-generator/backend/database/mock_modelDB.json"


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def encode(X_train, X_test):
  categorical_cols = X_train.select_dtypes(include=["object", "category"]).columns.tolist()

  if not categorical_cols:
    return X_train, X_test, None

  enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")

  X_train_encoded = enc.fit_transform(X_train[categorical_cols])
  X_test_encoded = enc.transform(X_test[categorical_cols])

  encoded_cols = enc.get_feature_names_out(categorical_cols)

  X_train_enc_df = pd.DataFrame(
    X_train_encoded,
    columns=encoded_cols,
    index=X_train.index
  )

  X_test_enc_df = pd.DataFrame(
    X_test_encoded,
    columns=encoded_cols,
    index=X_test.index
  )

  X_train_final = pd.concat(
    [X_train.drop(columns=categorical_cols), X_train_enc_df],
    axis=1
  )

  X_test_final = pd.concat(
    [X_test.drop(columns=categorical_cols), X_test_enc_df],
    axis=1
  )

  return X_train_final, X_test_final, enc


def scale_X(X_train, X_test):
  scaler_X = StandardScaler()

  X_train_scaled = scaler_X.fit_transform(X_train)
  X_test_scaled = scaler_X.transform(X_test)

  return X_train_scaled, X_test_scaled, scaler_X


def save_model_to_db(data):
  os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

  if os.path.exists(DB_PATH):
    with open(DB_PATH, "r") as f:
      try:
        db = json.load(f)
      except json.JSONDecodeError:
        db = []
  else:
    db = []

  db.append(data)

  with open(DB_PATH, "w") as f:
    json.dump(db, f, indent=2)


# ==========================================
# CLASSIFICATION FUNCTIONS
# ==========================================

def train(csv_file, target_x_columns, target_y_columns,
                     need_scale=False, need_encode=False):
  """
  Train a Logistic Regression classification model and save it.
  """

  df = pd.read_csv(csv_file)
  df.dropna(inplace=True)

  X = df[target_x_columns]
  y = df[target_y_columns]

  X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=np.ravel(y) if len(np.unique(np.ravel(y))) > 1 else None
  )

  encoder = None
  scaler_X = None

  if need_encode:
    X_train, X_test, encoder = encode(X_train, X_test)

  if need_scale:
    X_train, X_test, scaler_X = scale_X(X_train, X_test)

  model = LogisticRegression(max_iter=1000)
  model.fit(X_train, np.ravel(y_train))

  model_id = str(uuid.uuid4())
  model_path = os.path.join(MODEL_DIR, f"{model_id}.pkl")

  joblib.dump(
    {
      "model": model,
      "encoder": encoder,
      "scaler_X": scaler_X,
      "feature_columns": target_x_columns,
      "target_columns": target_y_columns,
      "need_encode": need_encode,
      "need_scale": need_scale,
      "task_type": "classification",
    },
    model_path
  )

  data = {
    "model_id": model_id,
    "model_path": model_path,
    "need_encode": need_encode,
    "need_scale": need_scale,
    "task_type": "classification",
    "feature_columns": target_x_columns,
    "target_columns": target_y_columns,
  }

  save_model_to_db(data)

  print(f"Created classification ML at {model_path}")

  return data


def prediction(model_id, X_test):
  """
  Generate class predictions using a saved classification model.
  """

  model_path = os.path.join(MODEL_DIR, f"{model_id}.pkl")
  bundle = joblib.load(model_path)

  model = bundle["model"]
  encoder = bundle["encoder"]
  scaler_X = bundle["scaler_X"]

  X = X_test.copy()

  if encoder is not None:
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()

    X_encoded = encoder.transform(X[categorical_cols])
    encoded_cols = encoder.get_feature_names_out(categorical_cols)

    X_encoded = pd.DataFrame(
      X_encoded,
      columns=encoded_cols,
      index=X.index
    )

    X = pd.concat(
      [X.drop(columns=categorical_cols), X_encoded],
      axis=1
    )

  if scaler_X is not None:
    X = scaler_X.transform(X)

  y_pred = model.predict(X)

  return y_pred.tolist()