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


        # Save figures?? 
        save_fig = False
        save_path = f'./plots/DurationCurve_{self.region}.png'

        linestyle = ['-', '--', ':', '-.', '-']  

        for i, y in enumerate(self.years):
            data = DataGeneration(year = y, region = self.region)
            data_offshore_wind = data.offshore_wind
            data_onshore_wind = data.onshore_wind
            data_solar = data.solar

            data_sorted_wind_on = data_onshore_wind.sort_values(by = f'{self.region}_onshore', ascending = False, ignore_index = True)
            data_sorted_wind_off = data_offshore_wind.sort_values(by = f'{self.region}_offshore', ascending = False, ignore_index=True)
            data_sorted_solar = data_solar.sort_values(by = f'{self.region}_solar', ascending = False, ignore_index = True)

            plt.plot(data_sorted_wind_on, label = f'Onshore Wind - {y}', linestyle = linestyle[i], color='blue')
            plt.plot(data_sorted_wind_off, label = f'Offshore Wind - {y}', linestyle = linestyle[i], color='green')
            plt.plot(data_sorted_solar, label = f'Solar - {y}', linestyle = linestyle[i], color='orange')
        plt.legend()
        plt.ylim(0, 1.1)
        plt.xlabel('Hours of the Year')
        plt.ylabel('Generation Capacity (p.u.)')
        if save_fig:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

if __name__ == '__main__':
    # region = 'DK_1'
    region = 'DK_2'
    # region = 'NO'
    # region = 'DE'

    years = [2015, 2016, 2017]
    tmp = DurationCurve(years = years, region = region)
