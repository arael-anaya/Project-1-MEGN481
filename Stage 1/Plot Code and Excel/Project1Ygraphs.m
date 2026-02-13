% runBeamPreset.m
clear; clc;

global vals k
k = 0;

vals = { ...
    15, ...      % L
    '1', ...     % E
    '1', ...     % I
    2, ...       % number of supports
    0, 15, ...   % support locations
    3, ...       % number of point loads
    -20.714285714286, 2.25, ...
    -240, 10.375, ...
    110.714285714286, 12.75, ...
    0, ...       % number of distributed loads
    0 ...        % number of moments
};

% override input()
input = @(varargin) fakeInput();

beamPlotsEngFixed   % <-- NO parentheses
T = table(x(:), V(:), Mx(:), ...
          'VariableNames', {'x_m','Shear_N','Moment_Nm'});

writetable(T,'beamPlotY.xlsx');