# SimFin Tools

A command line tool to retrieve financial data using SimFin API. This tool provides functionality to download and save various financial datasets including:
- Income Statements (P&L)
- Balance Sheets
- Cash Flow Statements
- Share Data
- Price Data

## Installation

### Option 1: Install from GitHub (recommended)
```bash
pip install git+https://github.com/HiroshiOkada/simfin-tools-cli.git
```

### Option 2: Install from source
1. Clone the repository:
```bash
git clone https://github.com/HiroshiOkada/simfin-tools-cli.git
cd simfin-tools-cli
```

2. Install the package:
```bash
pip install .
```

### Set up your SimFin API key
Create a `.env` file in your working directory and add your SimFin API key:
```bash
SIMFIN_API_KEY=your-api-key-here
```

## Usage

The tool provides several subcommands to retrieve different types of financial data:

### Help
Show available subcommands:
```bash
sfin help
```

### List Companies
List all companies or search for specific ones:
```bash
# List all companies
sfin list

# Search for companies (case-insensitive)
sfin list apple
```

### Full Year Data
Retrieve annual financial data:
```bash
# CSV output (default)
sfin fy AAPL

# Markdown output
sfin --md fy AAPL
```
This will create either:
- CSV files:
  - `AAPL_pl.csv`: Annual income statements
  - `AAPL_bs.csv`: Annual balance sheets
  - `AAPL_cf.csv`: Annual cash flow statements
  - `AAPL_shares.csv`: Annual shares data
  - `AAPL_price.csv`: Stock prices on fiscal year end dates
- Or a single Markdown file:
  - `AAPL.md`: All data in Markdown tables

### Quarterly Data
Retrieve quarterly financial data:
```bash
# CSV output (default)
sfin q AAPL

# Markdown output
sfin --md q AAPL
```
This will create either:
- CSV files:
  - `AAPL_pl_q1234.csv`: Quarterly income statements
  - `AAPL_bs_q1234.csv`: Quarterly balance sheets
  - `AAPL_cf_q1234.csv`: Quarterly cash flow statements
  - `AAPL_shares_q1234.csv`: Quarterly shares data
  - `AAPL_price_q1234.csv`: Stock prices on fiscal quarter end dates
- Or a single Markdown file:
  - `AAPL_q1234.md`: All data in Markdown tables

### Trailing Twelve Months (TTM) Data
Retrieve trailing twelve months financial data:
```bash
# CSV output (default)
sfin ttm AAPL

# Markdown output
sfin --md ttm AAPL
```
This will create either:
- CSV files:
  - `AAPL_pl_ttm.csv`: TTM income statements
  - `AAPL_bs_ttm.csv`: TTM balance sheets
  - `AAPL_cf_ttm.csv`: TTM cash flow statements
  - `AAPL_shares_ttm.csv`: TTM shares data
  - `AAPL_price_ttm.csv`: Stock prices on TTM dates
- Or a single Markdown file:
  - `AAPL_ttm.md`: All data in Markdown tables

## Output Formats

### CSV Files
- Comma-separated values
- Text fields are quoted
- Numeric fields are not quoted
- Dates are in YYYY-MM-DD format
- Numbers are formatted with 2 decimal places
- UTF-8 encoding

### Markdown Files
- Single file containing all data
- Each dataset in its own section with headers
- Ticker and SimFinId in section headers
- Numbers formatted with:
  - Thousands separators for accounting values (e.g., 1,234,567)
  - 3 decimal places for price values (e.g., 123.456)
- Tables aligned for readability:
  - Left-aligned: Report Date, Date, Fiscal Year, Fiscal Period, Currency
  - Right-aligned: All numeric columns

## Environment Variables

- `SIMFIN_API_KEY`: Your SimFin API key (required)
  - Sign up at [SimFin](https://simfin.com/)
  - Get your API key from your account settings
- `SIMFIN_DATA`: Path to the directory where SimFin data is stored (optional, defaults to `simfin_data`)

### Price Data
Retrieve all available daily price data using the new subcommand:
```bash
# CSV output (default)
sfin price AAPL

# Markdown output
sfin --md price AAPL
```
This will create either:
- A CSV file: 
  - `AAPL_price_all.csv` – All daily price data
- A Markdown file:
  - `AAPL_price_all.md` – All price data in Markdown tables

## Cache Directory

The tool uses a local cache directory (`simfin_data/`) to store downloaded datasets. This:
- Reduces API calls to SimFin servers
- Improves performance for subsequent queries
- Persists data between runs

The cache is automatically:
- Created in the current working directory if it doesn't exist
- Updated when new data is available from SimFin
- Reused when the data is still current

You can safely delete the `simfin_data/` directory if you want to force a fresh download of all datasets.
