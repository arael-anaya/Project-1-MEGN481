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
    -168.65783365325, 2.25, ...
    -777.94601355108, 10.375, ...
    583.22399364, 12.75, ...
    0, ...       % number of distributed loads
    0 ...        % number of moments
};

% override input()
input = @(varargin) fakeInput();

beamPlotsEngFixed   % <-- NO parentheses
