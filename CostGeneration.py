import pandas as pd
class CostGeneration:
       def __init__(self, year: int = 2020):
               self.costs = cost_data()

    def cost_data(self):
        url = f"https://raw.githubusercontent.com/PyPSA/technology-data/master/outputs/costs_{self.year}.csv"
        costs = pd.read_csv(url, index_col=[0, 1])
        costs.loc[costs.unit.str.contains("/kW"), "value"] *= 1e3
        costs.unit = costs.unit.str.replace("/kW", "/MW")

        defaults = {
            "FOM": 0,
            "VOM": 0,
            "efficiency": 1,
            "fuel": 0,
            "investment": 0,
            "lifetime": 25,
            "CO2 intensity": 0,
            "discount rate": 0.07,
        }
        costs = costs.value.unstack().fillna(defaults)

        costs.at["OCGT", "fuel"] = costs.at["gas", "fuel"]
        costs.at["CCGT", "fuel"] = costs.at["gas", "fuel"]
        costs.at["OCGT", "CO2 intensity"] = costs.at["gas", "CO2 intensity"]
        costs.at["CCGT", "CO2 intensity"] = costs.at["gas", "CO2 intensity"]

        
        costs["marginal_cost"] = costs["VOM"] + costs["fuel"] / costs["efficiency"]
        annuity = costs.apply(lambda x: annuity(x["discount rate"], x["lifetime"]), axis=1)
        costs["capital_cost"] = (annuity + costs["FOM"] / 100) * costs["investment"]
        costs.at["onwind", "capital_cost"] #EUR/MW/a
        costs.at["solar", "capital_cost"] #EUR/MW/a
        costs.at["CCGT", "CO2 intensity"] #tCO2/MWh_th
        return costs    

    def annuity(r, n):
            return r / (1.0 - 1.0 / (1.0 + r) ** n)

if __name__ == "__main__":

    