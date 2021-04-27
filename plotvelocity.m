clc
vx = xlsread('ukf-ekf-output.xlsx','ekf-raw','C1:C499');
gvx = xlsread('ukf-ekf-output.xlsx','ekf-raw','I1:I499');
vy = xlsread('ukf-ekf-output.xlsx','ekf-raw','D1:D499');
gvy = xlsread('ukf-ekf-output.xlsx','ekf-raw','J1:J499');
t = 1:1:499;
figure(1)
plot(t,gvx,'b');
title('EKF x-axis velocity performance');
xlabel('Time step');
ylabel('Vx (m/s)');
hold on 
plot(t,vx,'r');
legend('Vx Ground truth','Vx Estiamtion')

figure(2)
plot(t,gvy,'b');
title('EKF y-axis velocity performance');
xlabel('Time step');
ylabel('Vy (m/s)');
hold on 
plot(t,vy,'r');
legend('Vy Ground truth','Vy Estiamtion')








uvx = xlsread('ukf-ekf-output.xlsx','uukf-raw','C1:C499');
ugvx = xlsread('ukf-ekf-output.xlsx','uukf-raw','I1:I499');
uvy = xlsread('ukf-ekf-output.xlsx','uukf-raw','D1:D499');
ugvy = xlsread('ukf-ekf-output.xlsx','uukf-raw','J1:J499');
t = 1:1:499;
figure(3)
plot(t,ugvx,'b');
title('UKF x-axis velocity performance');
xlabel('Time step');
ylabel('Vx (m/s)');
hold on 
plot(t,uvx,'r');
legend('Vx Ground truth','Vx Estiamtion')

figure(4)
plot(t,ugvy,'b');
title('UKF y-axis velocity performance');
xlabel('Time step');
ylabel('Vy (m/s)');
hold on 
plot(t,uvy,'r');
legend('Vy Ground truth','Vy Estiamtion')
