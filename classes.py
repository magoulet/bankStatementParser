import io
import os
import pandas as pd
import yaml

class AppConfig():
    def __init__(self):
        cfg = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
        self.config = cfg

    def get_ci_path(self):
        basedir = self.config['ci']['basedir']
        filename = self.config['ci']['filename']
        path = os.path.join(basedir, filename)
        return path

    def get_ibkr_path(self):
        basedir = self.config['ibkr']['basedir']
        filename = self.config['ibkr']['filename']
        path = os.path.join(basedir, filename)
        return path

    def get_closed_path(self):
        basedir = self.config['closed']['basedir']
        filename = self.config['closed']['filename']
        path = os.path.join(basedir, filename)
        return path

class ci_direct_investing():
    def __init__(self):
        pass

    def print(self):
        print(f"Transactions: {self.transactions}")

    def parse(self, path):
        df = pd.read_csv(path,
                         # index_col=['Effective Date'],
                         parse_dates=['Effective Date']
                         )
        df = df.rename(columns={'Effective Date': 'Date', 'Total Value': 'Amount'})
        self.transactions = df

    def dividends(self):
        df = self.transactions
        condition = df['Activity'] == 'Dividend'
        cols = ['Date', 'Description', 'Amount']
        self.dividends = df.loc[condition, cols]

        return self.dividends

    def monthly_dividends(self):
        self.dividends()
        df = self.dividends
        self.monthly_dividends = df.groupby(pd.Grouper(key='Date', freq='ME')).agg({'Amount': 'sum'})
        # print(f"Dividend summary: \n{self.monthly_dividends}")
        return self.monthly_dividends

    def orders(self):
        df = self.transactions
        condition = (df['Activity'] == 'Buy') | (df['Activity'] == 'Sell')
        cols = ['Date', 'Activity', 'Symbol','Quantity','Price', 'Amount']
        self.orders = df.loc[condition, cols]

        return self.orders

class interactive_brokers():
    def __init__(self):
        pass

    def print(self):
        print(f"Transactions: {self.transactions}")

    def parse(self, path):
        buf = io.StringIO()

        with open(path, "r") as f:
            lines = f.readlines()
        with buf as f:
            headerFlag = False
            for line in lines:
                if (line.startswith("Dividends,Header")) and not headerFlag :
                    f.write(line)
                    headerFlag = True
                if line.startswith("Dividends,Data,USD"):
                    f.write(line)

            buf.seek(0)
            df = pd.read_csv(buf,
                             # index_col=['Effective Date'],
                             parse_dates=['Date']
                             )
        self.transactions = df

    def dividends(self):
        df = self.transactions
        self.dividends = df

        return self.dividends

    def monthly_dividends(self):
        self.dividends()
        df = self.dividends
        self.monthly_dividends = df.groupby(pd.Grouper(key='Date', freq='ME')).agg({'Amount': 'sum'})

        return self.monthly_dividends

class closed_accounts():
    def __init__(self):
        pass

    def print(self):
        pass

    def parse(self, path):
        df = pd.read_csv(path,
                 # index_col=['Effective Date'],
                 parse_dates=['Date']
                 )
        self.transactions = df

    def dividends(self):
        self.dividends = self.transactions
        return self.dividends

    def monthly_dividends(self):
        self.dividends()
        df = self.dividends
        self.monthly_dividends = df.groupby(pd.Grouper(key='Date', freq='ME')).agg({'Amount': 'sum'})
        return self.monthly_dividends
