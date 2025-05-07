import pypsa
import pandas as pd
from DataGeneration import DataGeneration
from HeatingDemand import HeatingDemand
from CostGeneration import CostGeneration


class ExpandedHeatNetwork:
    def __init__(self, year: int = 2017, cost_year: int = 2030, demand_year: int = 2019,
                 setup: dict = {'DK': 
                            {'OCGT': True,
                            'battery storage': True,
                            'onwind': True,
                            'solar': True,
                            'electrolysis': True,
                            'fuel cell': True,
                            'H2 (l) storage tank': True,
                            'industrial heat pump high temperature': True,
                            }}):
        
        self.year = year
        self.demand_year = demand_year

        self.cost_year = cost_year 
        self.costs = CostGeneration(year = self.cost_year).costs

        self.heating_demand = HeatingDemand().heating_demand_mw

        self.setup = setup
        self.regions = setup.keys()

        self.coordinates = {
            'DK': (55.98, 9.55),
            'DE': (51.64, 10.28),
            'NO': (61.68, 9.55),}
        
        self.network = pypsa.Network()
        self.hours_in_year = pd.date_range(f'{year}-01-01 00:00', f'{year}-12-31 23:00', freq='h')
        if len(self.hours_in_year) > 8760:
            self.hours_in_year = self.hours_in_year[:8760]  # Cut off extra Feb 29
        self.hours_in_year = self.hours_in_year
        self.network.set_snapshots(self.hours_in_year.values)

        self.data_dict = {region : {} for region in self.regions}

        self.carriers = ['gas', 'onwind', 'offwind', 'solar', 'hydrogen']

        self.colors = {'OCGT': 'gray',
                       'onwind': 'lightblue',
                       'offwind': 'dodgerblue',
                       'solar': 'orange',
                       'battery storage': 'lightgreen',
                       'electrolysis': 'brown',
                       'fuel cell': 'purple',}

        self.network.add("Carrier", self.carriers, co2_emissions=[self.costs.at[c, "CO2 intensity"] if c in self.costs.index else 0 for c in self.carriers])

        self.add_regions()

        #self.network.optimize(solver_name="gurobi",solver_options={"OutputFlag": 0})

    def add_regions(self):
        for region in self.regions:
            data = DataGeneration(year = self.year, demand_year=self.demand_year, region = region)
            self.data_dict[region]['Demand'] = data.demand
            self.data_dict[region]['solar'] = data.solar
            self.data_dict[region]['onwind'] = data.onshore_wind
            self.data_dict[region]['offwind'] = data.offshore_wind 
            self.data_dict[region]['heat_demand'] = data.heat_demand

            self.add_electricity_busses(region) # add electricity bus to region bus

            self.add_hydrogen_bus(region) # add hydrogen bus to region bus

            self.add_heat_bus(region) # add heat bus to region bus

            technologies = self.setup[region].keys()
            for tech in technologies:
                if self.setup[region][tech]:
                    self.add_network_technologies(region, tech) # add all region technologies

    def add_electricity_busses(self, region):
        self.network.add("Bus", f'electricity bus {region}',
                    x = self.coordinates[region][1], 
                    y = self.coordinates[region][0])
        
        self.network.add("Load", f'load {region}', bus = f'electricity bus {region}', p_set = self.data_dict[region]['Demand'].values.flatten())

    def add_hydrogen_bus(self, region):
        self.network.add("Bus", f'hydrogen bus {region}', carrier='hydrogen',
                    x = self.coordinates[region][1], 
                    y = self.coordinates[region][0])

    def add_heat_bus(self, region):
        self.network.add("Bus", f'heat bus {region}', carrier='heat',
                    x = self.coordinates[region][1], 
                    y = self.coordinates[region][0])

        self.network.add("Load", f'heat load {region}', bus = f'heat bus {region}', p_set = self.data_dict[region]['heat_demand'].values.flatten())

    def add_network_technologies(self, region, tech):
        if tech in ['OCGT', 'CCGT']:
            self.network.add("Generator", f'{tech} {region}', 
                                bus = f'electricity bus {region}', 
                                p_nom_extendable=True, 
                                carrier='gas', 
                                capital_cost = self.costs.at[tech, "capital_cost"], 
                                marginal_cost = self.costs.at[tech, "marginal_cost"])
        elif tech == 'solar':
            if region == 'DE':
                self.network.add("Generator",
                    f'{tech} {region}', 
                    bus = f'electricity bus {region}', 
                    p_nom_extendable=True, 
                    p_nom_max = 75000, # 75 GW limit
                    carrier='solar', 
                    capital_cost = self.costs.at[tech, "capital_cost"], 
                    marginal_cost = self.costs.at[tech, "marginal_cost"],
                    p_max_pu = self.data_dict[region]['solar'].values.flatten())
            else:
                self.network.add("Generator",
                    f'{tech} {region}', 
                    bus = f'electricity bus {region}', 
                    p_nom_extendable=True, 
                    carrier='solar', 
                    capital_cost = self.costs.at[tech, "capital_cost"], 
                    marginal_cost = self.costs.at[tech, "marginal_cost"],
                    p_max_pu = self.data_dict[region]['solar'].values.flatten())

        elif tech == 'onwind':
            if region == 'DK':
                self.network.add("Generator", f'{tech} {region}', 
                                    bus = f'electricity bus {region}', 
                                    p_nom_extendable=True,
                                    p_nom_max = 5500, # 5.5 GW limit 
                                    carrier='onwind', 
                                    capital_cost = self.costs.at[tech, "capital_cost"], 
                                    marginal_cost = self.costs.at[tech, "marginal_cost"],
                                    p_max_pu = self.data_dict[region]['onwind'].values.flatten())  
            else:
                self.network.add("Generator", f'{tech} {region}', 
                    bus = f'electricity bus {region}', 
                    p_nom_extendable=True,
                    # p_nom_max = 5500, # 5.5 GW limit 
                    carrier='onwind', 
                    capital_cost = self.costs.at[tech, "capital_cost"], 
                    marginal_cost = self.costs.at[tech, "marginal_cost"],
                    p_max_pu = self.data_dict[region]['onwind'].values.flatten())  
        elif tech == 'offwind':
            self.network.add("Generator", f'{tech} {region}', 
                                bus = f'electricity bus {region}', 
                                p_nom_extendable=True, 
                                carrier='offwind', 
                                capital_cost = self.costs.at[tech, "capital_cost"], 
                                marginal_cost = self.costs.at[tech, "marginal_cost"],
                                p_max_pu = self.data_dict[region]['offwind'].values.flatten())
        elif tech == 'battery storage':
            self.network.add("Store", f'{tech} {region}',
                                bus = f'electricity bus {region}', 
                                e_nom_extendable=True, 
                                e_cyclic = True,
                                capital_cost = self.costs.at[tech, "capital_cost"])
        elif tech == 'H2 (l) storage tank':
            self.network.add("Store", f'{tech} {region}',
                                bus = f'hydrogen bus {region}',
                                e_nom_extendable=True, 
                                e_cyclic = True,
                                capital_cost = self.costs.at[tech, "capital_cost"])
        elif tech == 'electrolysis':
            self.network.add("Link", f'{tech} {region}',
                bus0=f"electricity bus {region}",  
                bus1=f"hydrogen bus {region}",     
                bus2=f"heat bus {region}",         
                p_nom_extendable=True,
                efficiency=self.costs.at[tech, "efficiency"],           
                efficiency2=self.costs.at[tech, "efficiency-heat"],     
                capital_cost=self.costs.at["electrolysis", "capital_cost"])
            
        elif tech == 'fuel cell':
            self.network.add("Link", f'{tech} {region}', 
                                bus0 = f'hydrogen bus {region}',
                                bus1 = f'electricity bus {region}',
                                p_nom_extendable=True, 
                                capital_cost = self.costs.at[tech, "capital_cost"], 
                                efficiency = self.costs.at[tech, "efficiency"])
        elif tech == 'industrial heat pump high temperature':
            self.network.add("Link", f'{tech} {region}', 
                                bus0 = f'electricity bus {region}',
                                bus1 = f'heat bus {region}',
                                p_nom_extendable=True,
                                capital_cost = self.costs.at[tech, "capital_cost"],
                                efficiency = self.costs.at[tech, "efficiency"])

    @staticmethod
    def annuity(n, r):
        """ Calculate the annuity factor for an asset with lifetime n years and
        discount rate  r """

        if r > 0:
            return r/(1. - 1./(1.+r)**n)
        else:
            return 1/n
# if __name__ == "__main__":
#     setup = {'DK': 
#                     {'OCGT': True,
#                     'CCGT': False,
#                     'battery storage': False,
#                     'onwind': True,
#                     'offwind': True,
#                     'solar': True},
#             'DE': 
#                     {'OCGT': True,
#                      'solar': True,
#                     'offwind': True,
#                     'onwind': True,}
#                     # 'CCGT': True},
#                     }

#     tmp = BuildBaseNetwork(setup = setup, cost_year = 2030, year = 2017, demand_year= 2017)
#     print(tmp.network.generators.p_nom_opt)