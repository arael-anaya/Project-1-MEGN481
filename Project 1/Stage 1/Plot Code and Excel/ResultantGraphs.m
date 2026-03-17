Ty = readtable('beamPlotY.xlsx');
Tz = readtable('beamPlotZ.xlsx');

x  = Ty.x_m;          % common x

% ---- Resultant Shear ----
Vy = Ty.Shear_N;      % shear in Y
Vz = Tz.Shear_N;      % shear in Z
Vres = sqrt(Vy.^2 + Vz.^2);

% ---- Resultant Moment ----
My = Ty.Moment_Nm;    % moment about Y
Mz = Tz.Moment_Nm;    % moment about Z
Mres = sqrt(My.^2 + Mz.^2);

% ---- Plot ----
figure;

subplot(2,1,1)
plot(x, Vres, 'LineWidth', 2);
grid on;
xlabel('x [in]');
ylabel('Resultant Shear [lbf]');
title('Resultant Shear Diagram');

subplot(2,1,2)
plot(x, Mres, 'LineWidth', 2);
grid on;
xlabel('x [in]');
ylabel('Resultant Moment [lbf·in]');
title('Resultant Bending Moment Diagram');

% ---- Save tables ----
Tres = table(x, Vy, Vz, Vres, ...
    'VariableNames', {'x_m','Vy','Vz','Vresultant'});
writetable(Tres, 'beamPlotResultant.xlsx');

TresM = table(x, My, Mz, Mres, ...
    'VariableNames', {'x_m','My','Mz','Mresultant'});
writetable(TresM, 'beamPlotMomentResultant.xlsx');
