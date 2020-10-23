from sklearn.cross_validation import KFold
import numpy as np

X = np.array(["Science today", "Data science", "Titanic", "Batman"]) #raw text
y = np.array([1, 1, 2, 2]) #categories e.g., Science, Movies
kf = KFold(y.shape[0], n_folds=2)
for train_index, test_index in kf:
    x_train, y_train = X[train_index], y[train_index]
    x_test, y_test = X[test_index], y[test_index]
    #Now continue with your pre-processing steps..
