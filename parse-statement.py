#!/usr/bin/env python3

"""
PARSE-STATEMENT
Author: Liam Brown

Parse a PDF-formatted Toronto-Dominion (TD) Bank statement into tabular format.

Dependencies:
    python >= 3.11.0
    pandas >= 1.5.3
    pdfplumber >= 0.7.6

Other versions may work but are untested.
"""

import argparse
import pdfplumber
import pandas as pd
import re

# Regex patterns
TXN_RE = re.compile(r'(^[A-Z]{3}\d{1,2}) ([A-Z]{3}\d{1,2}) (\S+) (-?\$\d+\.\d{2})')
STATEMENT_DATE_RE = re.compile(r'STATEMENTDATE:(\S+)')
STATEMENT_PERIOD_RE = re.compile(r'STATEMENTPERIOD:([a-zA-Z]+\d{1,2},\d{4})to([a-zA-Z]+\d{1,2},\d{4})')

def parse_statement(pdf_path: str, output_path: str) -> None:
    txn_list = []

    statement_date = None
    statement_period_begin = None
    statement_period_end = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for line in text.split('\n'):
                # Extract statement date
                match = STATEMENT_DATE_RE.match(line)
                if match:
                    statement_date = match.group(1)
                    continue

                # Extract statement period
                match = STATEMENT_PERIOD_RE.match(line)
                if match:
                    statement_period_begin, statement_period_end = match.group(1), match.group(2)
                    continue

                # Extract transactions
                match = TXN_RE.match(line)
                if match:
                    txn_list.append({
                        'transaction_date': match.group(1),
                        'posting_date': match.group(2),
                        'activity_desc': match.group(3),
                        'amount': match.group(4),
                        'statement_date': statement_date,
                        'statement_period_begin': statement_period_begin,
                        'statement_period_end': statement_period_end,
                    })

    df = pd.DataFrame(txn_list)
    df.to_csv(output_path, sep='\t', index=False)
    print(f"Extracted {len(df)} transactions to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse TD Bank statement PDF into tabular format.")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("output_path", help="Path to the output TSV file")
    args = parser.parse_args()

    parse_statement(args.pdf_path, args.output_path)
