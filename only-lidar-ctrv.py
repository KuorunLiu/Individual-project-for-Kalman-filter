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
                    result.append(1.0)
            else:
                result.append(float(item))
        dataset.append(result)
    f.close()
print(result)
print(dataset)
'''lists in list'''

'''initialize the covariance matrix P, 如果不确切知道最初的位置与速度，那么协方差矩阵可以初始化为一个对角线元素是B的矩阵，B取一个合适的比较大的数。'''
P = np.diag([1.0, 1.0, 1.0, 1.0, 1.0])
print(P, P.shape)
'''initialize the measurement observation matrix for lidar which is linear'''
H_lidar = np.array([[ 1.,  0.,  0.,  0.,  0.],
       [ 0.,  1.,  0.,  0.,  0.]])
print(H_lidar, H_lidar.shape)

R_lidar = np.array([[0.0225, 0.],[0., 0.0225]])
'''lidar measurement covariance matrix'''
R_radar = np.array([[0.09, 0., 0.],[0., 0.0009, 0.], [0., 0., 0.09]])
'''radar measurement covariance matrix'''
print(R_lidar, R_lidar.shape)
print(R_radar, R_radar.shape)

'''sigma_ax，sigma_ay 需要根据实际运动模型进行估量，在本项目中我们给定sigma_ax=2 sigma_yaw =0.3'''
'''process noise standard deviation for acceleration'''
std_noise_a = 2.0
'''process noise standard deviation for yaw acceleration,0.3'''
std_noise_yaw_dd = 0.3




'''在整个预测和测量更新过程中，所有角度量的数值都应该控制在 [ − π , π ] [-\pi, \pi][−π,π]，
我们知道角度加减 2 π 2\pi2π 不变，所以用如下函数表示函数来调整角度'''

def control_psi(psi):
    while (psi > np.pi or psi < -np.pi):
        if psi > np.pi:
            psi = psi - 2 * np.pi
        if psi < -np.pi:
            psi = psi + 2 * np.pi
    return psi


'''initilize the state, for lidar, we can directly use the measurement data due to the linearity,
for radar we can use x= rho*cos(theta)   y= rho*sin(theta)'''

state = np.zeros(5)
init_measurement = dataset[0]
'''the first list in dataset'''
current_time = 0.0
if init_measurement[0] == 0.0:
    print('Initialize with LIDAR measurement!')
    current_time = init_measurement[3]
    state[0] = init_measurement[1]
    state[1] = init_measurement[2]

else:
    print('Initialize with RADAR measurement!')
    current_time = init_measurement[4]
    init_rho = init_measurement[1]
    init_psi = init_measurement[2]
    init_psi = control_psi(init_psi)
    state[0] = init_rho * np.cos(init_psi)
    state[1] = init_rho * np.sin(init_psi)
print(state, state.shape)


'''写一个辅助函数用于保存数值：'''

# Preallocation for Saving
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
    vx.append(np.cos(ss[3]) * ss[2])
    vy.append(np.sin(ss[3]) * ss[2])

    gpx.append(gx)
    gpy.append(gy)
    gvx.append(gv1)
    gvy.append(gv2)
    mx.append(m1)
    my.append(m2)



'''定义状态转移函数和测量函数，使用numdifftools库来计算其对应的雅可比矩阵，
这里我们先设 Δ t = 0.05 \Delta t = 0.05Δt=0.05，只是为了占一个位置，当实际运行EKF时会计算出前后两次测量的时间差，
一次来替换这里的 Δt'''

measurement_step = len(dataset)
'''the number of rows in dataset'''
state = state.reshape([5, 1])
dt = 0.05

I = np.eye(5)
'''transition function for state when w is none zero'''
transition_function = lambda y: np.vstack((
    y[0] + (y[2] / y[4]) * (np.sin(y[3] + y[4] * dt) - np.sin(y[3])),
    y[1] + (y[2] / y[4]) * (-np.cos(y[3] + y[4] * dt) + np.cos(y[3])),
    y[2],
    y[3] + y[4] * dt,
    y[4]))
print(transition_function([1,2,4,4,4]))
# when omega is 0
'''transition function for state when w is zero'''
transition_function_1 = lambda m: np.vstack((m[0] + m[2] * np.cos(m[3]) * dt,
                                             m[1] + m[2] * np.sin(m[3]) * dt,
                                             m[2],
                                             m[3] + m[4] * dt,
                                             m[4]))

J_A = nd.Jacobian(transition_function)
J_A_1 = nd.Jacobian(transition_function_1)
print(J_A([1., 2., 3., 4., 5.]))
print(J_A_1([1., 2., 3., 4., 5.]))

measurement_function = lambda k: np.vstack((np.sqrt(k[0] * k[0] + k[1] * k[1]),
                                            math.atan2(k[1], k[0]),
                                            (k[0] * k[2] * np.cos(k[3]) + k[1] * k[2] * np.sin(k[3])) / np.sqrt(k[0] * k[0] + k[1] * k[1])))
