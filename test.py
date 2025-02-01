#!/usr/bin/env python3
import simfin as sf
import os
from dotenv import load_dotenv
load_dotenv()

# Set up SimFin
sf.set_api_key(os.environ["SIMFIN_API_KEY"])
sf.set_data_dir('simfin_data')

# Load companies and inspect the data
companies = sf.load_companies()
print("Type of companies:", type(companies))
print("\nFirst few items:")
for name, ticker in list(companies.items())[:5]:
    print(f"Name: {name}, Ticker: {ticker}")
