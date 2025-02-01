#!/usr/bin/env python3
"""
A command line tool to retrieve financial data using simfin.
This tool provides functionality to:
- List and search companies
- Retrieve full year financial data (P&L, Balance Sheet, Cash Flow, etc.)
Usage: python sfin.py <subcommand> [args]
"""

import simfin as sf
import os
import pandas as pd
import csv
from dotenv import load_dotenv
load_dotenv()
import argparse

def save_dataframe(df, filename, index=True):
    """Helper function to save dataframes with consistent formatting"""
    df.to_csv(filename, 
              sep=',',
              index=index,
              float_format='%.2f',
              encoding='utf-8',
              quoting=csv.QUOTE_NONNUMERIC,
              doublequote=True)

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
        print("  fy      Retrieve full year financial data (P&L, Balance Sheet, Cash Flow, etc.) for a given ticker")
        print("  q       Retrieve quarterly financial data (P&L, Balance Sheet, Cash Flow, etc.) for a given ticker")
        print("  ttm     Retrieve trailing twelve months financial data (P&L, Balance Sheet, Cash Flow, etc.) for a given ticker")
        print("  list    Retrieve list of companies; if parameter provided, only those whose names contain the search term (case-insensitive)")
        sys.exit(0)
    elif cmd == "fy":
        if len(sys.argv) < 3:
            print("Usage: ./sfin.py fy <ticker>")
            sys.exit(1)
        ticker = sys.argv[2]
        sf.set_api_key(os.environ["SIMFIN_API_KEY"])
        sf.set_data_dir('simfin_data')
        try:
            saved_files = []
            
            try:
                # Load and save P&L data
                pl = sf.load_income(variant='annual')
                pl = pl[pl.index.get_level_values('Ticker') == ticker]
                if not pl.empty:
                    # Format numbers without scientific notation
                    pl = pl.round(2)
                    # Clean up column names
                    pl.columns = [col.strip() for col in pl.columns]
                    pl.index.names = [name.strip() for name in pl.index.names]
                    save_dataframe(pl, f"{ticker}_pl.csv")
                    saved_files.append("pl")
            except Exception as e:
                print(f"Warning: Could not load P&L data: {str(e)}")

            try:
                # Load and save Balance Sheet data
                bs = sf.load_balance(variant='annual')
                bs = bs[bs.index.get_level_values('Ticker') == ticker]
                if not bs.empty:
                    bs = bs.round(2)
                    bs.columns = [col.strip() for col in bs.columns]
                    bs.index.names = [name.strip() for name in bs.index.names]
                    save_dataframe(bs, f"{ticker}_bs.csv")
                    saved_files.append("bs")
            except Exception as e:
                print(f"Warning: Could not load Balance Sheet data: {str(e)}")

            try:
                # Load and save Cash Flow data
                cf = sf.load_cashflow(variant='annual')
                cf = cf[cf.index.get_level_values('Ticker') == ticker]
                if not cf.empty:
                    cf = cf.round(2)
                    cf.columns = [col.strip() for col in cf.columns]
                    cf.index.names = [name.strip() for name in cf.index.names]
                    save_dataframe(cf, f"{ticker}_cf.csv")
                    saved_files.append("cf")
            except Exception as e:
                print(f"Warning: Could not load Cash Flow data: {str(e)}")

            try:
                # Load and save Derived data
                derived = sf.load_derived(variant='annual')
                derived = derived[derived.index.get_level_values('Ticker') == ticker]
                if not derived.empty:
                    derived = derived.round(2)
                    derived.columns = [col.strip() for col in derived.columns]
                    derived.index.names = [name.strip() for name in derived.index.names]
                    save_dataframe(derived, f"{ticker}_derived.csv")
                    saved_files.append("derived")
            except Exception as e:
                print(f"Warning: Could not load Derived data: {str(e)}")

            try:
                # Extract shares data from income statement
                if 'pl' in saved_files:
                    # Get the exact column names from the P&L data that contain 'Shares'
                    shares_cols = [col for col in pl.columns if 'Shares' in col]
                    if len(shares_cols) >= 2:
                        shares_data = pl[shares_cols[:2]]  # Take first two shares columns
                        shares_data.columns = ['Common Shares Outstanding', 'Weighted Average Shares']
                        shares_data = shares_data.round(2)
                        shares_data.columns = [col.strip() for col in shares_data.columns]
                        shares_data.index.names = [name.strip() for name in shares_data.index.names]
                        save_dataframe(shares_data, f"{ticker}_shares.csv")
                        saved_files.append("shares")
            except Exception as e:
                print(f"Warning: Could not extract shares data: {str(e)}")

            try:
                # Load and save historical Price data
                if 'pl' in saved_files:
                    # Get fiscal year end dates from P&L data
                    fiscal_dates = pl.index.get_level_values('Report Date').unique()
                    
                    # Load daily share prices
                    prices = sf.load_shareprices(variant='daily')
                    prices = prices[prices.index.get_level_values('Ticker') == ticker]
                    
                    if not prices.empty:
                        # Get price data for each fiscal year end date
                        price_data = []
                        for date in fiscal_dates:
                            # Get the price on the fiscal year end date or the closest previous date
                            mask = prices.index.get_level_values('Date') <= date
                            if mask.any():
                                closest_date = prices[mask].index.get_level_values('Date').max()
                                price_row = prices[prices.index.get_level_values('Date') == closest_date]
                                if not price_row.empty:
                                    price_data.append(price_row)
                        
                        if price_data:
                            # Combine all price data
                            price_data = pd.concat(price_data)
                            # Get available columns for price data
                            price_columns = [col for col in ['Close', 'Adj. Close'] if col in price_data.columns]
                            if price_columns:
                                price_data = price_data[price_columns]
                                price_data = price_data.round(2)
                                price_data.columns = [col.strip() for col in price_data.columns]
                                price_data.index.names = [name.strip() for name in price_data.index.names]
                                save_dataframe(price_data, f"{ticker}_price.csv")
                                saved_files.append("price")
            except Exception as e:
                print(f"Warning: Could not load Price data: {str(e)}")

            if not saved_files:
                print(f"No data could be saved for {ticker}")
                sys.exit(1)
            else:
                print(f"Successfully saved the following datasets for {ticker}: {', '.join(saved_files)}")

        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
            sys.exit(1)

    elif cmd == "q":
        if len(sys.argv) < 3:
            print("Usage: ./sfin.py q <ticker>")
            sys.exit(1)
        ticker = sys.argv[2]
        sf.set_api_key(os.environ["SIMFIN_API_KEY"])
        sf.set_data_dir('simfin_data')
        try:
            saved_files = []
            
            try:
                # Load and save P&L data
                pl = sf.load_income(variant='quarterly')
                pl = pl[pl.index.get_level_values('Ticker') == ticker]
                if not pl.empty:
                    # Format numbers without scientific notation
                    pl = pl.round(2)
                    # Clean up column names
                    pl.columns = [col.strip() for col in pl.columns]
                    pl.index.names = [name.strip() for name in pl.index.names]
                    save_dataframe(pl, f"{ticker}_pl_q1234.csv")
                    saved_files.append("pl")
            except Exception as e:
                print(f"Warning: Could not load P&L data: {str(e)}")

            try:
                # Load and save Balance Sheet data
                bs = sf.load_balance(variant='quarterly')
                bs = bs[bs.index.get_level_values('Ticker') == ticker]
                if not bs.empty:
                    bs = bs.round(2)
                    bs.columns = [col.strip() for col in bs.columns]
                    bs.index.names = [name.strip() for name in bs.index.names]
                    save_dataframe(bs, f"{ticker}_bs_q1234.csv")
                    saved_files.append("bs")
            except Exception as e:
                print(f"Warning: Could not load Balance Sheet data: {str(e)}")

            try:
                # Load and save Cash Flow data
                cf = sf.load_cashflow(variant='quarterly')
                cf = cf[cf.index.get_level_values('Ticker') == ticker]
                if not cf.empty:
                    cf = cf.round(2)
                    cf.columns = [col.strip() for col in cf.columns]
                    cf.index.names = [name.strip() for name in cf.index.names]
                    save_dataframe(cf, f"{ticker}_cf_q1234.csv")
                    saved_files.append("cf")
            except Exception as e:
                print(f"Warning: Could not load Cash Flow data: {str(e)}")

            try:
                # Load and save Derived data
                derived = sf.load_derived(variant='quarterly')
                derived = derived[derived.index.get_level_values('Ticker') == ticker]
                if not derived.empty:
                    derived = derived.round(2)
                    derived.columns = [col.strip() for col in derived.columns]
                    derived.index.names = [name.strip() for name in derived.index.names]
                    save_dataframe(derived, f"{ticker}_derived_q1234.csv")
                    saved_files.append("derived")
            except Exception as e:
                print(f"Warning: Could not load Derived data: {str(e)}")

            try:
                # Extract shares data from income statement
                if 'pl' in saved_files:
                    # Get the exact column names from the P&L data that contain 'Shares'
                    shares_cols = [col for col in pl.columns if 'Shares' in col]
                    if len(shares_cols) >= 2:
                        shares_data = pl[shares_cols[:2]]  # Take first two shares columns
                        shares_data.columns = ['Common Shares Outstanding', 'Weighted Average Shares']
                        shares_data = shares_data.round(2)
                        shares_data.columns = [col.strip() for col in shares_data.columns]
                        shares_data.index.names = [name.strip() for name in shares_data.index.names]
                        save_dataframe(shares_data, f"{ticker}_shares_q1234.csv")
                        saved_files.append("shares")
            except Exception as e:
                print(f"Warning: Could not extract shares data: {str(e)}")

            try:
                # Load and save historical Price data
                if 'pl' in saved_files:
                    # Get fiscal quarter end dates from P&L data
                    fiscal_dates = pl.index.get_level_values('Report Date').unique()
                    
                    # Load daily share prices
                    prices = sf.load_shareprices(variant='daily')
                    prices = prices[prices.index.get_level_values('Ticker') == ticker]
                    
                    if not prices.empty:
                        # Get price data for each fiscal quarter end date
                        price_data = []
                        for date in fiscal_dates:
                            # Get the price on the fiscal quarter end date or the closest previous date
                            mask = prices.index.get_level_values('Date') <= date
                            if mask.any():
                                closest_date = prices[mask].index.get_level_values('Date').max()
                                price_row = prices[prices.index.get_level_values('Date') == closest_date]
                                if not price_row.empty:
                                    price_data.append(price_row)
                        
                        if price_data:
                            # Combine all price data
                            price_data = pd.concat(price_data)
                            # Get available columns for price data
                            price_columns = [col for col in ['Close', 'Adj. Close'] if col in price_data.columns]
                            if price_columns:
                                price_data = price_data[price_columns]
                                price_data = price_data.round(2)
                                price_data.columns = [col.strip() for col in price_data.columns]
                                price_data.index.names = [name.strip() for name in price_data.index.names]
                                save_dataframe(price_data, f"{ticker}_price_q1234.csv")
                                saved_files.append("price")
            except Exception as e:
                print(f"Warning: Could not load Price data: {str(e)}")

            if not saved_files:
                print(f"No data could be saved for {ticker}")
                sys.exit(1)
            else:
                print(f"Successfully saved the following datasets for {ticker}: {', '.join(saved_files)}")

        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
            sys.exit(1)

    elif cmd == "ttm":
        if len(sys.argv) < 3:
            print("Usage: ./sfin.py ttm <ticker>")
            sys.exit(1)
        ticker = sys.argv[2]
        sf.set_api_key(os.environ["SIMFIN_API_KEY"])
        sf.set_data_dir('simfin_data')
        try:
            saved_files = []
            
            try:
                # Load and save P&L data
                pl = sf.load_income(variant='ttm')
                pl = pl[pl.index.get_level_values('Ticker') == ticker]
                if not pl.empty:
                    # Format numbers without scientific notation
                    pl = pl.round(2)
                    # Clean up column names
                    pl.columns = [col.strip() for col in pl.columns]
                    pl.index.names = [name.strip() for name in pl.index.names]
                    save_dataframe(pl, f"{ticker}_pl_ttm.csv")
                    saved_files.append("pl")
            except Exception as e:
                print(f"Warning: Could not load P&L data: {str(e)}")

            try:
                # Load and save Balance Sheet data
                bs = sf.load_balance(variant='ttm')
                bs = bs[bs.index.get_level_values('Ticker') == ticker]
                if not bs.empty:
                    bs = bs.round(2)
                    bs.columns = [col.strip() for col in bs.columns]
                    bs.index.names = [name.strip() for name in bs.index.names]
                    save_dataframe(bs, f"{ticker}_bs_ttm.csv")
                    saved_files.append("bs")
            except Exception as e:
                print(f"Warning: Could not load Balance Sheet data: {str(e)}")

            try:
                # Load and save Cash Flow data
                cf = sf.load_cashflow(variant='ttm')
                cf = cf[cf.index.get_level_values('Ticker') == ticker]
                if not cf.empty:
                    cf = cf.round(2)
                    cf.columns = [col.strip() for col in cf.columns]
                    cf.index.names = [name.strip() for name in cf.index.names]
                    save_dataframe(cf, f"{ticker}_cf_ttm.csv")
                    saved_files.append("cf")
            except Exception as e:
                print(f"Warning: Could not load Cash Flow data: {str(e)}")

            try:
                # Load and save Derived data
                derived = sf.load_derived(variant='ttm')
                derived = derived[derived.index.get_level_values('Ticker') == ticker]
                if not derived.empty:
                    derived = derived.round(2)
                    derived.columns = [col.strip() for col in derived.columns]
                    derived.index.names = [name.strip() for name in derived.index.names]
                    save_dataframe(derived, f"{ticker}_derived_ttm.csv")
                    saved_files.append("derived")
            except Exception as e:
                print(f"Warning: Could not load Derived data: {str(e)}")

            try:
                # Extract shares data from income statement
                if 'pl' in saved_files:
                    # Get the exact column names from the P&L data that contain 'Shares'
                    shares_cols = [col for col in pl.columns if 'Shares' in col]
                    if len(shares_cols) >= 2:
                        shares_data = pl[shares_cols[:2]]  # Take first two shares columns
                        shares_data.columns = ['Common Shares Outstanding', 'Weighted Average Shares']
                        shares_data = shares_data.round(2)
                        shares_data.columns = [col.strip() for col in shares_data.columns]
                        shares_data.index.names = [name.strip() for name in shares_data.index.names]
                        save_dataframe(shares_data, f"{ticker}_shares_ttm.csv")
                        saved_files.append("shares")
            except Exception as e:
                print(f"Warning: Could not extract shares data: {str(e)}")

            try:
                # Load and save historical Price data
                if 'pl' in saved_files:
                    # Get fiscal dates from P&L data
                    fiscal_dates = pl.index.get_level_values('Report Date').unique()
                    
                    # Load daily share prices
                    prices = sf.load_shareprices(variant='daily')
                    prices = prices[prices.index.get_level_values('Ticker') == ticker]
                    
                    if not prices.empty:
                        # Get price data for each fiscal date
                        price_data = []
                        for date in fiscal_dates:
                            # Get the price on the fiscal date or the closest previous date
                            mask = prices.index.get_level_values('Date') <= date
                            if mask.any():
                                closest_date = prices[mask].index.get_level_values('Date').max()
                                price_row = prices[prices.index.get_level_values('Date') == closest_date]
                                if not price_row.empty:
                                    price_data.append(price_row)
                        
                        if price_data:
                            # Combine all price data
                            price_data = pd.concat(price_data)
                            # Get available columns for price data
                            price_columns = [col for col in ['Close', 'Adj. Close'] if col in price_data.columns]
                            if price_columns:
                                price_data = price_data[price_columns]
                                price_data = price_data.round(2)
                                price_data.columns = [col.strip() for col in price_data.columns]
                                price_data.index.names = [name.strip() for name in price_data.index.names]
                                save_dataframe(price_data, f"{ticker}_price_ttm.csv")
                                saved_files.append("price")
            except Exception as e:
                print(f"Warning: Could not load Price data: {str(e)}")

            if not saved_files:
                print(f"No data could be saved for {ticker}")
                sys.exit(1)
            else:
                print(f"Successfully saved the following datasets for {ticker}: {', '.join(saved_files)}")

        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
            sys.exit(1)

    elif cmd == "list":
        sf.set_api_key(os.environ["SIMFIN_API_KEY"])
        sf.set_data_dir('simfin_data')
        try:
            # Load companies data
            companies = sf.load_companies()
            search_term = sys.argv[2].lower() if len(sys.argv) > 2 else ""
            
            if search_term:
                # Handle NaN values in the search for both Company Name and Ticker
                name_mask = companies['Company Name'].str.lower().str.contains(search_term, na=False)
                ticker_mask = companies.index.str.lower().str.contains(search_term, na=False)
                companies = companies[name_mask | ticker_mask]
            
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
