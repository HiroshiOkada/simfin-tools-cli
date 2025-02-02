#!/usr/bin/env python3
"""
A command line tool to retrieve financial data using simfin.
This tool provides functionality to:
- List and search companies
- Retrieve full year financial data (P&L, Balance Sheet, Cash Flow, etc.)
Usage: python sfin.py <subcommand> [args]

Note: You may see FutureWarning messages about 'date_parser' being deprecated.
This is from the simfin library and does not affect functionality.
The warning will be resolved in a future update of the simfin package.
"""

import os
import csv
import warnings
import argparse
from contextlib import contextmanager

import simfin as sf
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


@contextmanager
def suppress_simfin_warnings():
    """一時的にsimfinライブラリの特定の警告のみを抑制するコンテキストマネージャー"""
    with warnings.catch_warnings():
        warnings.filterwarnings(
            'ignore',
            category=FutureWarning,
            message='.*date_parser.*'
        )
        yield


def format_number(value):
    """Format number with thousands separator for accounting values"""
    if pd.isna(value):
        return ""
    try:
        num = int(float(value))
        return f"{num:,}"
    except (ValueError, TypeError):
        return str(value)


def format_price(value):
    """Format price with 2 decimal places and multiply by 100 to account for splits"""
    if pd.isna(value):
        return ""
    try:
        return f"{float(value) * 100:.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_date(value):
    """Format date without time component"""
    if pd.isna(value):
        return ""
    try:
        return pd.to_datetime(value).strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return str(value)


def dataframe_to_markdown(df, title, is_price_data=False):
    """Convert DataFrame to Markdown table with proper formatting"""
    simfin_id = (
        df.index.get_level_values('SimFinId')[0]
        if 'SimFinId' in df.index.names else None
    )
    
    md = [f"## {title}" + (f" (SimFinId: {simfin_id})" if simfin_id is not None else "")]
    md.append("")
    
    # DataFrameのインデックスから Ticker, SimFinId を除いたコピーを作成
    df_copy = df.copy()
    if isinstance(df_copy.index, pd.MultiIndex):
        index_names = [name for name in df_copy.index.names if name not in ['Ticker', 'SimFinId']]
        df_copy = df_copy.reset_index()
        for col in ['Ticker', 'SimFinId']:
            if col in df_copy.columns:
                df_copy = df_copy.drop(col, axis=1)
        if index_names:
            df_copy = df_copy.set_index(index_names)
    
    headers = (df_copy.index.names if isinstance(df_copy.index, pd.MultiIndex) else [df_copy.index.name])
    headers = [h for h in headers if h is not None]
    headers.extend(df_copy.columns)
    md.append("| " + " | ".join(headers) + " |")
    
    alignments = []
    for col in headers:
        if col in ['Report Date', 'Date', 'Fiscal Year', 'Fiscal Period', 'Currency', 'Publish Date', 'Restated Date']:
            alignments.append(":-")  # Left align
        else:
            alignments.append("-:")  # Right align
    md.append("| " + " | ".join(alignments) + " |")
    
    for idx, row in df_copy.iterrows():
        if isinstance(idx, tuple):
            index_values = [str(v) for v in idx]
        else:
            index_values = [str(idx)]
        
        formatted_index_values = []
        for i, value in enumerate(index_values):
            if df_copy.index.names[i] in ['Report Date', 'Date']:
                formatted_index_values.append(format_date(value))
            else:
                formatted_index_values.append(value)
        
        formatted_values = []
        for col in df_copy.columns:
            value = row[col]
            if col in ['Report Date', 'Date', 'Publish Date', 'Restated Date']:
                formatted_values.append(format_date(value))
            elif is_price_data and col in ['Close', 'Adj. Close']:
                formatted_values.append(format_price(value))
            else:
                formatted_values.append(format_number(value))
        
        row_values = formatted_index_values + formatted_values
        md.append("| " + " | ".join(row_values) + " |")
    
    md.append("")
    return "\n".join(md)


def save_dataframe(df, filename, index=True):
    """Helper function to save dataframes with consistent formatting"""
    df.to_csv(
        filename,
        sep=',',
        index=index,
        float_format='%.2f',
        encoding='utf-8',
        quoting=csv.QUOTE_NONNUMERIC,
        doublequote=True
    )


def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='Retrieve financial data using SimFin API',
        usage='%(prog)s [options] <command> [<args>]'
    )
    parser.add_argument('--md', action='store_true', help='Output in Markdown format')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    subparsers.add_parser('help', help='Show this help message')
    
    list_parser = subparsers.add_parser('list', help='List or search companies')
    list_parser.add_argument('search_term', nargs='?', default='', help='Search term for company names')
    
    fy_parser = subparsers.add_parser('fy', help='Retrieve full year financial data')
    fy_parser.add_argument('ticker', help='Company ticker symbol')
    
    q_parser = subparsers.add_parser('q', help='Retrieve quarterly financial data')
    q_parser.add_argument('ticker', help='Company ticker symbol')
    
    ttm_parser = subparsers.add_parser('ttm', help='Retrieve trailing twelve months financial data')
    ttm_parser.add_argument('ticker', help='Company ticker symbol')
    
    return parser


def setup_simfin():
    """Set API key and data directory for simfin."""
    sf.set_api_key(os.environ["SIMFIN_API_KEY"])
    sf.set_data_dir('simfin_data')


