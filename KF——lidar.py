from __future__ import print_function
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from scipy.stats import norm
from sympy import Symbol, symbols, Matrix, sin, cos, sqrt, atan2
from sympy import init_printing
init_printing(use_latex=True)
import numdifftools as nd
import math



dataset = []

# read the measurement data, use 0.0 to stand LIDAR data
# and 1.0 stand RADAR data
with open('data_synthetic - lidar.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip('\n')
        line = line.strip()
        numbers = line.split()
        result = []
        for i, item in enumerate(numbers):
            item.strip()
            if i == 0:
                if item == 'L':
                    result.append(0.0)
            else:
                result.append(float(item))
        dataset.append(result)
    f.close()

print(result)
print(dataset)


P = np.diag([1.0, 1.0, 1.0, 1.0])
print(P, P.shape)
'''initialize the measurement observation matrix for lidar which is linear'''
H_lidar = np.array([[ 1.,  0.,  0.,  0.],
       [ 0.,  1.,  0.,  0.]])
print(H_lidar, H_lidar.shape)

R_lidar = np.array([[0.0225, 0.],[0., 0.0225]])
'''lidar measurement covariance matrix'''


std_noise_ax = 2
std_noise_ay = 2




def control_psi(psi):
    while (psi > np.pi or psi < -np.pi):
        if psi > np.pi:
            psi = psi - 2 * np.pi
        if psi < -np.pi:
            psi = psi + 2 * np.pi
    return psi


state = np.zeros(4)
init_measurement = dataset[0]
'''the first list in dataset'''
current_time = 0.0
if init_measurement[0] == 0.0:
    print('Initialize with LIDAR measurement!')
    current_time = init_measurement[3]
    state[0] = init_measurement[1]
    state[1] = init_measurement[2]



px = []
py = []
vx = []
vy = []

gpx = []
gpy = []
gvx = []
gvy = []

mx = []
my = []

def savestates(ss, gx, gy, gv1, gv2, m1, m2):
    px.append(ss[0])
    py.append(ss[1])
    vx.append(ss[2])
    vy.append(ss[3])

    gpx.append(gx)
    gpy.append(gy)
    gvx.append(gv1)
    gvy.append(gv2)
    mx.append(m1)
    my.append(m2)



measurement_step = len(dataset)
'''the number of rows in dataset'''
state = state.reshape([4, 1])
dt = 0.05

I = np.eye(4)
transition_function = lambda y: np.vstack((
    y[0] + y[2] * dt,
    y[1] + y[3] * dt,
    y[2],
    y[3]))
F = np.array([[ 1.,  0.,  dt,  0.],[ 0.,  1.,  0.,  dt],[ 0.,  0.,  1.,  0.],[ 0.,  0.,  0.,  1.]])


for step in range(1, measurement_step):

    # Prediction
    t_measurement = dataset[step]
    if t_measurement[0] == 0.0:
        '''assign values for lidar'''
        m_x = t_measurement[1]
        m_y = t_measurement[2]
        z = np.array([[m_x], [m_y]])

        dt = (t_measurement[3] - current_time) / 1000000.0
        current_time = t_measurement[3]

        # true position
        g_x = t_measurement[4]
        g_y = t_measurement[5]
        g_v_x = t_measurement[6]
        g_v_y = t_measurement[7]

    state = np.dot(F, state)
    G = np.zeros([4, 2])
    G[0, 0] = 0.5 * dt * dt
    G[1, 1] = 0.5 * dt * dt
    G[2, 0] = dt
    G[3, 1] = dt



    Q_v = np.diag([std_noise_ax * std_noise_ax, std_noise_ay * std_noise_ay])

    Q = np.dot(np.dot(G, Q_v), G.T)
    print(Q)
    P = np.dot(np.dot(F, P), F.T) + Q


    if t_measurement[0] == 0.0:
        # Lidar
        '''for lidar use the lidar observation matrix to calculate S'''
        S = np.dot(np.dot(H_lidar, P), H_lidar.T) + R_lidar
        '''calculate kalman gain'''
        K = np.dot(np.dot(P, H_lidar.T), np.linalg.inv(S))

        y = z - np.dot(H_lidar, state)

        '''state uptate equation'''
        '''xn+1 = xn + K(zn - h(xn))'''
        state = state + np.dot(K, y)
        # Update the error covariance
        '''covariance update equation'''
        P = np.dot((I - np.dot(K, H_lidar)), P)

        # Save states for Plotting
        '''ss in savestates function is the updated state list'''
        savestates(state.ravel().tolist(), g_x, g_y, g_v_x, g_v_y, m_x, m_y)
print(state)

def rmse(estimates, actual):
    result = np.sqrt(np.mean((estimates-actual)**2))
    return result

print(rmse(np.array(px), np.array(gpx)),
      rmse(np.array(py), np.array(gpy)),
      rmse(np.array(mx), np.array(gpx)),
      rmse(np.array(my), np.array(gpy)),
      )

# write to the output file
stack = [px, py, vx, vy, mx, my, gpx, gpy, gvx, gvy]
'''transform the data from column to row'''
stack = np.array(stack)
stack = stack.T
np.savetxt('output-lidar-kf.txt', stack, '%.6f')
