# -*- coding: utf-8 -*-
"""qubo_minlossfunc.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/

# Qubo-nn example
"""

!git clone https://github.com/instance01/qubo-nn.git

# Commented out IPython magic to ensure Python compatibility.
# %%bash
# cd qubo-nn/
# pip3 install -r requirements.txt
# pip3 install -e .

!cd qubo-nn/qubo_nn && python3 -m qubo_nn.main -t reverse -c tsp1 --gendata
!cd qubo-nn/qubo_nn && python3 -m qubo_nn.main -t reverse -c tsp1 --train -n 1

# Commented out IPython magic to ensure Python compatibility.
# %%bash
# python3
# import shutil
# import matplotlib
# shutil.rmtree(matplotlib.get_cachedir())

# Commented out IPython magic to ensure Python compatibility.
# %%bash
# python3
# import matplotlib.font_manager as fm
# for font in fm.fontManager.ttflist:
#   print(font)

#!cd qubo-nn/qubo_nn && python3 -m qubo_nn.main -t classify -c tsp1 --gendata
!cd qubo-nn/qubo_nn && python3 -m qubo_nn.main -t classify -c tsp1 --train
#!cd qubo-nn/qubo_nn && python3 -m qubo_nn.main -t classify -c 2 --eval -m models/21-02-16_20\:28\:42-9893713-instances-MacBook-Pro.local-2

"""Above facing classification problem with the example"""







"""# Qubo Implementation"""

# set integers C
C = [2, 10, 3, 8, 5, 7, 9, 5, 3, 2]
N = len(C)

# set the above Q_{ii} & Q_{ij} as a dictionary type such as {(i, j): Q_{ij}}
Q = {}
for i in range(N):
    Q[i, i] = 4 * C[i] * (C[i] - sum(C))
    for j in range(i + 1, N):
        Q[i, j] = 8 * C[i] * C[j]

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
# %matplotlib inline

def show_qubo(qubo, cmap=cm.GnBu, save_path=None):
    n_qubo = max(sorted(qubo.keys())[-1][0], sorted(qubo.keys(), key=lambda x: x[1])[-1][1]) + 1

    np_qubo = np.zeros((n_qubo, n_qubo))
    for (pos_x, pos_y), coeff in qubo.items():
        np_qubo[pos_x][pos_y] = coeff

    plt.imshow(np_qubo, cmap=cmap)
    plt.colorbar()
    if save_path is not None:
        plt.savefig(save_path)
    plt.show()

show_qubo(Q)

#ising model
# set h_i & J_ij
h = {}
J = {}
for i in range(N):
    h[i] = 0
    for j in range(i + 1, N):
        J[i, j] = 2 * C[i] * C[j]

import dimod

# convert from ising model to QUBO
model = dimod.BinaryQuadraticModel(h, J, 0.0, vartype='SPIN')
qubo, offset = model.to_qubo()
show_qubo(qubo)

"""## D-wave implement"""

!pip install dwave-ocean-sdk

!git clone https://github.com/dwavesystems/dwave-ocean-sdk.git
!cd dwave-ocean-sdk && python setup.py install

from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from dwave.system.samplers import LeapHybridSampler

# set the connection information as an option
endpoint = 'https://cloud.dwavesys.com/sapi'
token = 'DEV-'
solver = 'DW_2000Q_6'  ## QPU solver
## list of solvers
##QPU
# DW_2000Q_6
##Hybrid
# hybrid_binary_quadratic_model_version2
# hybrid_constrained_quadratic_model_version1
# hybrid_discrete_quadratic_model_version1

# use DWaveSampler
dw = DWaveSampler(endpoint=endpoint, token=token, solver=solver) # client='base' use for hybrid solver

# embed to Chimera graph
sampler = EmbeddingComposite(dw)


# in the case of ising model, use the following
response = sampler.sample_ising(h, J, num_reads=100)

# in the case of QUBO, use the following
# response = sampler.sample_qubo(Q, num_reads=100)

response.record

def calcurate_energy(solution, vartype='BINARY'):
    if vartype == 'BINARY':
        ene = sum(C) ** 2  # offset
        for i in range(N):
            ene += Q[i, i] * solution[i]
            for j in range(i + 1, N):
                ene += Q[i, j] * solution[i] * solution[j]
    elif vartype == 'SPIN':
        ene = sum(C[i] ** 2 for i in range(N))
        for i in range(N):
            for j in range(i + 1, N):
                ene += J[i, j] * solution[i] * solution[j]
    else:
        raise ValueError("vartype mast be 'BINARY' or 'SPIN'.")

    return ene

