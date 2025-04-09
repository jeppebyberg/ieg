import pandas as pd
import pypsa
import gurobipy as gp

class Project:
    def __init__(self):
        
        self.network = pypsa.Network()
        self.hours_in_2019 = pd.date_range('2019-01-01 00:00', '2019-12-31 23:00', freq='h')
        self.network.set_snapshots(self.hours_in_2019.values)

        self.load_data()

        self.add_busses()

        self.network.optimize(solver_name='gurobi')

    def add_busses(self):
        self.network.add("Bus", 'electricity bus')
        self.network.add("Load", 'load', bus = 'electricity bus', p_set = self.data['DK_load_actual_entsoe_transparency'].values)
        # add the different carriers, only gas emits CO2

        self.network.add("Carrier", "gas", co2_emissions=0.19) # in t_CO2/MWh_th
        # add OCGT (Open Cycle Gas Turbine) generator
        capital_cost_OCGT = self.annuity(25,0.07)*560000*(1+0.033) # in €/MW
        fuel_cost = 21.6 # in €/MWh_th
        efficiency = 0.39 # MWh_elec/MWh_th
        marginal_cost_OCGT = fuel_cost/efficiency # in €/MWh_el
        
        self.network.add("Generator",
                    "OCGT",
                    bus="electricity bus",
                    p_nom_extendable=True,
                    carrier="gas",
                    #p_nom_max=1000,
                    capital_cost = capital_cost_OCGT,
                    marginal_cost = marginal_cost_OCGT)

        self.network.add("Carrier", "onshorewind")
        # add onshore wind generator
        CF_wind = self.data['DK_wind_onshore_generation_actual'].values
        capital_cost_onshorewind = self.annuity(30,0.07)*910000*(1+0.033) # in €/MW
        self.network.add("Generator",
                    "onshorewind",
                    bus="electricity bus",
                    p_nom_extendable=True,
                    carrier="onshorewind",
                    #p_nom_max=1000, # maximum capacity can be limited due to environmental constraints
                    capital_cost = capital_cost_onshorewind,
                    marginal_cost = 0,
                    p_max_pu = CF_wind)


        self.network.add("Carrier", "solar")

        # add solar PV generator
        CF_solar = self.data['DK_solar_generation_actual'].values
        capital_cost_solar = self.annuity(25,0.07)*425000*(1+0.03) # in €/MW
        self.network.add("Generator",
                    "solar",
                    bus="electricity bus",
                    p_nom_extendable=True,
                    carrier="solar",
                    #p_nom_max=1000, # maximum capacity can be limited due to environmental constraints
                    capital_cost = capital_cost_solar,
                    marginal_cost = 0,
                    p_max_pu = CF_solar)

    def add_line(self, name, bus0, bus1, length, s_nom):
        self.network.add("Line", name, bus0, bus1, length=length, s_nom=s_nom)

    def load_data(self):
        self.data = pd.read_csv('data/time_series_60min_singleindex_filtered.csv', index_col=0)
        self.data.index = pd.to_datetime(self.data.index)

    def annuity(self, n, r):
        """ Calculate the annuity factor for an asset with lifetime n years and
        discount rate  r """

        if r > 0:
            return r/(1. - 1./(1.+r)**n)
        else:
            return 1/n

if __name__ == "__main__":
    tmp = Project()
