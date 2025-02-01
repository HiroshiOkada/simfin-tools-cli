#!/usr/bin/env python3
"""
A command line tool to retrieve financial data using simfin.
This tool uses simfin to retrieve annual income statement data for a given ticker.
Usage: python simfin_cli.py AAPL
"""

import simfin as sf
import os
from dotenv import load_dotenv
load_dotenv()
import argparse

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: ./sfin.py <subcommand> [args]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "help":
        print("Usage: ./sfin.py <subcommand> [args]")
        print("Subcommands:")
        print("  help    Show this help message")
        print("  income  Retrieve annual income statement data for a given ticker")
        print("  list    Retrieve list of companies; if parameter provided, only those whose names contain the search term (case-insensitive)")
        sys.exit(0)
    elif cmd == "income":
        if len(sys.argv) < 3:
            print("Usage: ./sfin.py income <ticker>")
            sys.exit(1)
        ticker = sys.argv[2]
        sf.set_api_key(os.environ["SIMFIN_API_KEY"])  # API key loaded from .env file
        sf.set_data_dir('simfin_data')
        try:
            df = sf.get_income(ticker=ticker, variant='annual')
            print(df.head())
        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
    elif cmd == "list":
        sf.set_api_key(os.environ["SIMFIN_API_KEY"])
        sf.set_data_dir('simfin_data')
        try:
            # Load companies data
            companies = sf.load_companies()
            search_term = sys.argv[2].lower() if len(sys.argv) > 2 else ""
            
            if search_term:
                # Handle NaN values in the search
                mask = companies['Company Name'].str.lower().str.contains(search_term, na=False)
                companies = companies[mask]
            
            if companies.empty:
                print(f"No companies found matching '{search_term}'")
            else:
                # Display results with ticker as index and company name
                result = companies[['Company Name']].copy()
                result.columns = ['Name']  # Rename column for display
                print(result)
        except Exception as e:
            print(f"Error retrieving companies list: {e}")
    else:
        print(f"Unknown subcommand: {cmd}")
        print("Usage: ./sfin.py <subcommand> [args]")
        sys.exit(1)

if __name__ == "__main__":
    main()