# count the number of optimal solution
num_optimal_sol = 0
optimal_sol = []
twenty_sol = []
for state in response.record:
    # 0th contains a list of state, 2nd contains the number of occurrences in .record
    solution = state[0]
    num_oc = state[2]
    # compute energy
    energy = calcurate_energy(solution, vartype='SPIN')
    # count up the times when the energy is zero
    if energy == 0.0:
        num_optimal_sol += num_oc
        optimal_sol.append(solution)
    # preserve a result of 20 µs (we use later)
    twenty_sol.append(solution)

num_optimal_sol



for solution in optimal_sol:
    group_A = [C[i] for i, s in enumerate(solution) if s==1]
    group_B = [C[i] for i, s in enumerate(solution) if s==-1]
    print(solution)
    print('Group A: ', group_A, ', Sum = ', sum(group_A))
    print('Group B: ', group_B, ', Sum = ', sum(group_B))

response.data_vectors

response.info

#Change the number of reading

# in the case of ising model, use the following
response = sampler.sample_ising(h, J, num_reads=1000)

# in the case of QUBO, use the following
# response = sampler.sample_qubo(Q, num_reads=1000)

# count up the number of occurrences of optimal solution
num_optimal_sol = 0
optimal_sol = []
for state in response.record:
    # 0th is a list of states, 2nd is the number of occurrence in .record
    solution = state[0]
    num_oc = state[2]
    # compute energy
    energy = calcurate_energy(solution, vartype='SPIN')
    # count up the times when the energy is zero
    if energy == 0.0:
        num_optimal_sol += num_oc
        optimal_sol.append(solution)

num_optimal_sol

response.info

#Change annealing time

# In the case of ising model, use the following
response = sampler.sample_ising(h, J, num_reads=100, annealing_time=50)

# In the case of QUBO, use the following
# response = sampler.sample_qubo(Q, num_reads=100, annealing_time=50)

# count up the number of times the optimal solution was found
num_optimal_sol = 0
optimal_sol = []
fifty_sol = []
for state in response.record:
    # 0th contains a list of states, 2nd contains the number of occurrences of states in .record
    solution = state[0]
    num_oc = state[2]
    # compute energy
    energy = calcurate_energy(solution, vartype='SPIN')
    # count up when the energy is 0
    if energy == 0.0:
        num_optimal_sol += num_oc
        optimal_sol.append(solution)
    # preserve a result of 50µs
    fifty_sol.append(solution)

num_optimal_sol



plt.hist([calcurate_energy(solution, vartype='SPIN') for solution in twenty_sol], alpha=0.5, label='20μs')
plt.hist([calcurate_energy(solution, vartype='SPIN') for solution in fifty_sol], alpha=0.5, label='50μs')
plt.xlabel('Energy')
plt.ylabel('Frequency')
plt.legend()
plt.show()







"""### Qboost Classification

Reference: [https://github.com/dwavesystems/qboost/blob/master/demo.ipynb](https://github.com/dwavesystems/qboost/blob/master/demo.ipynb)
"""

!curl https://codeload.github.com/dwavesystems/qboost/zip/refs/heads/master -o qboost-master.zip

!unzip qboost-master.zip

!pip install scikit-learn dwave-system

import os
import sys

py_file_location = "/content/qboost-master/qboost"
try:
  sys.path.index(py_file_location)
except ValueError:
  print("not in list, adding it ...")
  sys.path.append(os.path.abspath(py_file_location))
  #sys.path

import qboost
qboost

# import necessary packages
from sklearn import preprocessing, metrics
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.datasets import fetch_openml
# from sklearn.datasets import load_breast_cancer
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from sklearn.impute import SimpleImputer

# set the connection information as an option
endpoint = 'https://cloud.dwavesys.com/sapi'
token = 'DEV-'
solver = 'DW_2000Q_6'  ## QPU solver
## list of solvers
##QPU
# DW_2000Q_6
##Hybrid
# hybrid_binary_quadratic_model_version2
# hybrid_constrained_quadratic_model_version1
# hybrid_discrete_quadratic_model_version1

from qboost import WeakClassifiers, QBoostClassifier, QboostPlus

import sklearn
sklearn.__version__

# Define the functions required in this example
def metric(y, y_pred):
    """
    :param y: true label
    :param y_pred: predicted label
    :return: metric score
    """

    return metrics.accuracy_score(y, y_pred)


