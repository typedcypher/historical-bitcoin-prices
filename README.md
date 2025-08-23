# Historical Bitcoin Prices

![Update daily Bitcoin prices](https://github.com/typedcypher/historical-bitcoin-prices/workflows/Update%20daily%20Bitcoin%20prices/badge.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

Automated daily collection of historical Bitcoin prices in multiple currencies using Kaggle datasets and GitHub Actions.

## Features

- **Multi-Currency Support**: Bitcoin prices in 12 major currencies (USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR, BRL, KRW, MXN)
- **Automated Updates**: Daily price updates via GitHub Actions at 00:00 UTC
- **Historical Data**: Complete historical Bitcoin price data from available sources
- **Forward-Fill Logic**: Handles weekends and holidays by using previous day's exchange rates
- **CSV Output**: Clean, structured data format for easy integration

## Quick Start

### Fork and Configure

1. Fork this repository to your GitHub account
2. Enable GitHub Actions in your forked repository
3. Add the following secrets to your repository (Settings → Secrets and variables → Actions):
   - `KAGGLE_USERNAME`: Your Kaggle username
   - `KAGGLE_KEY`: Your Kaggle API key (get it from [Kaggle Account Settings](https://www.kaggle.com/account))

The workflow will automatically run daily and update the Bitcoin prices in `data/daily_bitcoin_prices.csv`.

## Data Format

The generated CSV file (`data/daily_bitcoin_prices.csv`) contains:

| Column | Description |
|--------|-------------|
| Date | Date in YYYY-MM-DD format |
| BTC_USD | Bitcoin price in US Dollars |
| BTC_EUR | Bitcoin price in Euros |
| BTC_GBP | Bitcoin price in British Pounds |
| BTC_JPY | Bitcoin price in Japanese Yen |
| BTC_CAD | Bitcoin price in Canadian Dollars |
| BTC_AUD | Bitcoin price in Australian Dollars |
| BTC_CHF | Bitcoin price in Swiss Francs |
| BTC_CNY | Bitcoin price in Chinese Yuan |
| BTC_INR | Bitcoin price in Indian Rupees |
| BTC_BRL | Bitcoin price in Brazilian Real |
| BTC_KRW | Bitcoin price in South Korean Won |
| BTC_MXN | Bitcoin price in Mexican Pesos |

Note: JPY and KRW prices are rounded to whole numbers (no decimals), while other currencies use 2 decimal places.

## Manual Usage

### Prerequisites

- Python 3.11+
- Kaggle account with API credentials

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/historical-bitcoin-prices.git
cd historical-bitcoin-prices

# Install dependencies
pip install -r daily_prices/requirements.txt
```

### Running Locally

```bash
# Set Kaggle credentials
export KAGGLE_USERNAME="your_kaggle_username"
export KAGGLE_KEY="your_kaggle_api_key"

# Run the script
cd daily_prices
python generate_bitcoin_prices_kaggle.py
```

The script will download the latest data from Kaggle and generate the CSV file in the `data/` directory.

## GitHub Actions Workflow

The repository includes an automated workflow that:

1. **Runs daily** at 00:00 UTC
2. **Downloads** latest Bitcoin and currency exchange data from Kaggle
3. **Processes** and combines the data for all supported currencies
4. **Commits** updates if prices have changed
5. **Pushes** changes back to the repository

You can also manually trigger the workflow from the Actions tab in your GitHub repository.

## Dependencies

- **pandas** (2.3.2): Data manipulation and analysis
- **numpy** (2.3.2): Numerical operations
- **kagglehub** (>=0.3.12): Kaggle dataset downloads

## Data Sources

This project uses the following Kaggle datasets:

- [Bitcoin Historical Data](https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data) by mczielinski
- [Global Currency Historical Prices](https://www.kaggle.com/datasets/usamabuttar/global-currency-historical-prices-updated-daily) by usamabuttar

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Common Issues

1. **Kaggle Authentication Error**: Ensure your `KAGGLE_USERNAME` and `KAGGLE_KEY` are correctly set
2. **Missing Data**: The script handles missing exchange rates by forward-filling from previous days
3. **GitHub Actions Failing**: Check that your repository secrets are properly configured

### Getting Help

If you encounter issues:
1. Check the GitHub Actions logs for error messages
2. Ensure all dependencies are installed with correct versions
3. Verify your Kaggle API credentials are valid
4. Open an issue in this repository with details about the problem

## Disclaimer

This tool provides historical Bitcoin price data for informational purposes only. It should not be used as the sole basis for investment decisions. Always do your own research and consult with financial advisors when making investment choices.