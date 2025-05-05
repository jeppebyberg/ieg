import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

rain = pd.read_csv('data/rain_data.csv', sep=';', index_col=0)

rain

# def estimate_hourly_hydro_power_mw(
#     rain_mm_per_hour,
#     area_km2,
#     head_m,
#     efficiency=0.9,
#     scaling_factor=1.0
# ):
#     """
#     Estimate average MW from rainfall per hour for a given area and head.

#     Parameters:
#     - rain_mm_per_hour: Rainfall in mm/hour at a local site
#     - area_km2: Catchment area in km²
#     - head_m: Effective head height in meters
#     - efficiency: Turbine efficiency (default 90%)
#     - scaling_factor: Multiplier to scale result to national level

#     Returns:
#     - Estimated average power in MW
#     """
#     rho = 1000      # kg/m³
#     g = 9.81        # m/s²

#     # Convert rain to volume flow (m³/hour → m³/s)
#     volume_m3_per_hour = (rain_mm_per_hour / 1000) * (area_km2 * 1e6)
#     flow_m3_per_s = volume_m3_per_hour / 3600

#     # Power in watts
#     power_watts = efficiency * rho * g * flow_m3_per_s * head_m

#     # Convert to MW
#     power_mw = power_watts / 1e6

#     return power_mw * scaling_factor

