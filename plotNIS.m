clc
nis_lidar = xlsread('ukf-ekf-output.xlsx','ekf-raw','M251:M499');
nis_radar = xlsread('ukf-ekf-output.xlsx','ekf-raw','M2:M250');
t = 1:1:249;
figure(1)
plot(t,nis_lidar,'b');
hold on
yline(5.991,'r','LineWidth',1);
title('Lidar NIS value for EKF');
xlabel('Time step');
ylabel('NIS value');
figure(2)
plot(t,nis_radar,'b');
hold on
yline(7.815,'r','LineWidth',1);
title('Radar NIS value for EKF');
xlabel('Time step');
ylabel('NIS value');


nis_lidar = xlsread('ukf-ekf-output.xlsx','ekf-raw','R1:R250');
nis_radar = xlsread('ukf-ekf-output.xlsx','ekf-raw','R252:R500');
t1 = 1:1:250;
t2 = 1:1:249;
figure(3)
plot(t1,nis_lidar,'b');
hold on
yline(5.991,'r','LineWidth',1);
title('Lidar NIS value for UKF');
xlabel('Time step');
ylabel('NIS value');
figure(4)
plot(t2,nis_radar,'b');
hold on
yline(7.815,'r','LineWidth',1);
title('Radar NIS value for UKF');
xlabel('Time step');
ylabel('NIS value');