import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pylab import rc, plot
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import precision_recall_curve, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


# Воспользуемся функцией построения матрицы ошибок из документации sklearn
def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


df = pd.read_csv('BigML_Dataset_5f8d3da6cb4f9607220054f9.csv')
df.head(5)

# Сделаем маппинг бинарных колонок
# и закодируем dummy-кодированием штат (для простоты, лучше не делать так для деревянных моделей)
d = {'yes': 1, 'no': 0}
df['international plan'] = df['international plan'].map(d)
df['voice mail plan'] = df['voice mail plan'].map(d)
df['churn'] = df['churn'].astype('int64')

le = LabelEncoder()
df['state'] = le.fit_transform(df['state'])

ohe = OneHotEncoder(sparse=False)
encoded_state = ohe.fit_transform(df['state'].values.reshape(-1, 1))
tmp = pd.DataFrame(encoded_state, columns=['state ' + str(i) for i in range(encoded_state.shape[1])])
df = pd.concat([df, tmp], axis=1)

# Обучение алгоритма, построение матрицы ошибок
X = df.drop('churn', axis=1).drop('phone number', axis=1)
y = df['churn']

# Делим выборку на train и test, все метрики будем оценивать на тестовом датасете
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y,  test_size=0.33, random_state=42)

# Обучаем ставшую родной логистическую регрессию
lr = LogisticRegression(random_state=42)
lr.fit(X_train, y_train)
y_test_pred = lr.predict(X_test)
print(classification_report(y_test, y_test_pred, target_names=['Non-churned', 'Churned']))

cnf_matrix = confusion_matrix(y_test, y_test_pred)

font = {'size': 15}
plt.rc('font', **font)
plt.figure(figsize=(10, 8))
plot_confusion_matrix(cnf_matrix, classes=['Non-churned', 'Churned'], title='Confusion matrix')
plt.savefig("conf_matrix.png")
plt.show()