def train_model(X_train, y_train, X_test, y_test, lmd):
    """
    :param X_train: training data
    :param y_train: training label
    :param X_test: testing data
    :param y_test: testing label
    :param lmd: lambda used in regularization
    :return:
    """

    # define parameters used in this function
    NUM_READS = 1000
    NUM_WEAK_CLASSIFIERS = 30
    TREE_DEPTH = 2
    DW_PARAMS = {'num_reads': NUM_READS,
                 'auto_scale': True,
                 'num_spin_reversal_transforms': 10,
                 'postprocess': 'optimization',
                 }

    # define sampler
    # dwave_sampler = DWaveSampler() ##
    dwave_sampler = DWaveSampler(endpoint=endpoint, token=token, solver=solver) # client='base' use for hybrid solver

    emb_sampler = EmbeddingComposite(dwave_sampler)

    N_train = len(X_train)
    N_test = len(X_test)
    print("\n======================================")
    print("Train size: %d, Test size: %d" %(N_train, N_test))
    print('Num weak classifiers:', NUM_WEAK_CLASSIFIERS)

    # Preprocessing data
    # imputer = preprocessing.Imputer()
    imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
    scaler = preprocessing.StandardScaler()
    normalizer = preprocessing.Normalizer()

    X_train = scaler.fit_transform(X_train)
    X_train = normalizer.fit_transform(X_train)

    X_test = scaler.fit_transform(X_test)
    X_test = normalizer.fit_transform(X_test)

    ## Adaboost
    print('\nAdaboost')
    clf1 = AdaBoostClassifier(n_estimators=NUM_WEAK_CLASSIFIERS)
    clf1.fit(X_train, y_train)
    y_train1 = clf1.predict(X_train)
    y_test1 = clf1.predict(X_test)
#     print(clf1.estimator_weights_)
    print('accu (train): %5.2f'%(metric(y_train, y_train1)))
    print('accu (test): %5.2f'%(metric(y_test, y_test1)))

    # Ensembles of Decision Tree
    print('\nDecision tree')
    clf2 = WeakClassifiers(n_estimators=NUM_WEAK_CLASSIFIERS, max_depth=TREE_DEPTH)
    clf2.fit(X_train, y_train)
    y_train2 = clf2.predict(X_train)
    y_test2 = clf2.predict(X_test)
#     print(clf2.estimator_weights)
    print('accu (train): %5.2f' % (metric(y_train, y_train2)))
    print('accu (test): %5.2f' % (metric(y_test, y_test2)))
    
    # Random forest
    print('\nRandom Forest')
    clf3 = RandomForestClassifier(max_depth=TREE_DEPTH, n_estimators=NUM_WEAK_CLASSIFIERS)
    clf3.fit(X_train, y_train)
    y_train3 = clf3.predict(X_train)
    y_test3 = clf3.predict(X_test)
    print('accu (train): %5.2f' % (metric(y_train, y_train3)))
    print('accu (test): %5.2f' % (metric(y_test, y_test3)))

    # Qboost
    print('\nQBoost')
    clf4 = QBoostClassifier(n_estimators=NUM_WEAK_CLASSIFIERS, max_depth=TREE_DEPTH)
    clf4.fit(X_train, y_train, emb_sampler, lmd=lmd, **DW_PARAMS) # using Dwave
    y_train4 = clf4.predict(X_train)
    y_test4 = clf4.predict(X_test)
    print(clf4.estimator_weights)
    print('accu (train): %5.2f' % (metric(y_train, y_train4)))
    print('accu (test): %5.2f' % (metric(y_test, y_test4)))

    # QboostPlus
    print('\nQBoostPlus')
    clf5 = QboostPlus([clf1, clf2, clf3, clf4])
    clf5.fit(X_train, y_train, emb_sampler, lmd=lmd, **DW_PARAMS) # using Dwave
    y_train5 = clf5.predict(X_train)
    y_test5 = clf5.predict(X_test)
    print(clf5.estimator_weights)
    print('accu (train): %5.2f' % (metric(y_train, y_train5)))
    print('accu (test): %5.2f' % (metric(y_test, y_test5)))

    print("===========================================================================")
    print("Method \t Adaboost \t DecisionTree \t RandomForest \t Qboost \t Qboost+")
    print("Train\t %5.2f \t\t %5.2f \t\t %5.2f \t\t %5.2f \t\t %5.2f"% (metric(y_train, y_train1),
                                                                         metric(y_train, y_train2),
                                                                         metric(y_train, y_train3),
                                                                         metric(y_train, y_train4),
                                                                         metric(y_train, y_train5),
                                                                        ))
    print("Test\t %5.2f \t\t %5.2f \t\t %5.2f \t\t %5.2f \t\t %5.2f"% (metric(y_test, y_test1),
                                                                       metric(y_test, y_test2),
                                                                       metric(y_test, y_test3),
                                                                       metric(y_test, y_test4),
                                                                       metric(y_test, y_test5)))
    print("===========================================================================")
    
    return [clf1, clf2, clf3, clf4, clf5]

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
#import os
import matplotlib.pyplot as plt
# %matplotlib inline

