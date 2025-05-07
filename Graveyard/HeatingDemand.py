import pandas as pd
import matplotlib.pyplot as plt

class HeatingDemand:
    def __init__(self):
        self.regions = ['DK', 'DE', 'NO']

        self.hours_in_2017 = pd.date_range('2017-01-01 00:00', '2017-12-31 23:00', freq='h')

        self.temperature_df = pd.DataFrame(index=self.hours_in_2017)

        self.heating_targets = {
            'DK': 35e6,     # MWh/year
            'DE': 350e6,
            'NO': 50e6,
        }


        for region in self.regions:
            df = pd.read_csv(f'data/Temperature_{region}.csv')

            # Ensure correct column name (use # T2M or T depending on file)
            temp_col = 'T2M'

            # Build datetime column
            df['datetime'] = pd.date_range('2017-01-01 00:00', periods=len(df), freq='h')

            # Use datetime as index and rename temperature column
            df = df.set_index('datetime')
            df = df[[temp_col]].rename(columns={temp_col: region})

            # Join with the main DataFrame
            self.temperature_df = self.temperature_df.join(df)
      
            self.temperature_df[region] = self.temperature_df[region] * 24 / 1000

        # Compute Heating Degree Hours (HDH)
        self.heating_demand_hdh = self._calculate_heating_demand()

        self.scaling_factors = {
            region: self.heating_targets[region] / self.heating_demand_hdh[region].sum()
            for region in self.regions
        }

        self.heating_demand_mw = self.heating_demand_hdh.multiply(self.scaling_factors)


    def _calculate_heating_demand(self, threshold=17):
        return (threshold - self.temperature_df).clip(lower=0)

if __name__ == "__main__":
    hd = HeatingDemand()
    df = hd.temperature_df

    demand_hdh = hd.heating_demand_hdh
    demand_mw = hd.heating_demand_mw

    plt.plot(df.index, df['DK'], label='DK')
    plt.plot(df.index, df['DE'], label='DE')
    plt.plot(df.index, df['NO'], label='NO')
    plt.title('Temperature Data')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.show()
