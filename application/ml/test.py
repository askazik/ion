import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import linear_model

sns.set()

np.random.seed(42)
num_pts = 1000
noise_range = 0.2
x_vals = []
y_vals = []

(x_left, x_right) = (-2, 2)
for i in range(num_pts):
    x = np.random.uniform(x_left, x_right)
    y = np.random.uniform(-noise_range, noise_range) + (2 * math.sin(x))
    x_vals.append(x)
    y_vals.append(y)
x_column = np.reshape(x_vals, [len(x_vals), 1])

ridge_estimator = linear_model.Ridge()
ridge_estimator.fit(x_column, y_vals)

(x_left, x_right) = (-1, 1)
y_left = ridge_estimator.predict(np.reshape(x_left, [1, 1]))
y_right = ridge_estimator.predict(np.reshape(x_right, [1, 1]))

fig, subplots = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True)
ax0 = fig.axes[0]
ax0.grid(True)
# ax0.text(0.1, 0.1, str(0), color='red')
ax0.plot(x_vals, y_vals, marker='.', linestyle='')

ax1 = fig.axes[1]
ax1.grid(True)
# ax1.text(0.1, 0.1, str(1), color='red')
ax1.plot(x_vals, y_vals, marker='.', linestyle='')
ax1.plot([x_left, x_right], [y_left, y_right], '-ro')

plt.show()