def process_statement(load_func, ticker, variant, suffix, title, file_tag, markdown, md_list, saved_files):
    """
    共通の財務データの取得・整形・出力処理。
    load_func: simfinのデータ読み込み関数
    """
    try:
        with suppress_simfin_warnings():
            df = load_func(variant=variant)
        df = df[df.index.get_level_values('Ticker') == ticker]
        if df.empty:
            return None
        df = df.round(2)
        df.columns = [col.strip() for col in df.columns]
        df.index.names = [name.strip() for name in df.index.names]
        if markdown:
            md_list.append(dataframe_to_markdown(df, title))
        else:
            filename = f"{ticker}_{file_tag}{suffix}.csv"
            save_dataframe(df, filename)
        saved_files.append(file_tag)
        return df
    except Exception as e:
        print(f"Warning: Could not load {title} data: {e}")
        return None


def process_shares_data(pl, ticker, suffix, markdown, md_list, saved_files):
    """株式データの抽出と出力処理"""
    try:
        if pl is not None:
            shares_cols = [col for col in pl.columns if 'Shares' in col]
            if len(shares_cols) >= 2:
                shares_data = pl[shares_cols[:2]]
                shares_data.columns = ['Common Shares Outstanding', 'Weighted Average Shares']
                shares_data = shares_data.round(2)
                shares_data.columns = [col.strip() for col in shares_data.columns]
                shares_data.index.names = [name.strip() for name in shares_data.index.names]
                if markdown:
                    md_list.append(dataframe_to_markdown(shares_data, "Share Data"))
                else:
                    save_dataframe(shares_data, f"{ticker}_shares{suffix}.csv")
                saved_files.append("shares")
    except Exception as e:
        print(f"Warning: Could not extract shares data: {e}")


def process_price_data(ticker, pl, suffix, markdown, md_list, saved_files):
    """株価データの取得と出力処理"""
    try:
        if pl is not None:
            fiscal_dates = pl.index.get_level_values('Report Date').unique()
            with suppress_simfin_warnings():
                prices = sf.load_shareprices(variant='daily')
            prices = prices[prices.index.get_level_values('Ticker') == ticker]
            if not prices.empty:
                price_data_list = []
                for date in fiscal_dates:
                    mask = prices.index.get_level_values('Date') <= date
                    if mask.any():
                        closest_date = prices[mask].index.get_level_values('Date').max()
                        price_row = prices[prices.index.get_level_values('Date') == closest_date]
                        if not price_row.empty:
                            price_data_list.append(price_row)
                if price_data_list:
                    price_data = pd.concat(price_data_list)
                    price_columns = [col for col in ['Close', 'Adj. Close'] if col in price_data.columns]
                    if price_columns:
                        price_data = price_data[price_columns]
                        price_data = (price_data * 100).round(2)
                        price_data.columns = [col.strip() for col in price_data.columns]
                        price_data.index.names = [name.strip() for name in price_data.index.names]
                        if markdown:
                            md_list.append(dataframe_to_markdown(price_data, "Price Data", is_price_data=True))
                        else:
                            save_dataframe(price_data, f"{ticker}_price{suffix}.csv")
                        saved_files.append("price")
    except Exception as e:
        print(f"Warning: Could not load Price data: {e}")


def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None or args.command == 'help':
        parser.print_help()
        return
    
    if args.command == 'list':
        setup_simfin()
        try:
            companies = sf.load_companies()
            search_term = args.search_term.lower()
            if search_term:
                name_mask = companies['Company Name'].str.lower().str.contains(search_term, na=False)
                ticker_mask = companies.index.str.lower().str.contains(search_term, na=False)
                companies = companies[name_mask | ticker_mask]
            if companies.empty:
                print(f"No companies found matching '{search_term}'")
            else:
                result = companies[['Company Name']].copy()
                result.columns = ['Name']
                print(result)
        except Exception as e:
            print(f"Error retrieving companies list: {e}")
        return

    elif args.command in ['fy', 'q', 'ttm']:
        ticker = args.ticker
        variant = {'fy': 'annual', 'q': 'quarterly', 'ttm': 'ttm'}[args.command]
        suffix = {'fy': '', 'q': '_q1234', 'ttm': '_ttm'}[args.command]
        
        setup_simfin()
        saved_files = []
        markdown_content = []
        
        if args.md:
            markdown_content.append(f"# {ticker}")
            markdown_content.append("")
        
        try:
            # 損益計算書の取得
            pl = process_statement(sf.load_income, ticker, variant, suffix,
                                   "Income Statement", "pl", args.md, markdown_content, saved_files)
            
            # 貸借対照表の取得
            process_statement(sf.load_balance, ticker, variant, suffix,
                              "Balance Sheet", "bs", args.md, markdown_content, saved_files)
            
            # キャッシュフロー計算書の取得
            process_statement(sf.load_cashflow, ticker, variant, suffix,
                              "Cash Flow Statement", "cf", args.md, markdown_content, saved_files)
            
            # Derived Metricsは現プランでは利用不可
            print("Note: Derived metrics are not available in the current plan. Please upgrade to access this feature.")
            
            # 株式データの抽出(損益計算書から)
            process_shares_data(pl, ticker, suffix, args.md, markdown_content, saved_files)
            
            # 株価データの取得
            process_price_data(ticker, pl, suffix, args.md, markdown_content, saved_files)
            
            if not saved_files:
                print(f"No data could be saved for {ticker}")
                return
            else:
                if args.md:
                    md_suffix = suffix  # 同じsuffixを利用
                    md_filename = f"{ticker}{md_suffix}.md"
                    with open(md_filename, 'w', encoding='utf-8') as f:
                        f.write("\n".join(markdown_content))
                    print(f"Successfully saved markdown file: {md_filename}")
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