mnist = fetch_openml('mnist_784')



import pandas as pd
a = pd.Series(mnist.target).astype('int')

# idx_01 = np.where(mnist.target <= 9)[0]
idx_01 = np.where(a <= 9)[0]
np.random.shuffle(idx_01)
idx_01 = idx_01[:15000]
idx_train = idx_01[:2*len(idx_01)//3]
idx_test = idx_01[2*len(idx_01)//3:]

X_train = mnist.data.iloc[idx_train]
X_test = mnist.data.iloc[idx_test]

# y_train = 2*(mnist.target[idx_train] >4) - 1
y_train = 2*(a[idx_train] >4) - 1
# y_test = 2*(mnist.target[idx_test] >4) - 1
y_test = 2*(a[idx_test] >4) - 1

print("Training data size: (%d, %d)" %(X_train.shape))
print("Testing data size: (%d, %d)" %(X_test.shape))

## for debug
# import math
# math.sqrt(X_train.iloc[1].size)
# b=pd.Series(X_train.iloc[10])
# c=X_train.iloc[0].array
# c.reshape(28,28)

for i in range(16):
    if y_train.iloc[i] == 1:
        COLORMAP = 'gray'
    else:
        COLORMAP = 'gray_r'
    plt.subplot(4,4, i+1)
    plt.imshow(np.reshape(X_train.iloc[i].array, (28, 28)), cmap=COLORMAP)
    plt.axis('off')

# start training the model
clfs = train_model(X_train, y_train, X_test, y_test, 1.0)

"""# ML Model API

### ML Model API Example (from the slide "API Spec..pptx")
<pre>
API Name: quantum_machine_learning, classical_machine_learning
Input: Train and Test Dataset (Pandas Dataframe)
Output: Model Accuracy (Float)

def quantum_machine_learning(input_training_dataset_pd, input_testing_dataset_pd):
	model = train_machine_learning_process(input_training_dataset_pd)
	output_accuracy_float = model(input_testing_dataset_pd)
	return output_accuracy_float
</pre>
"""

!curl -o /content/titanic_train.csv https://raw.githubusercontent.com/bmwv12lmr/project-qml/main/ML_Pipeline/sprint_1/PostgreSQL/train.csv?token=

import pandas as pd
data_path = '/content/'
input_training_dataset_pd = pd.read_csv(data_path +'titanic_train.csv')

def train_machine_learning_process(input_training_dataset_pd, mode='q'): # mode: q=quantum, c=classical
  """ 
  :param input_training_dataset_pd: Train Dataset (Pandas Dataframe)
  :param mode: Training mode, q='Quantum', c='Classical'
  :return: trained_model
  """
  # dataset preparation ...
  idx_train = input_training_dataset_pd.index.values.tolist()

  if mode is 'q':
    print('doing quantum...')
    #do something for quantum
  else:
    print('doing classical...')
    #do something for classical

  trained_model = train_model(X_train, y_train, X_test, y_test, 1.0) 

  return trained_model


def model(trained_model, input_testing_dataset_pd):
  """ 
  :param trained_model: Trained mode
  :param input_testing_dataset_pd: Test Dataset (Pandas Dataframe)
  :return: output_accuracy_float
  """
  output_accuracy_float = 0.0 # some accuracy num after some process

  return output_accuracy_float


########## ML Model API ##################################################

def quantum_machine_learning(input_training_dataset_pd, input_testing_dataset_pd):
  """ 
  :quantum_machine_learning
  :param input_training_dataset_pd: Train Dataset (Pandas Dataframe)
  :param input_testing_dataset_pd: Train and Test Dataset (Pandas Dataframe)
  :return: output_accuracy_float
  """
  train_model = train_machine_learning_process(input_training_dataset_pd, mode='q') # mode: q=quantum,
  output_accuracy_float = model(train_model, input_testing_dataset_pd)
  return output_accuracy_float

def classical_machine_learning(input_training_dataset_pd, input_testing_dataset_pd):
  """ 
  :classical_machine_learning
  :param input_training_dataset_pd: Train Dataset (Pandas Dataframe)
  :param input_testing_dataset_pd: Train and Test Dataset (Pandas Dataframe)
  :return: output_accuracy_float
  """
  train_model = train_machine_learning_process(input_training_dataset_pd, mode='c') # mode: c=classical
  output_accuracy_float = model(train_model, input_testing_dataset_pd)
  return output_accuracy_float

