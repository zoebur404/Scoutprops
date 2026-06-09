import polars as pl
import xgboost as xgb
import numpy as np
import scipy.stats

def train_prop_model(data: pl.DataFrame, features: list[str], target: str) -> xgb.Booster:
    """
    Trains an XGBoost count model using Poisson regression to predict the expected value (lambda).
    """
    # Convert Polars columns to native NumPy arrays
    X = data.select(features).to_numpy()
    y = data.select(target).to_numpy().ravel()

    # Create XGBoost DMatrix
    dtrain = xgb.DMatrix(X, label=y, feature_names=features)

    # Set XGBoost parameters
    params = {
        'objective': 'count:poisson',
        'eval_metric': 'poisson-nloglik',
        'max_delta_step': 0.7,
        'eta': 0.05
    }

    num_boost_round = 150

    # Train model
    model = xgb.train(params, dtrain, num_boost_round=num_boost_round)

    return model

def calculate_true_probabilities(model: xgb.Booster, market_df: pl.DataFrame, features: list[str]) -> pl.DataFrame:
    """
    Calculates the true probabilities for over and under using the trained model
    and the Poisson survival function.
    """
    # Generate continuous lambda distributions
    X_market = market_df.select(features).to_numpy()
    dmarket = xgb.DMatrix(X_market, feature_names=features)
    lambdas = model.predict(dmarket)

    # Get the line thresholds
    lines = market_df.get_column("line_threshold").to_numpy()

    # Calculate exact discrete survival probabilities for 'true_prob_over'
    # scipy.stats.poisson.sf computes P(X > k)
    true_prob_over = scipy.stats.poisson.sf(np.floor(lines).astype(int), lambdas)
    true_prob_under = 1.0 - true_prob_over

    # Return original dataframe with appended columns
    return market_df.with_columns(
        pl.Series("predicted_lambda", lambdas),
        pl.Series("true_prob_over", true_prob_over),
        pl.Series("true_prob_under", true_prob_under)
    )
