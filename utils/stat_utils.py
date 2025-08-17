from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.preprocessing import StandardScaler
from pandas import Series


def coefficient_of_variation_continuous_data(
    data: Series, min_mean=1e-6, max_cv=10, verbose=0
):
    """Calculate coefficient of variation (cv) for a continuous series data.
    Always >=0, maybe larger than 1 for highly skewed distributions.

    Args: data: Series from Dataframe
    """
    mean = data.mean()
    std = data.std(ddof=1)  # Sample standard deviation
    if std == 0:
        if verbose:
            logger.debug(f"{std = } is Zero")
        return 0.0
    # Use coefficient of variation only when mean is sufficiently large and cv is within limits
    # Otherwise, use normalized standard deviation based on data range
    if abs(mean) > min_mean and abs(std / mean) < max_cv:
        cv = abs(std / mean)
    else:
        if verbose:
            logger.debug(
                f"{mean = }, {std = }, use normalized standard deviation based on data range"
            )
        data_range = data.max() - data.min()
        if data_range > 0:
            cv = std / data_range
        else:
            cv = 0.0
    return cv


def coefficient_of_variation_categorical_data(data: Series, verbose=0):
    """Calculate coefficient of variation (cv) for a categorical series data.
    For categorical: use normalized entropy, always between 0 and 1.

    Args: data: Series from Dataframe
    """
    # Get the counts of each category
    value_counts = data.value_counts(normalize=True)
    if value_counts.sum() == 0 or len(value_counts) <= 1:
        return 0.0
    entropy = -sum(p * np.log(p) for p in value_counts if p > 0)
    # normalize is must to keep the value is between 0 and 1
    cv = entropy / np.log(len(value_counts))
    if verbose:
        logger.debug(
            f"{value_counts = }, {len(value_counts) = }, {np.log(len(value_counts)) = }, {entropy = }, {cv = }"
        )
    return cv


def test_coefficient_of_variation_continuous(verbose=0):
    df1 = pd.DataFrame({"values": [10, 12, 11, 0, -13, -8, -12]})
    df2 = pd.DataFrame({"values": [100, 1200, 11000, 0, 13, 8, 1]})
    dfs = [df1, df2]
    for df in dfs:
        cv = coefficient_of_variation_continuous_data(df["values"], verbose)
        logger.info(f"Coefficient of Variation: {cv:.2f}")

        scaler = StandardScaler()
        scaled_df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
        cv = coefficient_of_variation_continuous_data(scaled_df["values"], verbose)
        logger.info(f"Coefficient of Variation (scaled): {cv:.2f}")


def test_coefficient_of_variation_categorical(verbose=0):
    df1 = pd.DataFrame({"category": ["A", "B", "A", "B", "A", "B", "B", "A"]})
    df2 = pd.DataFrame({"category": ["A", "A", "A", "A", "A", "A", "A", "A"]})
    dfs = [df1, df2]
    for df in dfs:
        df["category"] = df["category"].astype("category")
        df["category"] = df["category"].cat.codes.replace(-1, np.nan)

        scaler = StandardScaler()
        scaled_df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
        if verbose:
            logger.info(f"{df = }\n{scaled_df = }")
        cv = coefficient_of_variation_categorical_data(scaled_df["category"], verbose)
        logger.info(f"Coefficient of Variation (categorical): {cv:.2f}")


if __name__ == "__main__":
    test_coefficient_of_variation_continuous(verbose=1)
    test_coefficient_of_variation_categorical(verbose=1)
