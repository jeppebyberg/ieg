import pandas as pd

class DataGeneration:
    def __init__(self, year: int = 2019):

        self.year = year # default year is 2019
        self.load_data()

    def load_data(self):
        self.data = pd.read_csv('data/time_series_60min_singleindex_filtered.csv', index_col=0)
        self.data.index = pd.to_datetime(self.data.index)        
        self.data = self.data[self.data.index.year == self.year]
        self.data = self.data.fillna(0)

if __name__ == "__main__":
    tmp = DataGeneration()

