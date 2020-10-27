import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import warnings; warnings.filterwarnings(action='once')

import numpy as np
from scipy.signal import hilbert

large = 22
med = 16
small = 12
params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (16, 10),
          'axes.labelsize': med,
          'axes.titlesize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
plt.rcParams.update(params)
plt.style.use('seaborn-whitegrid')
sns.set_style("white")


def draw_caustics(df):
    # Draw Plot
    plt.figure(figsize=(16, 10), dpi=80)
    # plt.plot('time', 'amplitude', data=df, color='tab:red', label='source')

    analytic_signal = hilbert(df.amplitude.tolist())
    amplitude_envelope = np.abs(analytic_signal)
    # instantaneous_phase = np.unwrap(np.angle(analytic_signal))

    # Decoration
    plt.yticks(fontsize=12, alpha=.7)
    plt.title("Caustics", fontsize=22)
    plt.grid(axis='both', alpha=.3)
    plt.plot(df.time.tolist(), amplitude_envelope, color='tab:blue', label='envelope')
    # plt.legend()
    # ax0.set_xlabel("time in seconds")
    # ax0.plot(t, signal, label='signal')
    # ax0.plot(t, amplitude_envelope, label='envelope')

    # Remove borders
    plt.gca().spines["top"].set_alpha(0.0)
    plt.gca().spines["bottom"].set_alpha(0.3)
    plt.gca().spines["right"].set_alpha(0.0)
    plt.gca().spines["left"].set_alpha(0.3)
    plt.show()
