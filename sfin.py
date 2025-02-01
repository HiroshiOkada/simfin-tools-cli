#!/usr/bin/env python3
"""
A command line tool to retrieve financial data using simfin.
This tool uses simfin to retrieve annual income statement data for a given ticker.
Usage: python simfin_cli.py AAPL
"""

import simfin as sf
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
        sys.exit(0)
    elif cmd == "income":
        if len(sys.argv) < 3:
            print("Usage: ./sfin.py income <ticker>")
            sys.exit(1)
        ticker = sys.argv[2]
        sf.set_api_key('free')  # free API key provided by SimFin
        sf.set_data_dir('simfin_data')
        try:
            df = sf.get_income(ticker=ticker, variant='annual')
            print(df.head())
        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
    else:
        print(f"Unknown subcommand: {cmd}")
        print("Usage: ./sfin.py <subcommand> [args]")
        sys.exit(1)

if __name__ == "__main__":
    main()
