#!/usr/bin/env python3
"""
A command line tool to retrieve financial data using simfin.
This tool uses simfin to retrieve annual income statement data for a given ticker.
Usage: python simfin_cli.py AAPL
"""

import simfin as sf
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Retrieve financial data from SimFin"
    )
    parser.add_argument("ticker", help="Ticker to fetch data for (e.g., AAPL)")
    args = parser.parse_args()
    
    # Configure simfin with a free API key and local data directory
    sf.set_api_key('free')  # free API key provided by SimFin
    sf.set_data_dir('simfin_data')

    try:
        # Retrieve annual income statement data for the given ticker
        df = sf.get_income(ticker=args.ticker, variant='annual')
        print(df.head())
    except Exception as e:
        print(f"Error retrieving data for {args.ticker}: {e}")

if __name__ == "__main__":
    main()
