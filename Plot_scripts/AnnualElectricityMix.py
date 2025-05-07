import matplotlib.pyplot as plt
from BaseNetwork import BuildBaseNetwork

class AnnualElectricityMix():
    def __init__(self, base_network: BuildBaseNetwork, save_plots: bool = False):
        self.base_network = base_network      
        self.save_plots = save_plots # SAVE AND OVERWRITE PLOTS?

        self.plot_electricity_mix()

    def plot_electricity_mix(self):
        generators = self.base_network.network.generators.p_nom_opt.keys()

        for region in self.base_network.regions:
                labels = []
                sizes = []
                for generator in generators:
                    if generator.split(' ')[1] == region:
                        if self.base_network.network.generators.p_nom_opt[generator] > 10:
                            labels.append(generator.split(' ')[0])
                            sizes.append(self.base_network.network.generators.p_nom_opt[generator].sum())

                # Map each label to its color
                colors = [self.base_network.colors[label] for label in labels]

                plt.pie(
                    sizes,
                    labels=labels,
                    wedgeprops={'linewidth': 0},
                    autopct='%1.1f%%',
                    colors=colors
                )

                plt.axis('equal')
                plt.title(f'Electricity mix - {region}', y=1.07)
                plt.tight_layout()

                if self.save_plots:
                    plt.savefig(f'./Plots/mix_{region}_section_D.png', dpi=300, bbox_inches='tight')
                plt.show()

if __name__ == "__main__":
    setup = {'DK': 
                    {'OCGT': True,
                    'solar': True,
                    'offwind': True,
                    'onwind': True},
            'DE': 
                    {'OCGT': True,
                    # 'solar': True,
                    'offwind': True,
                    'onwind': True,}
                    # 'CCGT': True},
                    }

    tmp = BuildBaseNetwork(setup = setup, cost_year = 2030)
    tmp.network.optimize(solver_name="gurobi",solver_options={"OutputFlag": 0})

    PlotAnnualElectricityMix = AnnualElectricityMix(tmp)
    PlotAnnualElectricityMix.plot_electricity_mix()
