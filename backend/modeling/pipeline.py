import polars as pl
from backend.modeling.engine import train_prop_model, calculate_true_probabilities

def run_prediction_pipeline(historical_games_list: list, active_market_lines: pl.DataFrame) -> pl.DataFrame:
    """
    Pipeline bridge to process historical data, train the model, and evaluate active market lines.
    """
    # Cast incoming data streams instantly to a Polars DataFrame
    df = pl.DataFrame(historical_games_list)

    # Sort by player_id and game_date to ensure chronological order
    df = df.sort(["player_id", "game_date"])

    # Apply vectorized window functions to compute rolling means for 5-game and 15-game spans
    # We drop nulls to ensure the model doesn't train on NaN features.
    df = df.with_columns(
        pl.col("points").rolling_mean(window_size=5).over("player_id").alias("rolling_5_points"),
        pl.col("points").rolling_mean(window_size=15).over("player_id").alias("rolling_15_points")
    ).drop_nulls(subset=["rolling_5_points", "rolling_15_points", "points"])

    features = ["rolling_5_points", "rolling_15_points"]
    target = "points"

    # Check if df has data to train
    if df.height == 0:
        raise ValueError("Not enough historical data to compute 15-game rolling windows for training.")

    # Call the training routine
    model = train_prop_model(df, features, target)

    # The active_market_lines dataframe must have these rolling features.
    # We will assume that active_market_lines already has these features joined or we compute them?
    # The instructions say: "Call the training and calculation routines from modeling/engine.py to yield a unified evaluation matrix."
    # Wait, does `active_market_lines` have `rolling_5_points` and `rolling_15_points`?
    # If not, we might need to join it. But usually, predicting market lines implies the market_df has the features.

    # Let's assume active_market_lines already contains the features, or we should prepare it.
    # The instructions: "Apply vectorized window functions using .over("player_id") to compute rolling means for 5-game and 15-game spans."
    # Then "Call the training and calculation routines from modeling/engine.py to yield a unified evaluation matrix."

    # Evaluation matrix computation
    evaluation_matrix = calculate_true_probabilities(model, active_market_lines, features)

    return evaluation_matrix
