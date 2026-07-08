import json
import uuid
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
import os

MODEL_DIR = "models"


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def encode(X_train, X_test):
  """
  Finds categorical text features, transforms them into binary columns (one-hot),
  and stitches them back together with the original numerical features.
  """
  # Identify text or categorical columns
  categorical_cols = X_train.select_dtypes(include=['object', 'category']).columns.tolist()
  
  # If no categorical columns exist, return original frames unchanged
  if not categorical_cols:
      return X_train, X_test, None
      
  # Instantiate OneHotEncoder (handles unseen test categories gracefully)
  enc = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
  
  # Fit on training data, transform both partitions
  X_train_encoded = enc.fit_transform(X_train[categorical_cols])
  X_test_encoded = enc.transform(X_test[categorical_cols])
  
  # Generate meaningful binary column labels
  encoded_cols = enc.get_feature_names_out(categorical_cols)
  
  # Convert arrays back int o dataframes maintaining structural alignment
  X_train_enc_df = pd.DataFrame(X_train_encoded, columns=encoded_cols, index=X_train.index)
  X_test_enc_df = pd.DataFrame(X_test_encoded, columns=encoded_cols, index=X_test.index)
  
  # Drop raw categorical strings and append numerical columns to new encoded features
  X_train_final = pd.concat([X_train.drop(columns=categorical_cols), X_train_enc_df], axis=1)
  X_test_final = pd.concat([X_test.drop(columns=categorical_cols), X_test_enc_df], axis=1)
  
  return X_train_final, X_test_final, enc


def regularize(X_train, X_test, y_train, y_test):
  """
  Standardizes features and targets by scaling to zero mean and unit variance.
  Crucial for regularized models like Ridge/Lasso to prevent feature scale bias.
  """
  scaler_X = StandardScaler()
  scaler_y = StandardScaler()
  
  # Fit and scale training partitions, transform test partitions
  X_train_scaled = scaler_X.fit_transform(X_train)
  X_test_scaled = scaler_X.transform(X_test)
  
  y_train_scaled = scaler_y.fit_transform(y_train)
  y_test_scaled = scaler_y.transform(y_test)
  
  return X_train_scaled, X_test_scaled, y_train_scaled, y_test_scaled, scaler_X, scaler_y


def re_transform(y_pred_scaled, scaler_y):
    """
    Reverts standardized target predictions back to their original physical units.
    """
    return scaler_y.inverse_transform(y_pred_scaled)


# ==========================================
# MAIN CORE FUNCTIONS
# ==========================================


def train(csv_file, target_x_columns, target_y_columns,
          need_scale=False, need_encode=False):
  """
  Train a Linear Regression model and save it.

  Returns
  -------
  dict
      {
        "model_id": "...",
        "model_path": "...",
      }
  """

  df = pd.read_csv(csv_file)
  df.dropna(inplace=True)

  X = df[target_x_columns]
  y = df[target_y_columns]
  
  X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
  )

  encoder = None
  scaler_X = None
  scaler_y = None

  if need_encode:
    X_train, X_test, encoder = encode(X_train, X_test)

  if need_scale:
    X_train, X_test, y_train, y_test, scaler_X, scaler_y = regularize(
      X_train, X_test, y_train, y_test
    )

  model = LinearRegression()
  model.fit(X_train, np.ravel(y_train))

  model_id = str(uuid.uuid4())
  model_path = os.path.join(MODEL_DIR, f"{model_id}.pkl")

  joblib.dump(
    {
      "model": model,
      "encoder": encoder,
      "scaler_X": scaler_X,
      "scaler_y": scaler_y,
      "feature_columns": target_x_columns,
      "target_columns": target_y_columns,
      "need_encode": need_encode,
      "need_scale": need_scale,
    },
    model_path
  )
  print(f"Created ML at {model_path}")
  
  data = {
    "model_id": model_id,
    "model_path": model_path,
    "need_encode": need_encode,
    "need_scale": need_scale,
  }
  DB_PATH = "/Users/minhquang/Desktop/SS 2026/No-Code-ML-Models-generator/backend/database/mock_modelDB.json"
  # Load existing database
  if os.path.exists(DB_PATH):
    with open(DB_PATH, "r") as f:
      try:
        db = json.load(f)
      except json.JSONDecodeError:
        db = []
  else:
    db = []
  # Append new model
  db.append(data)

  # Save back to file
  with open(DB_PATH, "w") as f:
    json.dump(db, f, indent=2)
  return {
    "model_id": model_id,
    "model_path": model_path,
    "need_encode": need_encode,
    "need_scale": need_scale,
  }


def prediction(model_id, X_test):
  """
  Generate predictions using a previously trained regression model.

  Parameters
  ----------
  model_id : str
      Identifier of the trained model.
  X_test : pandas.DataFrame
      Input feature data.

  Returns
  -------
  numpy.ndarray
      Predicted values.
  """

  model_path = os.path.join(MODEL_DIR, f"{model_id}.pkl")

  bundle = joblib.load(model_path)

  model = bundle["model"]
  encoder = bundle["encoder"]
  scaler_X = bundle["scaler_X"]
  scaler_y = bundle["scaler_y"]

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

  y_pred = model.predict(X).reshape(-1, 1)

  if scaler_y is not None:
    y_pred = scaler_y.inverse_transform(y_pred)

  return y_pred