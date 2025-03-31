import pandas as pd

class DataGeneration:
    def __init__(self, year: int = 2019, region: str = 'DK_1'):

        self.year = year # default year is 2019
        self.region = region # default region is DK1
        self.load_data()

    def load_data(self):
        self.data = pd.read_csv('data/time_series_60min_singleindex_filtered (3).csv', index_col=0)
        self.data.index = pd.to_datetime(self.data.index)        
        self.data = self.data[self.data.index.year == self.year]
        self.data = self.data.fillna(0)

        # Filter the data for the selected region
        self.data = self.data[[col for col in self.data.columns if col.startswith(self.region)]]

        # Get the wind and solar profiles
        if not self.region == 'NO':
            data_columns = ['wind_onshore', 'wind_offshore', 'solar']
        else:
            data_columns = ['wind_onshore']

        for data_col in data_columns:
            if not str(f'{self.region}_{data_col}_capacity') in self.data.columns:
                self.data[f'{self.region}_{data_col}_profile'] = self.data[f'{self.region}_{data_col}_generation_actual'] / self.data[f'{self.region}_{data_col}_generation_actual'].max()
            else:
                self.data[f'{self.region}_{data_col}_profile'] = self.data[f'{self.region}_{data_col}_generation_actual'] / self.data[f'{self.region}_{data_col}_capacity']

        for col in self.data.columns:
            new_col_name = col.split(self.region + '_', 1)[-1]
            self.data.rename(columns={col: new_col_name}, inplace=True)

if __name__ == "__main__":

    region = 'DK_1'
    # region = 'DK_2'
    region = 'NO'
    # region = 'DE'

    year = 2019
    tmp = DataGeneration(year = year, region = region).data

