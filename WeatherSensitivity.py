from BaseNetwork import BuildBaseNetwork
from DataGeneration import DataGeneration
from DurationCurve import DurationCurve
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

setup = {'DK': 
                {'OCGT': True,
                'solar': True,
                'offwind': True,
                'onwind': True},
        'DE': 
                {'OCGT': True,
                'solar': True,
                'offwind': True,
                'onwind': True,}
                # 'CCGT': True},
                }

years = [2012, 2013, 2014, 2015, 2016, 2017]

generator_opt = {
    key: {
        'OCGT': [],
        'CCGT': [],
        'onwind': [],
        'offwind': [],
        'solar': []}
    for key in setup.keys()}

network = {year: None for year in years}
for year in years:
    tmp = BuildBaseNetwork(year = year, demand_year=2017, setup = setup, cost_year = 2030)
    tmp.network.optimize(solver_name="gurobi",solver_options={"OutputFlag": 0})
    network[year] = tmp.network
    generators = tmp.network.generators.p_nom_opt.keys()
    for region in tmp.regions:
        for generator in generators:
            if generator.split(' ')[1] == region:
                generator_opt[region][generator.split(' ')[0]].append(tmp.network.generators.p_nom_opt[generator].sum())

technologies = ['OCGT', 'onwind', 'offwind', 'solar']
x = np.arange(len(years) + 1)  # One extra slot for 'Average'
bar_width = 0.15

for country, techs in generator_opt.items():
    plt.figure(figsize=(12, 6))

    for i, tech in enumerate(technologies):
        values = techs.get(tech, [])
        base_value = values[years.index(2017)] if values and values[years.index(2017)] != 0 else 1

        normalized = [(v / base_value) * 100 for v in values]
        avg = np.mean(normalized)
        normalized.append(avg)

        plt.bar(x + i * bar_width, normalized, width=bar_width, label=tech)

    xtick_labels = years + ['Avg']
    plt.xticks(x + bar_width * (len(technologies) - 1) / 2, xtick_labels)

    plt.axhline(100, color='gray', linestyle='--', linewidth=1)
    plt.title(f"Electricity Mix Relative to 2017 - {country}")
    plt.xlabel("Year")
    plt.ylabel("Capacity (% of 2017)")
    plt.legend()
    plt.tight_layout()
    plt.show()

solar_years = {year: None for year in years}

for year in years:
    data = DataGeneration(year = year, region = 'DK')
    solar_years[year] = data.solar['DK_solar'].values.flatten()

plt.figure(figsize=(10, 5))
for year, cf in solar_years.items():
    dates = pd.date_range(start=f'2017-01-01', end=f'2017-12-31 23:00', freq='h')
    series = pd.Series(cf, index=dates)
    monthly_avg = series.resample('M').mean()
    plt.plot(monthly_avg.index.month, monthly_avg.values, marker='o', label=str(year))
plt.xticks(range(1, 13))
plt.legend()
plt.title("Monthly Average Solar Capacity Factor")
plt.xlabel("Month")
plt.ylabel("Avg Capacity Factor")
plt.tight_layout()
plt.show()

for year, cf in solar_years.items():
    print(f"{year}: Total CF sum = {np.sum(cf):.2f}, Mean = {np.mean(cf):.5f}")
