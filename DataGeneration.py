import pandas as pd

class DataGeneration:
    def __init__(self, year: int = 2019, demand_year: int=2017, region: str = 'DK'):

        self.year = year # default year is 2019
        self.demand_year = demand_year # default demand year is 2017
        self.region = region # default region is DK1

        self.demand_factor = {'DK': 1.55, 'NO': 1.21, 'DE': 1.11}

        self.demand = self.load_data()
        self.offshore_wind = self.offshore_wind_data()
        self.onshore_wind = self.onshore_wind_data()
        self.solar = self.solar_data()
        self.heat_demand = self.heat_data()

    def load_data(self):
        data = pd.read_csv('data/time_series_60min_singleindex_filtered (4).csv', index_col=0)
        data.index = pd.to_datetime(data.index)        
        data = data[data.index.year == self.demand_year]
        data = data.fillna(0)

        # # Filter the data for the selected region
        data = data[[col for col in data.columns if col.startswith(self.region)]]

        data.rename(columns={f'{self.region}_load_actual_entsoe_transparency': self.region + '_demand'}, inplace=True)

        demand_col = f'{self.region}_load_actual_entsoe_transparency'
        new_demand_col = f'{self.region}_demand'
        data.rename(columns={demand_col: new_demand_col}, inplace=True)

        data[new_demand_col] *= self.demand_factor[self.region]

        return data

    def offshore_wind_data(self):
        data = pd.read_csv('data/offshore_wind_1979-2017.csv', sep=';', index_col=0)
        data.index = pd.to_datetime(data.index)
        if self.year > 2017:
            print(f"Year {self.year} is greater than 2017, using data from last available year.")
            data = data[data.index.year == 2017]
        else:
            data = data[data.index.year == self.year]
        if self.region == 'DK':
            data = data[['DNK']]
            data.rename(columns={'DNK': 'DK_offshore'}, inplace=True)
        elif self.region == 'NO':
            data = data[['NOR']]
            data.rename(columns={'NOR': 'NO_offshore'}, inplace=True)
        elif self.region == 'DE':
            data = data[['DEU']]
            data.rename(columns={'DEU': 'DE_offshore'}, inplace=True)
        else:
            raise ValueError(f"Region {self.region} not recognized.")
        data = data.fillna(0)

        return data
    
    def onshore_wind_data(self):
        data = pd.read_csv('data/onshore_wind_1979-2017.csv', sep=';', index_col=0)
        data.index = pd.to_datetime(data.index)
        if self.year > 2017:
            data = data[data.index.year == 2017]
        else:
            data = data[data.index.year == self.year]
        if self.region == 'DK':
            data = data[['DNK']]
            data.rename(columns={'DNK': 'DK_onshore'}, inplace=True)
        elif self.region == 'NO':
            data = data[['NOR']]
            data.rename(columns={'NOR': 'NO_onshore'}, inplace=True)
        elif self.region == 'DE':
            data = data[['DEU']]
            data.rename(columns={'DEU': 'DE_onshore'}, inplace=True)
        else:
            raise ValueError(f"Region {self.region} not recognized.")
        data = data.fillna(0)

        return data

    def solar_data(self):
        data = pd.read_csv('data/pv_optimal.csv', sep=';', index_col=0)
        data.index = pd.to_datetime(data.index)
        if self.year > 2017:
            data = data[data.index.year == 2017]
        else:
            data = data[data.index.year == self.year]
        if self.region == 'DK':
            data = data[['DNK']]
            data.rename(columns={'DNK': 'DK_solar'}, inplace=True)
        elif self.region == 'NO':
            data = data[['NOR']]
            data.rename(columns={'NOR': 'NO_solar'}, inplace=True)
        elif self.region == 'DE':
            data = data[['DEU']]
            data.rename(columns={'DEU': 'DE_solar'}, inplace=True)
        else:
            raise ValueError(f"Region {self.region} not recognized.")
        data = data.fillna(0)

        return data

    def heat_data(self):
        data = pd.read_csv('data/heat_demand.csv', sep=';', index_col=0)
        data.index = pd.to_datetime(data.index)
        if self.year > 2015:
            data = data[data.index.year == 2015]
        else:
            data = data[data.index.year == self.year]
        if self.region == 'DK':
            data = data[['DNK']]
            data.rename(columns={'DNK': 'DK_heat'}, inplace=True)
        elif self.region == 'NO':
            data = data[['NOR']]
            data.rename(columns={'NOR': 'NO_heat'}, inplace=True)
        elif self.region == 'DE':
            data = data[['DEU']]
            data.rename(columns={'DEU': 'DE_heat'}, inplace=True)
        else:
            raise ValueError(f"Region {self.region} not recognized.")
        data = data.fillna(0)

        return data

    # def hydro_storage_inflow(self):

if __name__ == "__main__":

    region = 'DK'
    # region = 'DK_2'
    # region = 'NO'
    # region = 'DE'
    # region = 'DE'

    year = 2017
    tmp = DataGeneration(year = year, demand_year= 2019, region = region)

    print(tmp.heat_demand)


