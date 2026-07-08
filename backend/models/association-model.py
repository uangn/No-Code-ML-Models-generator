import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import Ridge


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def encoder(X_train, X_test):
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
    
    # Convert arrays back into dataframes maintaining structural alignment
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

def import_csv(file_path):
    """
    Reads a CSV dataset from a local path or web URL into a structured DataFrame.
    """
    return pd.read_csv(file_path)


def get_x_y(df, target_column):
    """
    get
    """
    X = df.drop(columns=[target_column])
    y = df[[target_column]] # Retained as DataFrame for multi-dimensional scaling step
    return X, y


def train_test_split_custom(X, y, test_size=0.2, random_state=42):
    """
    Partitions data randomly into independent subsets for training and validation.
    """
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def train(X_train, y_train, alpha=1.0):
    """
    Trains a Ridge Regression model. Ridge includes an L2 penalty on weights,
    utilizing the regularization preprocessing applied upstream.
    """
    model = Ridge(alpha=alpha)
    # ravel() converts y column shape from (N, 1) to (N,) flat array required by sklearn
    model.fit(X_train, y_train.ravel())
    return model


def prediction(model, X_test):
    """
    Generates predicted continuous values using the fitted model matrix.
    """
    return model.predict(X_test).reshape(-1, 1)
