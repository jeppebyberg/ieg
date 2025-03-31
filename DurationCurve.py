from DataGeneration import DataGeneration
import pandas as pd
import matplotlib.pyplot as plt

class DurationCurve():
    def __init__(self, years: list[int] = 2019, region: str = 'DK_1'):
        self.years = years
        self.region = region

        self.generate_plot()

    def generate_plot(self):
        plt.figure(figsize=(10, 6))
        plt.title(f'Duration Curves of Wind and Solar Profiles for {self.region} in {self.years}')

        linestyle = ['-', '--', ':', '-.', '-']  

        for i, y in enumerate(self.years):
            data = DataGeneration(year = y, region = self.region).data

            data_sorted_wind_on= data.sort_values(by = 'wind_onshore_profile', ascending = False, ignore_index = True)
            if not self.region == 'NO':
                data_sorted_wind_off = data.sort_values(by = 'wind_offshore_profile', ascending = False, ignore_index=True)
                data_sorted_solar = data.sort_values(by = 'solar_profile', ascending = False, ignore_index = True)

            plt.plot(data_sorted_wind_on['wind_onshore_profile'], label = f'Onshore Wind - {y}', linestyle = linestyle[i], color='blue')
            if not self.region == 'NO':
                plt.plot(data_sorted_wind_off['wind_offshore_profile'], label = f'Offshore Wind - {y}', linestyle = linestyle[i], color='green')
                plt.plot(data_sorted_solar['solar_profile'], label = f'Solar - {y}', linestyle = linestyle[i], color='orange')
        plt.legend()
        plt.show()


if __name__ == '__main__':
    # region = 'DK_1'
    region = 'DK_2'
    # region = 'NO'
    # region = 'DE'

    years = [2017, 2018, 2019, 2020]
    tmp = DurationCurve(years = years, region = region)
