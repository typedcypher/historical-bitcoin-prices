#!/usr/bin/env python3
"""
Generate historical Bitcoin prices in multiple currencies using Kaggle datasets.
Limited to the 12 currencies supported by the Living on Bitcoin app.
"""

import pandas as pd
import os
from datetime import datetime
import sys
import kagglehub

# Define the supported currencies from the app
SUPPORTED_CURRENCIES = [
    "USD",
    "EUR",
    "GBP",
    "JPY",
    "CAD",
    "AUD",
    "CHF",
    "CNY",
    "INR",
    "BRL",
    "KRW",
    "MXN",
]


def setup_kaggle_credentials():
    """Setup Kaggle API credentials from environment variables."""
    username = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")

    if not username or not key:
        print("Error: KAGGLE_USERNAME and KAGGLE_KEY environment variables must be set")
        print("Please export these variables or create a .env file")
        sys.exit(1)

    # Kagglehub will automatically use these environment variables
    print("Kaggle credentials configured from environment variables")


def load_bitcoin_data_from_kaggle():
    """Load Bitcoin price data from Kaggle dataset."""
    print("Loading Bitcoin data from Kaggle...")

    try:
        # Download the Bitcoin dataset
        dataset_path = kagglehub.dataset_download("mczielinski/bitcoin-historical-data")
        bitcoin_file = os.path.join(dataset_path, "btcusd_1-min_data.csv")

        if not os.path.exists(bitcoin_file):
            print(f"Error: Bitcoin data file not found at {bitcoin_file}")
            sys.exit(1)

        print(f"  Reading Bitcoin data from {bitcoin_file}")
        df = pd.read_csv(bitcoin_file)

        # Convert timestamp (Unix timestamp) to datetime
        if "Timestamp" in df.columns:
            df["Date"] = pd.to_datetime(df["Timestamp"], unit="s")
        elif "timestamp" in df.columns:
            df["Date"] = pd.to_datetime(df["timestamp"], unit="s")
        else:
            print("Error: No timestamp column found in Bitcoin data")
            sys.exit(1)

        # Filter to only midnight (00:00:00) data - one price per day
        df["DateOnly"] = df["Date"].dt.date
        df = df.groupby("DateOnly").first().reset_index()
        df["Date"] = pd.to_datetime(df["DateOnly"])
        df = df.drop("DateOnly", axis=1)

        # Find the close column (case-insensitive)
        close_col = None
        for col in df.columns:
            if "close" in col.lower():
                close_col = col
                break

        if close_col is None:
            print(
                "Warning: No 'Close' column found, using 'Open' or first numeric column"
            )
            for col in df.columns:
                if df[col].dtype in ["float64", "int64"] and col != "Date":
                    close_col = col
                    break

        # Keep only Date and Close columns
        df = df[["Date", close_col]].rename(columns={close_col: "BTC_USD"})

        # Sort by date
        df = df.sort_values("Date")

        print(
            f"  Loaded {len(df)} Bitcoin price records from {df['Date'].min().date()} to {df['Date'].max().date()}"
        )
        return df

    except Exception as e:
        print(f"Error loading Bitcoin data from Kaggle: {e}")
        sys.exit(1)


def load_currency_data_from_kaggle():
    """Load currency exchange rate data from Kaggle dataset."""
    print("Loading currency data from Kaggle...")

    currency_dataframes = {}

    # Mapping of currency codes to file names in the dataset
    currency_files = {
        "EUR": "EUR_European-Euro.csv",
        "GBP": "GBP_Pound-Sterling.csv",
        "JPY": "JPY_Japanese-Yen.csv",
        "CAD": "CAD_Canadian-Dollar.csv",
        "AUD": "AUD_Australian-Dollar.csv",
        "CHF": "CHF_Swiss-Franc.csv",
        "CNY": "CNY_Chinese-Yuan-Renminbi.csv",
        "INR": "INR_Indian-Rupee.csv",
        "BRL": "BRL_Brazilian-Real.csv",
        "KRW": "KRW_South-Korean-Won.csv",
        "MXN": "MXN_Mexican-Peso.csv",
    }

    try:
        # Download the currency dataset
        dataset_path = kagglehub.dataset_download(
            "usamabuttar/global-currency-historical-prices-updated-daily"
        )
        print(f"  Currency dataset downloaded to: {dataset_path}")

        # Files are in the Price-Data subdirectory
        price_data_path = os.path.join(dataset_path, "Price-Data")

        for currency_code, filename in currency_files.items():
            try:
                currency_file = os.path.join(price_data_path, filename)

                if not os.path.exists(currency_file):
                    print(
                        f"  Warning: {currency_code} file not found at {currency_file}"
                    )
                    continue

                print(f"  Loading {currency_code} data from {filename}...")
                df = pd.read_csv(currency_file)

                # Process the dataframe
                processed_df = process_currency_dataframe(df, currency_code)
                if processed_df is not None:
                    currency_dataframes[currency_code] = processed_df

            except Exception as e:
                print(f"  Error loading {currency_code}: {e}")
                continue

    except Exception as e:
        print(f"Error downloading currency dataset: {e}")

    return currency_dataframes


