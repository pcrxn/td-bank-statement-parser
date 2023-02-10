"""
PARSE-STATEMENT

Parse a PDF-formatted Toronto-Dominion (TD) Bank statement into tabular format.

Dependencies: python=3.11.0, pandas=1.5.3, numpy=1.24.2, pdfplumber = 0.7.6
Other Python and package versions may work but are untested.
"""

import pdfplumber
import pandas as pd
import numpy as np
import re

# Regex patterns
txn_re = re.compile(r'(^[A-Z]{3}\d{1,2}) ([A-Z]{3}\d{1,2}) (\S*) (\$\d+\.\d{2})')
statement_date_re = re.compile(r'STATEMENTDATE:(\S*)')
statement_period_re = re.compile(r'STATEMENTPERIOD:([a-zA-Z]+\d{1,2},\d{4})to([a-zA-Z]+\d{1,2},\d{4})')

# List to hold dictionaries
txn_list = []

with pdfplumber.open("td-statement.pdf") as pdf:

    for page in pdf.pages:

        text = page.extract_text()
        # print(text)
        for line in text.split('\n'):

            if re.match(statement_date_re, line):
                statement_date = re.search(statement_date_re, line).group(1)

            if re.match(statement_period_re, line):
                statement_period_begin = re.search(statement_period_re, line).group(1)
                statement_period_end = re.search(statement_period_re, line).group(2)

            if re.match(txn_re, line):
                txn = re.search(txn_re, line)
                txn_list.append({'transaction_date': txn.group(1),
                                'posting_date': txn.group(2),
                                'activity_desc': txn.group(3),
                                'amount': txn.group(4),
                                'statement_date': statement_date,
                                'statement_period_begin': statement_period_begin,
                                'statement_period_end': statement_period_end})