J_H = nd.Jacobian(measurement_function)
print(J_H([1., 2., 3., 4., 5.]))

print(state)


'''EKF的过程代码：'''
'''for each row in the dataset list'''
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

    else:
        '''assign values for radar'''
        m_rho = t_measurement[1]
        m_psi = t_measurement[2]
        m_dot_rho = t_measurement[3]
        z = np.array([[m_rho], [m_psi], [m_dot_rho]])

        dt = (t_measurement[4] - current_time) / 1000000.0
        current_time = t_measurement[4]

        # true position
        g_x = t_measurement[5]
        g_y = t_measurement[6]
        g_v_x = t_measurement[7]
        g_v_y = t_measurement[8]
    '''np.ravel is combine all the list in one list'''
    '''np.ravel().tolist() is list all the elements in column'''
    if np.abs(state[4, 0]) < 0.0001:  # omega is 0, Driving straight
        '''jocabian matrix * initial state, state transition function, state extroplation, xn = f(xn-1,un=0)'''
        state = transition_function_1(state.ravel().tolist())
        state[3, 0] = control_psi(state[3, 0])
        JA = J_A_1(state.ravel().tolist())
    else:  # otherwise
        state = transition_function(state.ravel().tolist())
        state[3, 0] = control_psi(state[3, 0])
        JA = J_A(state.ravel().tolist())

    '''construct process noise matrix Q, noise_term = G matrix * acceleration array'''
    G = np.zeros([5, 2])
    G[0, 0] = 0.5 * dt * dt * np.cos(state[3, 0])
    G[1, 0] = 0.5 * dt * dt * np.sin(state[3, 0])
    G[2, 0] = dt
    G[3, 1] = 0.5 * dt * dt
    G[4, 1] = dt

    Q_v = np.diag([std_noise_a*std_noise_a, std_noise_yaw_dd*std_noise_yaw_dd])
    Q = np.dot(np.dot(G, Q_v), G.T)

    '''COVARIANCE EXTRAPOLATION EQUATION'''
    P = np.dot(np.dot(JA, P), JA.T) + Q

    # Measurement Update (Correction)
    # ===============================
    if t_measurement[0] == 0.0:
        # Lidar
        '''for lidar use the lidar observation matrix to calculate S'''
        S = np.dot(np.dot(H_lidar, P), H_lidar.T) + R_lidar
        '''calculate kalman gain'''
        K = np.dot(np.dot(P, H_lidar.T), np.linalg.inv(S))

        y = z - np.dot(H_lidar, state)
        y[1, 0] = control_psi(y[1, 0])
        '''state uptate equation'''
        '''xn+1 = xn + K(zn - h(xn))'''
        state = state + np.dot(K, y)
        state[3, 0] = control_psi(state[3, 0])
        # Update the error covariance
        '''covariance update equation'''
        P = np.dot((I - np.dot(K, H_lidar)), P)

        # Save states for Plotting
        '''ss in savestates function is the updated state list'''
        savestates(state.ravel().tolist(), g_x, g_y, g_v_x, g_v_y, m_x, m_y)

    else:
        # Radar
        '''for radar use the jocabian matrix for observation matrix '''
        JH = J_H(state.ravel().tolist())

        S = np.dot(np.dot(JH, P), JH.T) + R_radar
        K = np.dot(np.dot(P, JH.T), np.linalg.inv(S))
        map_pred = measurement_function(state.ravel().tolist())
        if np.abs(map_pred[0, 0]) < 0.0001:
            # if rho is 0
            map_pred[2, 0] = 0

        y = z - map_pred
        y[1, 0] = control_psi(y[1, 0])

        state = state + np.dot(K, y)
        state[3, 0] = control_psi(state[3, 0])
        # Update the error covariance
        P = np.dot((I - np.dot(K, JH)), P)

        savestates(state.ravel().tolist(), g_x, g_y, g_v_x, g_v_y, m_rho * np.cos(m_psi), m_rho * np.sin(m_psi))


def rmse(estimates, actual):
    result = np.sqrt(np.mean((estimates-actual)**2))
    return result

print(rmse(np.array(px), np.array(gpx)),
      rmse(np.array(py), np.array(gpy)),
      rmse(np.array(mx), np.array(gpx)),
      rmse(np.array(my), np.array(gpy)),
      rmse(np.array(vx), np.array(gvx)),
      rmse(np.array(vy), np.array(gvy)))

# write to the output file
stack = [px, py, vx, vy, mx, my, gpx, gpy, gvx, gvy]
'''transform the data from column to row'''
stack = np.array(stack)
stack = stack.T
np.savetxt('output-lidar-ctrv.txt', stack, '%.6f')
