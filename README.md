# SimFin Tools

A command line tool to retrieve financial data using SimFin API. This tool provides functionality to download and save various financial datasets including:
- Income Statements (P&L)
- Balance Sheets
- Cash Flow Statements
- Share Data
- Price Data

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd simfin-tools
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your SimFin API key:
Create a `.env` file in the project root and add your SimFin API key:
```bash
SIMFIN_API_KEY=your-api-key-here
```

## Usage

The tool provides several subcommands to retrieve different types of financial data:

### Help
Show available subcommands:
```bash
./sfin.py help
```

### List Companies
List all companies or search for specific ones:
```bash
# List all companies
./sfin.py list

# Search for companies (case-insensitive)
./sfin.py list apple
```

### Full Year Data
Retrieve annual financial data:
```bash
./sfin.py fy AAPL
```
This will create the following files:
- `AAPL_pl.csv`: Annual income statements
- `AAPL_bs.csv`: Annual balance sheets
- `AAPL_cf.csv`: Annual cash flow statements
- `AAPL_shares.csv`: Annual shares data
- `AAPL_price.csv`: Stock prices on fiscal year end dates

### Quarterly Data
Retrieve quarterly financial data:
```bash
./sfin.py q AAPL
```
This will create the following files:
- `AAPL_pl_q1234.csv`: Quarterly income statements
- `AAPL_bs_q1234.csv`: Quarterly balance sheets
- `AAPL_cf_q1234.csv`: Quarterly cash flow statements
- `AAPL_shares_q1234.csv`: Quarterly shares data
- `AAPL_price_q1234.csv`: Stock prices on fiscal quarter end dates

### Trailing Twelve Months (TTM) Data
Retrieve trailing twelve months financial data:
```bash
./sfin.py ttm AAPL
```
This will create the following files:
- `AAPL_pl_ttm.csv`: TTM income statements
- `AAPL_bs_ttm.csv`: TTM balance sheets
- `AAPL_cf_ttm.csv`: TTM cash flow statements
- `AAPL_shares_ttm.csv`: TTM shares data
- `AAPL_price_ttm.csv`: Stock prices on TTM dates

## Output Files

All output files are in CSV format with the following characteristics:
- Comma-separated values
- Text fields are quoted
- Numeric fields are not quoted
- Dates are in YYYY-MM-DD format
- Numbers are formatted with 2 decimal places
- UTF-8 encoding

## Environment Variables

- `SIMFIN_API_KEY`: Your SimFin API key (required)
  - Sign up at [SimFin](https://simfin.com/)
  - Get your API key from your account settings
