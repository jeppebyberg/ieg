import matplotlib.pyplot as plt
from BaseNetwork import BuildBaseNetwork

class PlotDispatch():
    def __init__(self, base_network: BuildBaseNetwork):
        self.base_network = base_network      

        self.plot_dispatch()

    def plot_dispatch(self):
        generators = self.base_network.network.generators.p_nom_opt.keys()

        # SAVE AND OVERWRITE PLOTS?
        save_plots = False

        for region in self.base_network.regions:

            plt.figure(figsize=(10, 5))
            for generator in generators:
                if generator.split(' ')[1] == region:
                    if self.base_network.network.generators.p_nom_opt[generator].sum() > 10:
                        plt.plot(self.base_network.network.generators_t.p[generator][0:7 * 24], label=generator.split(' ')[0], color = self.base_network.colors[generator.split(' ')[0]])
            plt.title(f'Dispatch Winter - {region}', y=1.07)
            plt.ylabel('Generation in MWh')
            plt.grid(True, which='major',alpha=0.25)
            plt.legend()
            if save_plots:
                plt.savefig(f'./Plots/dispatch_{region}_winter.png', dpi=300, bbox_inches='tight')
            plt.show()

            plt.figure(figsize=(10, 5))
            for generator in generators:
                if generator.split(' ')[1] == region:
                    if self.base_network.network.generators.p_nom_opt[generator].sum() > 10:
                        plt.plot(self.base_network.network.generators_t.p[generator][4993: 4993 + 7 * 24], label=generator.split(' ')[0], color = self.base_network.colors[generator.split(' ')[0]])
            plt.title(f'Dispatch Summer - {region}', y=1.07)
            plt.ylabel('Generation in MWh')
            plt.legend()
            plt.grid(True, which='major',alpha=0.25)
            if save_plots:
                plt.savefig(f'./Plots/dispatch_{region}_summer.png', dpi=300, bbox_inches='tight')
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

    plot_dispatch = PlotDispatch(tmp)