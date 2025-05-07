from DataGeneration import DataGeneration
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
class DurationCurve():
    def __init__(self, year: int = 2030, region: str = 'DK', gas_data = None, save_fig: bool = False):
        self.year = year
        self.region = region
        self.gas_data = gas_data
        self.save_fig = save_fig

        self.generate_plot()

    def generate_plot(self):
        plt.figure(figsize=(10, 6))
        plt.title(f'Duration Curves of Wind and Solar Profiles for {self.region} in {self.year}')

        linestyle = ['-', '--', ':', '-.', '-', '--', ':', '-.']  

        data = DataGeneration(year = self.year, region = self.region)
        data_offshore_wind = data.offshore_wind
        data_onshore_wind = data.onshore_wind
        data_solar = data.solar

        data_sorted_wind_on = data_onshore_wind.sort_values(by = f'{self.region}_onshore', ascending = False, ignore_index = True)
        data_sorted_wind_off = data_offshore_wind.sort_values(by = f'{self.region}_offshore', ascending = False, ignore_index=True)
        data_sorted_solar = data_solar.sort_values(by = f'{self.region}_solar', ascending = False, ignore_index = True)

        plt.plot(data_sorted_wind_on, label = f'Onshore Wind - {self.year}', linestyle = linestyle[0], color='blue')
        plt.plot(data_sorted_wind_off, label = f'Offshore Wind - {self.year}', linestyle = linestyle[0], color='green')
        plt.plot(data_sorted_solar, label = f'Solar - {self.year}', linestyle = linestyle[0], color='orange')
        plt.plot(self.gas_data, label = f'Gas - {self.year}', linestyle = linestyle[0], color='black')
        
        plt.legend()
        plt.ylim(0, 1.1)
        plt.xlabel('Hours of the Year')
        plt.ylabel('Generation Capacity (p.u.)')
        plt.grid()
        if self.save_fig:
            plt.savefig(f'./plots/DurationCurve_{self.region}_{self.year}.png', dpi=300, bbox_inches='tight')
        plt.show()

if __name__ == '__main__':
    region = 'DK'
    # region = 'DK_2'
    # region = 'NO'
    # region = 'DE'

    year = 2017
    tmp = DurationCurve(year = year, region = region)
