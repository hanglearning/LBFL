import pickle
import matplotlib.pyplot as plt
import numpy as np
import os

log_base_path = '/Users/chenhang/Documents/Working'
logger_concerning = 'global_test_acc'
y_axis_label = 'Accuracy'

# draw for all devices
# for attack_type in [0, 4]:
#     for mal in [0, 3, 6, 10]:
for attack_type in [4]:
    for mal in [3, 6, 9, 10]:
        for alpha in [1.0, 100.0]:

            if (attack_type == 0 and mal != 0) or (attack_type != 0 and mal == 0):
                continue
            if attack_type == 0:
                Standalone_log_paths = [f'{log_base_path}/LBFL/logs/{folder}' for folder in os.listdir(f'{log_base_path}/LBFL/logs') if os.path.isdir(f'{log_base_path}/LBFL/logs/{folder}') and f"malicious_{mal}" in folder and "STANDALONE" in folder and f"alpha_{alpha}" in folder]
                FedAvg_log_paths = [f'{log_base_path}/LBFL/logs/{folder}' for folder in os.listdir(f'{log_base_path}/LBFL/logs') if os.path.isdir(f'{log_base_path}/LBFL/logs/{folder}') and f"malicious_{mal}" in folder and "FEDAVG" in folder and f"alpha_{alpha}" in folder]
            LBFL_log_paths = [f'{log_base_path}/LBFL/logs/{folder}' for folder in os.listdir(f'{log_base_path}/LBFL/logs') if os.path.isdir(f'{log_base_path}/LBFL/logs/{folder}') and f"mal_{mal}" in folder and f"attack_{attack_type}" in folder and f"alpha_{alpha}" in folder]
            CELL_log_paths = [f'{log_base_path}/LBFL/logs/{folder}' for folder in os.listdir(f'{log_base_path}/LBFL/logs') if os.path.isdir(f'{log_base_path}/LBFL/logs/{folder}') and f"malicious_{mal}" in folder and f"attack_{attack_type}" in folder and "CELL" in folder and f"alpha_{alpha}" in folder]
            LotteryFL_log_paths = [f'{log_base_path}/LBFL/logs/{folder}' for folder in os.listdir(f'{log_base_path}/LBFL/logs') if os.path.isdir(f'{log_base_path}/LBFL/logs/{folder}') and f"nmalicious_{mal}" in folder and f"attack_{attack_type}" in folder and f"alpha_{alpha}" in folder]
            run_names = ['LBFL', 'Standalone', 'FedAvg', 'LotteryFL'] if attack_type == 0 else ['LBFL', 'LotteryFL']
            colors = ['red', 'blue', 'green', 'purple', 'orange'] if attack_type == 0 else ['red', 'purple', 'orange']

            run_names = ['LBFL']
            for i, rn in enumerate(run_names):
                vars()[f'{rn}_avg_values_over_runs'] = []

                for lp in vars()[f'{rn}_log_paths']:
                    # Open and load the pickle file
                    with open(f'{lp}/logger.pickle', 'rb') as file:
                        logger = pickle.load(file)
                        global_accs_over_devices = []
                        for comm_round, global_test_accs in logger[logger_concerning].items():
                            global_accs_over_devices.append(list(global_test_accs.values())) # op1: convert accuracies over devices to list
                        global_accs_over_devices = list(zip(*global_accs_over_devices)) # op2: stack accuracies over devices
                        vars()[f'{rn}_avg_values_over_runs'].append(np.mean(global_accs_over_devices, axis=0)) # op3: average over the run

                mean_line = np.mean(vars()[f'{rn}_avg_values_over_runs'], axis=0)
                std = np.std(vars()[f'{rn}_avg_values_over_runs'], axis=0)

                plt.fill_between(range(1, len(mean_line) + 1), mean_line - std, mean_line + std,
                    facecolor=colors[i], # The fill color
                    color=colors[i],       # The outline color
                    alpha=0.2)          # Transparency of the fill
                plt.plot(range(1, len(mean_line) + 1), mean_line, color=colors[i], label=rn)

                # Add text annotations every 5 x-axis ticks
                x = 0
                plt.text(x + 1, mean_line[x], f'{mean_line[x]:.2f}', ha='center', va='bottom', fontsize=8, color='black')
                for x in range(4, len(mean_line), 5):
                    plt.text(x + 1, mean_line[x], f'{mean_line[x]:.2f}', ha='center', va='bottom', fontsize=8, color='black')

            plt.legend(loc='best')
            plt.xlabel('Communication Round')
            plt.ylabel(y_axis_label)
            attack_type_map = {0: 'No Attack', 1: 'Poison Attack', 2: 'Label Flipping Attack', 3: 'Lazy Attack',  4: 'Poison & Lazy'}
            plt.title(f'{" ".join(logger_concerning.split('_')).title()} - {mal} Atkers - {attack_type_map[attack_type]}, α: {alpha}')

            plt.savefig(f'{log_base_path}/LBFL/logs/avg_{logger_concerning}_mal_{mal}_attack_{attack_type}_alpha_{alpha}.png', dpi=300)

            plt.clf()