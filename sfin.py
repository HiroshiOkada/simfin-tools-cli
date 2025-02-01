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
import argparse
from dotenv import load_dotenv
load_dotenv()

def format_number(value):
    """Format number with thousands separator for accounting values"""
    if pd.isna(value):
        return ""
    try:
        # Convert to integer first to remove decimal places
        num = int(float(value))
        return f"{num:,}"
    except (ValueError, TypeError):
        return str(value)

def format_price(value):
    """Format price with 3 decimal places"""
    if pd.isna(value):
        return ""
    try:
        return f"{float(value):.3f}"
    except (ValueError, TypeError):
        return str(value)

def save_dataframe(df, filename, index=True):
    """Helper function to save dataframes with consistent formatting"""
    df.to_csv(filename, 
              sep=',',
              index=index,
              float_format='%.2f',
              encoding='utf-8',
              quoting=csv.QUOTE_NONNUMERIC,
              doublequote=True)

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='Retrieve financial data using SimFin API',
        usage='%(prog)s [options] <command> [<args>]'
    )
    parser.add_argument('--md', action='store_true', help='Output in Markdown format')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # help command
    help_parser = subparsers.add_parser('help', help='Show this help message')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List or search companies')
    list_parser.add_argument('search_term', nargs='?', default='', help='Search term for company names')
    
    # fy command
    fy_parser = subparsers.add_parser('fy', help='Retrieve full year financial data')
    fy_parser.add_argument('ticker', help='Company ticker symbol')
    
    # q command
    q_parser = subparsers.add_parser('q', help='Retrieve quarterly financial data')
    q_parser.add_argument('ticker', help='Company ticker symbol')
    
    # ttm command
    ttm_parser = subparsers.add_parser('ttm', help='Retrieve trailing twelve months financial data')
    ttm_parser.add_argument('ticker', help='Company ticker symbol')
    
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None or args.command == 'help':
        parser.print_help()
        return
    
    if args.command == 'list':
        sf.set_api_key(os.environ["SIMFIN_API_KEY"])
        sf.set_data_dir('simfin_data')
        try:
            # Load companies data
            companies = sf.load_companies()
            search_term = args.search_term.lower()
            
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
            return
    
    elif args.command in ['fy', 'q', 'ttm']:
        ticker = args.ticker
        variant = {'fy': 'annual', 'q': 'quarterly', 'ttm': 'ttm'}[args.command]
        suffix = {'fy': '', 'q': '_q1234', 'ttm': '_ttm'}[args.command]
        
        sf.set_api_key(os.environ["SIMFIN_API_KEY"])
        sf.set_data_dir('simfin_data')
        try:
            saved_files = []
            
            try:
                # Load and save P&L data
                pl = sf.load_income(variant=variant)
                pl = pl[pl.index.get_level_values('Ticker') == ticker]
                if not pl.empty:
                    # Format numbers without scientific notation
                    pl = pl.round(2)
                    # Clean up column names
                    pl.columns = [col.strip() for col in pl.columns]
                    pl.index.names = [name.strip() for name in pl.index.names]
                    save_dataframe(pl, f"{ticker}_pl{suffix}.csv")
                    saved_files.append("pl")
            except Exception as e:
                print(f"Warning: Could not load P&L data: {str(e)}")

            try:
                # Load and save Balance Sheet data
                bs = sf.load_balance(variant=variant)
                bs = bs[bs.index.get_level_values('Ticker') == ticker]
                if not bs.empty:
                    bs = bs.round(2)
                    bs.columns = [col.strip() for col in bs.columns]
                    bs.index.names = [name.strip() for name in bs.index.names]
                    save_dataframe(bs, f"{ticker}_bs{suffix}.csv")
                    saved_files.append("bs")
            except Exception as e:
                print(f"Warning: Could not load Balance Sheet data: {str(e)}")

            try:
                # Load and save Cash Flow data
                cf = sf.load_cashflow(variant=variant)
                cf = cf[cf.index.get_level_values('Ticker') == ticker]
                if not cf.empty:
                    cf = cf.round(2)
                    cf.columns = [col.strip() for col in cf.columns]
                    cf.index.names = [name.strip() for name in cf.index.names]
                    save_dataframe(cf, f"{ticker}_cf{suffix}.csv")
                    saved_files.append("cf")
            except Exception as e:
                print(f"Warning: Could not load Cash Flow data: {str(e)}")

            try:
                # Load and save Derived data
                derived = sf.load_derived(variant=variant)
                derived = derived[derived.index.get_level_values('Ticker') == ticker]
                if not derived.empty:
                    derived = derived.round(2)
                    derived.columns = [col.strip() for col in derived.columns]
                    derived.index.names = [name.strip() for name in derived.index.names]
                    save_dataframe(derived, f"{ticker}_derived{suffix}.csv")
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
                        save_dataframe(shares_data, f"{ticker}_shares{suffix}.csv")
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
                                save_dataframe(price_data, f"{ticker}_price{suffix}.csv")
                                saved_files.append("price")
            except Exception as e:
                print(f"Warning: Could not load Price data: {str(e)}")

            if not saved_files:
                print(f"No data could be saved for {ticker}")
                return
            else:
                print(f"Successfully saved the following datasets for {ticker}: {', '.join(saved_files)}")

        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
            return
    
    else:
        parser.print_help()
        return

if __name__ == "__main__":
    main()
