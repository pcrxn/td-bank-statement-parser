#!/usr/bin/env python3

"""
parse-non-credit-statement.py
Author: Liam Brown

Parses a PDF-formatted Toronto-Dominion (TD) Bank non-credit card statement
(e.g. chequing or savings account) into a tabular format (TSV).

Dependencies:
    - python >= 3.11.0
    - pandas >= 1.5.3
    - pdfplumber >= 0.7.6
"""

import argparse
import re
import pdfplumber
import pandas as pd

# Regex pattern to extract statement date range from the header
STATEMENT_DATES_RE = re.compile(r"([A-Z]{3}\d{2}/\d{2})-\s*([A-Z]{3}\d{2}/\d{2})")

# PDF table extraction settings
TABLE_SETTINGS = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "text",
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "text_tolerance": 3,
    "intersection_tolerance": 7,
    "edge_min_length": 5,
    "min_words_vertical": 1,
    "min_words_horizontal": 1,
}


def parse_statement(pdf_path: str, output_path: str) -> None:
    transactions = []
    start_balance = close_balance = None
    start_date = close_date = None
    closing_found = False

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if closing_found:
                break

            text = page.extract_text()
            if not text:
                continue

            # Extract statement dates from header text
            for line in text.splitlines():
                match = STATEMENT_DATES_RE.search(line)
                if match:
                    start_date, close_date = match.groups()
                    break  # Only need to match once per page

            # Extract transaction table
            table = page.extract_table(table_settings=TABLE_SETTINGS)
            if not table:
                continue

            for i, row in enumerate(table):
                if i == 0:
                    continue  # Skip header

                label = row[0]
                if label == "STARTINGBALANCE":
                    start_balance = row[4]
                elif label == "CLOSINGBALANCE":
                    close_balance = row[4]
                    closing_found = True
                    break
                else:
                    transactions.append({
                        "activity_desc": row[0],
                        "amount_withdrawal": row[1],
                        "amount_deposit": row[2],
                        "activity_date": row[3],
                        "activity_balance": row[4],
                    })

    df = pd.DataFrame(transactions)
    df["statement_starting_date"] = start_date
    df["statement_starting_balance"] = start_balance
    df["statement_closing_date"] = close_date
    df["statement_closing_balance"] = close_balance

    df.to_csv(output_path, sep="\t", index=False)
    print(f"Extracted {len(df)} transactions to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Parse TD Bank non-credit card statement PDF into tabular format (TSV).")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("output_path", help="Path to the output TSV file")
    args = parser.parse_args()

    parse_statement(args.pdf_path, args.output_path)


if __name__ == "__main__":
    main()