def process_currency_dataframe(df, currency_code):
    """Process a currency dataframe to standard format."""
    try:
        # Skip the first two header rows if they exist
        if len(df) > 2 and df.iloc[0, 0] == "Ticker:":
            df = df.iloc[2:]

        # Reset column names
        if len(df.columns) >= 2:
            df.columns = ["Date", "Close"] + list(df.columns[2:])

        # Convert Date to datetime
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Convert Close to numeric
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

        # Keep only Date and Close columns
        df = df[["Date", "Close"]].rename(columns={"Close": f"{currency_code}_Rate"})

        # Remove any rows with NaN values
        df = df.dropna()

        # Sort by date
        df = df.sort_values("Date")

        print(f"    Processed {len(df)} {currency_code} exchange rate records")
        return df

    except Exception as e:
        print(f"    Error processing {currency_code}: {e}")
        return None


def calculate_bitcoin_prices(bitcoin_df, currency_df, currency_code):
    """Calculate Bitcoin prices in a specific currency with forward-fill for missing data."""
    # Sort both dataframes by date
    currency_df = currency_df.sort_values("Date")

    # Merge with left join to keep all Bitcoin dates
    merged = pd.merge(bitcoin_df, currency_df, on="Date", how="left")

    # Forward-fill missing exchange rates (use previous day's rate for weekends/holidays)
    merged[f"{currency_code}_Rate"] = merged[f"{currency_code}_Rate"].ffill()

    # Backward-fill any remaining NaN values at the beginning if needed
    merged[f"{currency_code}_Rate"] = merged[f"{currency_code}_Rate"].bfill()

    # Calculate Bitcoin price in the currency
    merged[f"BTC_{currency_code}"] = merged["BTC_USD"] * merged[f"{currency_code}_Rate"]

    # Keep only Date and BTC price columns
    result = merged[["Date", f"BTC_{currency_code}"]]

    # Count how many values were filled vs actual data
    filled_count = merged[f"{currency_code}_Rate"].isna().sum()
    total_count = len(result)
    actual_data = total_count - filled_count

    print(
        f"  Calculated {total_count} Bitcoin prices in {currency_code} ({actual_data} with actual rates)"
    )
    return result


def main():
    # Setup Kaggle credentials
    setup_kaggle_credentials()

    # Define output path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(base_dir, "../data/daily_bitcoin_prices.csv")

    # Load Bitcoin data from Kaggle
    bitcoin_df = load_bitcoin_data_from_kaggle()

    # Start with Bitcoin USD prices
    result_df = bitcoin_df.copy()

    # Load currency data from Kaggle
    currency_dataframes = load_currency_data_from_kaggle()

    # Process each supported currency
    print("\nProcessing currencies...")
    for currency_code in SUPPORTED_CURRENCIES:
        if currency_code == "USD":
            # USD is already in the base data
            continue

        if (
            currency_code not in currency_dataframes
            or currency_dataframes[currency_code] is None
        ):
            print(f"  Skipping {currency_code} - no data available")
            continue

        # Calculate Bitcoin prices in this currency
        currency_prices = calculate_bitcoin_prices(
            bitcoin_df, currency_dataframes[currency_code], currency_code
        )

        # Merge with result dataframe
        result_df = pd.merge(result_df, currency_prices, on="Date", how="left")

    # Round all numeric columns to 2 decimal places (except JPY and KRW which don't use decimals)
    for col in result_df.columns:
        if col != "Date" and "BTC_" in col:
            if "JPY" in col or "KRW" in col:
                # No decimals for JPY and KRW
                result_df[col] = result_df[col].round(0)
            else:
                result_df[col] = result_df[col].round(2)

    # Sort by date (newest first to match the original Bitcoin data format)
    result_df = result_df.sort_values("Date", ascending=False)

    # Format date as YYYY-MM-DD
    result_df["Date"] = result_df["Date"].dt.strftime("%Y-%m-%d")

    # Save to CSV
    print(f"\nSaving results to {output_file}...")
    result_df.to_csv(output_file, index=False)

    # Print summary
    print(f"\nSuccess! Generated {output_file}")
    print(f"Total records: {len(result_df)}")
    print(f"Date range: {result_df['Date'].min()} to {result_df['Date'].max()}")
    print(
        f"Currencies included: {', '.join([col.replace('BTC_', '') for col in result_df.columns if 'BTC_' in col])}"
    )

    # Show first few rows
    print("\nFirst 5 rows of output:")
    print(result_df.head().to_string())


if __name__ == "__main__":
    main()
