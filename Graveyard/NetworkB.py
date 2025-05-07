import pypsa
import pandas as pd
from DataGeneration import DataGeneration
from CostGeneration import CostGeneration

class NetworkB:
    def __init__(self, year: int = 2019, cost_year: int = 2030,
                 setup: dict = {'DK': 
                            {'OCGT': True,
                            'CCGT': True,
                            'battery storage': True,
                            'onwind': True,
                            'solar': True}},
                 CO2_limit: float = 5000000):
        
        self.year = year

        self.cost_year = cost_year 
        self.costs = CostGeneration(year = self.cost_year).costs

        self.setup = setup

        self.CO2_limit = CO2_limit

        self.regions = setup.keys()
        
        self.network = pypsa.Network()
        self.hours_in_year = pd.date_range(f'{year}-01-01 00:00', f'{year}-12-31 23:00', freq='h')
        self.network.set_snapshots(self.hours_in_year.values)

        self.data_dict = {region : {} for region in self.regions}

        self.carriers = ['gas', 'onwind', 'offwind', 'solar']
        self.network.add("Carrier", self.carriers, color=["dodgerblue", "gold", "indianred", "yellow-green"], co2_emissions=[self.costs.at[c, "CO2 intensity"] for c in self.carriers])

        self.add_regions()

        self.network.add(
            "GlobalConstraint",
            "CO2Limit",
            carrier_attribute="co2_emissions",
            sense="<=",
            constant=self.CO2_limit, #5MtCO2
        )

        self.network.optimize(solver_name="gurobi",solver_options={"OutputFlag": 0})

    def add_regions(self):
        for region in self.regions:
            data = DataGeneration(year = self.year, region = region)
            self.data_dict[region]['Demand'] = data.demand
            self.data_dict[region]['solar'] = data.solar
            self.data_dict[region]['onwind'] = data.onshore_wind
            self.data_dict[region]['offwind'] = data.offshore_wind 

            self.add_busses(region) # add bus to region bus

            technologies = self.setup[region].keys()
            for tech in technologies:
                if self.setup[region][tech]:
                    self.add_network_technologies(region, tech) # add all regioin technologies

    def add_busses(self, region):
        self.network.add("Bus", f'electricity bus {region}')
        self.network.add("Load", f'load {region}', bus = f'electricity bus {region}', p_set = self.data_dict[region]['Demand'].values.flatten())

    def add_network_technologies(self, region, tech):
        if tech in ['OCGT', 'CCGT']:
            self.network.add("Generator", f'{tech} {region}', 
                                bus = f'electricity bus {region}', 
                                p_nom_extendable=True, 
                                carrier='gas', 
                                capital_cost = self.costs.at[tech, "capital_cost"], 
                                marginal_cost = self.costs.at[tech, "marginal_cost"])
        elif tech == 'solar':
            self.network.add("Generator",
                                f'{tech} {region}', 
                                bus = f'electricity bus {region}', 
                                p_nom_extendable=True, 
                                carrier='solar', 
                                capital_cost = self.costs.at[tech, "capital_cost"], 
                                marginal_cost = self.costs.at[tech, "marginal_cost"],
                                p_max_pu = self.data_dict[region]['solar'].values.flatten())
        elif tech == 'onwind':
            self.network.add("Generator", f'{tech} {region}', 
                                bus = f'electricity bus {region}', 
                                p_nom_extendable=True, 
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

    @staticmethod
    def annuity(n, r):
        """ Calculate the annuity factor for an asset with lifetime n years and
        discount rate  r """

        if r > 0:
            return r/(1. - 1./(1.+r)**n)
        else:
            return 1/n