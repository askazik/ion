import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
import os
import sys
import inspect
import seaborn as sns

sns.set()

# Make a File_Helper for saving and loading files.
save_files = True

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(current_dir)) # path to parent dir
# from DLBasics_Utilities import File_Helper
# file_helper = File_Helper(save_files)

# make starting data
np.random.seed(42)
XY = []
for i in range(7):
    bxy, bc = make_blobs(n_samples=200, centers=1, n_features=2, cluster_std=2)
    XY.append(bxy)

# show starting data. Use hand-picked colorblind-friendly colors rather than the garish defaults.
colors = ( '#582B5C', '#8CBEB2', '#9E955F', '#F3B562', '#912424',
           '#5B56D6', '#D185D6', '#408C18', '#7D3C19', '#8096BF')
plt.figure(figsize=(12,6))
plt.subplot(1,2,1)
for i in range(len(XY)):
    plt.scatter(XY[i][:,0], XY[i][:,1], c='black', edgecolors='none', s=25)
plt.title('Original data')
plt.xticks([], [])
plt.yticks([], [])

plt.subplot(1,2,2)
for i in range(len(XY)):
    plt.scatter(XY[i][:,0], XY[i][:,1], c=colors[i%len(colors)], edgecolors='none', s=25)
plt.title('Original data showing '+str(len(XY))+' clusters')
plt.xticks([], [])
plt.yticks([], [])
# file_helper.save_figure('clustering-start')
plt.show()

# reshape input data for KMeans and scatter plots
XY_points = []
scatter_x = []
scatter_y = []
for x in XY:
    XY_points.extend(x)
    scatter_x.extend(x[:,0])
    scatter_y.extend(x[:,1])

fig = plt.figure(figsize=(10,10))
for num_clusters in range(2, 11):
    kMeans = KMeans(n_clusters=num_clusters)
    kMeans.fit(XY_points)
    predictions = kMeans.predict(XY_points)
    clrs = [colors[p%len(colors)] for p in predictions]
    plt.subplot(3, 3, num_clusters-1)
    plt.scatter(scatter_x, scatter_y, c=clrs, edgecolors='none', s=7)
    plt.xticks([], [])
    plt.yticks([], [])
    plt.title(str(num_clusters)+' clusters')
# file_helper.save_figure('clustering-fits')
plt.show()
fig.show()
