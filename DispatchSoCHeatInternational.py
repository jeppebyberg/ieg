import matplotlib.pyplot as plt
from ExpandedNetwork import ExpandedNetwork
import pandas as pd

class PlotInternationalDispatchSoCHeat:
    def __init__(self, network: ExpandedNetwork, start: str, end: str):
        self.network = network.network
        self.start = start
        self.end = end

        self.plot_dispatch_and_soc(self.network, self.start, self.end)

    def plot_dispatch_and_soc(self, network, start, end):
        """
        Creates a dispatch + SOC plot for each region in a PyPSA network.

        Assumes that generator/store/link/load names end with the region name, e.g. 'solar DK'.
        """
        ts = pd.date_range(start, end, freq="h")

        # Extract full time series upfront
        generators_t = network.generators_t.p.loc[ts]
        stores_t_p = network.stores_t.p.loc[ts]
        stores_t_e = network.stores_t.e.loc[ts]
        links_t_p0 = network.links_t.p0.loc[ts]
        links_t_p1 = network.links_t.p1.loc[ts]
        loads_t = network.loads_t.p.loc[ts]

        # Infer regions from generator names (e.g., "OCGT DK")
        regions = set(bus.split()[-1] for bus in network.buses.index if "electricity bus" in bus)

        for region in sorted(regions):
            # --------------------------
            # Select components for region
            gen_cols = [col for col in generators_t.columns if col.endswith(region)]
            store_cols = [col for col in stores_t_p.columns if col.endswith(region)]
            link_cols_p1 = [col for col in links_t_p1.columns if col.endswith(region)]
            link_cols_p0 = [col for col in links_t_p0.columns if col.endswith(region)]

            region_loads = [col for col in loads_t.columns if col.endswith(region)]
            # Electricity load (e.g., 'load DK', not starting with 'heat')
            load_cols_electric = [col for col in region_loads if not col.startswith("heat")]

            # Heat load (e.g., 'heat load DK')
            load_cols_heat = [col for col in region_loads if col.startswith("heat")]

            # --------------------------
            # Prepare generation (including discharge + fuel cell)
            gen_df = generators_t[gen_cols].copy()
            for col in store_cols:
                if "battery" in col:
                    gen_df["battery storage"] = stores_t_p[col].clip(lower=0)
            for col in link_cols_p1:
                if "fuel cell" in col:
                    gen_df["fuel cell"] = -links_t_p1[col]

            gen_df = gen_df.fillna(0)
            gen_df.columns = [col.replace(f" {region}", "") for col in gen_df.columns]  # Remove region from labels
            gen_df = gen_df.sort_index(axis=1)

            # --------------------------
            # Charging
            bat_charge_df = pd.DataFrame(index=ts)
            for col in store_cols:
                name = col.replace(f" {region}", "")
                bat_charge_df[name + " charge"] = stores_t_p[col].clip(upper=0)
            for col in link_cols_p0:
                if "electrolysis" in col:
                    name = col.replace(f" {region}", "")
                    bat_charge_df["electrolyzer"] = links_t_p0[col]
                if "industrial heat pump high temperature" in col:
                    bat_charge_df["heat pump"] = links_t_p0[col]
            bat_charge_df = bat_charge_df.fillna(0)
            bat_charge_df = bat_charge_df.sort_index(axis=1)

            # --------------------------
            # Load
            total_electric_load = loads_t[load_cols_electric].sum(axis=1)
            total_heat_load = loads_t[load_cols_heat].sum(axis=1)

            # --------------------------
            # SOC
            soc_df = stores_t_e[store_cols].copy()
            soc_df.columns = [col.replace(f" {region}", "") for col in soc_df.columns]

            # --------------------------
            # --- Add interconnector flows ---
            interconnector_cols = [col for col in links_t_p0.columns if f"{region} -" in col or f"- {region}" in col]

            for col in interconnector_cols:
                raw_flow = links_t_p0[col].copy()

                # Flip sign if it's an export (region is on the left)
                if col.startswith(f"{region} -"):
                    flow = -raw_flow
                else:
                    flow = raw_flow

                # Split into positive (import) and negative (export)
                import_flow = flow.clip(lower=0)   # to gen_df
                export_flow = flow.clip(upper=0)   # to bat_charge_df

                # Extract the other region name (for label clarity)
                other_region = col.replace(region, "").replace("-", "").strip()

                gen_df[f"Import {other_region}"] = import_flow
                bat_charge_df[f"Export {other_region}"] = export_flow

            # Heat supply from links (e.g., electrolysis heat recovery)
            heat_supply_cols = [col for col in links_t_p1.columns if "heat" in col and col.endswith(region)]
            heat_supply_df = -links_t_p1[heat_supply_cols].copy()

            # Clean column names
            heat_supply_df.columns = [col.replace(f" {region}", "").replace("Link ", "") for col in heat_supply_df.columns]

            # Create three subplots: electricity dispatch, storage SOC, and heat
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
            plt.suptitle(f"Dispatch, SOC, and Heat – {region}")

            # 1️⃣ ELECTRICITY Dispatch
            ax1.stackplot(ts, gen_df.T.values, labels=gen_df.columns, alpha=0.7)
            ax1.plot(ts, total_electric_load, label="Total Load", color="black", linestyle="--", linewidth=2)
            ax1.stackplot(ts, bat_charge_df.T.values, labels=bat_charge_df.columns, alpha=0.5)
            ax1.hlines(0, xmin=ts[0], xmax=ts[-1], color="black", linewidth=1)
            ax1.set_ylabel("Electric Dispatch [MW]")
            ax1.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
            ax1.grid(True) 

            # 2️⃣ SOC
            ax2.set_title("State of Charge (SOC)")
            for column in soc_df.columns:
                ax2.plot(ts, soc_df[column], label=column, linestyle="--", linewidth=2)
            ax2.set_ylabel("SOC [MWh]")
            ax2.set_xlabel("Time")
            ax2.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
            ax2.grid(True)

            # 3️⃣ HEAT Sector
            ax3.set_title("Heat Dispatch and Demand")
            if not heat_supply_df.empty:
                ax3.stackplot(ts, heat_supply_df.T.values, labels=heat_supply_df.columns, alpha=0.7)

            ax3.plot(ts, total_heat_load, label="Heat Load", linestyle="--", linewidth=2, color="black")
            ax3.set_ylabel("Heat [MW]")
            ax3.set_xlabel("Time")
            ax3.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
            ax3.grid(True)

            plt.tight_layout()
            plt.show()
