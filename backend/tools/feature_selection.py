import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.feature_selection import RFECV
from sklearn.impute import SimpleImputer
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from sklearn.preprocessing import OrdinalEncoder, LabelEncoder

ID_COLUMN_NAMES = {
  "id",
  "case",
  "index",
  "row",
  "row_id",
  "row_number",
  "record_id",
  "uuid"
}
class CustomTargetPipeline:
  def __init__(
    self,
    max_missing_pct: float = 0.4,
    random_state: int = 42,
    ignored_columns = []
  ):
    self.max_missing_pct = max_missing_pct
    self.random_state = random_state
    self.selectors = {}
    self.results = {}
    self.ignored_columns = {
      str(column).strip().lower().replace(" ", "_")
      for column in (ignored_columns or [])
    }

  def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
      df.columns
      .str.strip()
      .str.lower()
      .str.replace(r"\s+", "_", regex=True)
    )
    return df

  def _is_classification_target(self, y: pd.Series) -> bool:
    if (
      pd.api.types.is_object_dtype(y)
      or isinstance(y.dtype, pd.CategoricalDtype)
      or pd.api.types.is_bool_dtype(y)
    ):
      return True
    if (
      pd.api.types.is_string_dtype(y.dtype)
      or pd.api.types.is_object_dtype(y.dtype)
      or isinstance(y.dtype, pd.CategoricalDtype)
      or pd.api.types.is_bool_dtype(y.dtype)
    ):
      return True
    if pd.api.types.is_integer_dtype(y):
      unique_count = y.nunique()
      unique_ratio = unique_count / len(y)

      return unique_count <= 20 and unique_ratio <= 0.1

    return False

  def _filter_features(self, X: pd.DataFrame) -> pd.DataFrame:
    valid_columns = []

    for column in X.columns:
      normalized_name = column.lower()
      if normalized_name in self.ignored_columns:
        continue

      if (
        normalized_name == "id"
        or normalized_name.endswith("_id")
        or "uuid" in normalized_name
        or normalized_name == "index"
      ):
        continue

      missing_ratio = X[column].isna().mean()

      if missing_ratio > self.max_missing_pct:
        continue

      if X[column].nunique(dropna=True) <= 1:
        continue

      valid_columns.append(column)

    if not valid_columns:
      raise ValueError("No usable feature columns remain after filtering.")

    return X[valid_columns]

  def fit(
    self,
    csv_path: str,
    target_columns: list[str]
  ) -> dict:
    df = self._clean_column_names(pd.read_csv(csv_path))

    cleaned_targets = [
      str(column).strip().lower().replace(" ", "_")
      for column in target_columns
    ]

    missing_targets = [
      column
      for column in cleaned_targets
      if column not in df.columns
    ]

    if missing_targets:
      raise ValueError(
        f"Target columns not found: {missing_targets}"
      )

    results = {}

    for target in cleaned_targets:
      # Do not create artificial target values.
      target_mask = df[target].notna()

      X_raw = df.loc[target_mask].drop(columns=[target])
      y = df.loc[target_mask, target].copy()

      X = self._filter_features(X_raw)

      numeric_columns = X.select_dtypes(
        include=[np.number]
      ).columns.tolist()

      categorical_columns = X.select_dtypes(
        exclude=[np.number]
      ).columns.tolist()

      numeric_pipeline = Pipeline([
        (
          "imputer",
          SimpleImputer(strategy="median")
        )
      ])

      categorical_pipeline = Pipeline([
        (
          "imputer",
          SimpleImputer(strategy="most_frequent")
        ),
        (
          "encoder",
          OrdinalEncoder(
            handle_unknown="use_encoded_value",
            unknown_value=-1
          )
        )
      ])

      preprocessor = ColumnTransformer(
        transformers=[
          (
            "numeric",
            numeric_pipeline,
            numeric_columns
          ),
          (
            "categorical",
            categorical_pipeline,
            categorical_columns
          )
        ],
        verbose_feature_names_out=False
      )

      is_classification = self._is_classification_target(y)

      if is_classification:
        class_counts = y.value_counts()
        smallest_class = int(class_counts.min())

        if smallest_class < 2:
          raise ValueError(
            f"Target '{target}' has a class with fewer than "
            "two samples."
          )

        n_splits = min(5, smallest_class)

        estimator = RandomForestClassifier(
          n_estimators=200,
          random_state=self.random_state,
          n_jobs=-1,
          class_weight="balanced"
        )

        cv = StratifiedKFold(
          n_splits=n_splits,
          shuffle=True,
          random_state=self.random_state
        )

        scoring = "balanced_accuracy"

      else:
        estimator = RandomForestRegressor(
          n_estimators=200,
          random_state=self.random_state,
          n_jobs=-1
        )

        n_splits = min(5, len(y))

        if n_splits < 2:
          raise ValueError(
            f"Target '{target}' has too few valid rows."
          )

        cv = KFold(
          n_splits=n_splits,
          shuffle=True,
          random_state=self.random_state
        )

        scoring = "neg_root_mean_squared_error"

      # Preprocess first so RFECV receives numeric data.
      X_processed = preprocessor.fit_transform(X)

      feature_names = preprocessor.get_feature_names_out()

      selector = RFECV(
        estimator=estimator,
        step=1,
        min_features_to_select=1,
        cv=cv,
        scoring=scoring,
        n_jobs=-1
      )

      selector.fit(X_processed, y)

      selected_features = feature_names[
        selector.support_
      ].tolist()

      self.selectors[target] = {
        "preprocessor": preprocessor,
        "selector": selector
      }

      results[target] = {
        "task_type": (
          "classification"
          if is_classification
          else "regression"
        ),
        "selected_features": selected_features,
        "feature_count": len(selected_features),
        "cv_score": float(
          selector.cv_results_["mean_test_score"][
            selector.n_features_ - 1
          ]
        )
      }

    self.results = results
    return results


pipeline = CustomTargetPipeline(ignored_columns=ID_COLUMN_NAMES)
result = pipeline.fit('/Users/minhquang/Desktop/SS 2026/No-Code-ML-Models-generator/backend/models/possum.csv', ["age", "hdlngth", "sex"])
print(result)