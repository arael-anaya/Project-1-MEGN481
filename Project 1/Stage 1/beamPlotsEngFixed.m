%% Interactive Beam Analysis (General Supports)
% Handles Simply Supported, Cantilever, and Overhanging beams
% Separate inputs for E and I.
clc; close all;

%% -----------------------------
% 1. Beam Properties
%% -----------------------------
L = input('Enter beam length [m]: ');

% Input E and I separately
E_input = input('Enter Young''s Modulus E [Pa] (e.g., 200e9): ', 's');
E = eval(E_input);

I_input = input('Enter Area Moment of Inertia I [m^4] (e.g., (1/12)*b*h^3): ', 's');
I = eval(I_input);

% Compute Flexural Rigidity
EI = E * I;

x = linspace(0, L, 15*10^4);

%% -----------------------------
% 2. Support Definitions
%% -----------------------------
fprintf('\n--- Support Configuration ---\n');
numSupports = input('Enter number of supports (1 for Cantilever, 2 for Simply/Overhanging): ');

supLoc = zeros(1, numSupports);
for i = 1:numSupports
    supLoc(i) = input(['Enter location of support #' num2str(i) ' [m]: ']);
end
supLoc = sort(supLoc); 

isCantilever = (numSupports == 1);

%% -----------------------------
% 3. Macaulay Function
%% -----------------------------
macaulay = @(x,a,n) ((x - a).^n) .* (x >= a);

%% -----------------------------
% 4. Loads (Point, UDL, Moments)
%% -----------------------------
fprintf('\n--- Applied Loads ---\n');
numP = input('Enter number of APPLIED point loads (exclude supports): ');
P_load = zeros(1,numP); aP = zeros(1,numP);
for i = 1:numP
    P_load(i) = input(['Mag of load #' num2str(i) ' [N] (- down): ']);
    aP(i)     = input(['Loc of load #' num2str(i) ' [m]: ']);
end

numW = input('Enter number of distributed loads: ');
w = zeros(1,numW); aW = zeros(1,numW); bW = zeros(1,numW);
for i = 1:numW
    w(i)  = input(['Mag of UDL #' num2str(i) ' [N/m] (- down): ']);
    aW(i) = input(['Start loc #' num2str(i) ' [m]: ']);
    bW(i) = input(['End loc #' num2str(i) ' [m]: ']);
end

numM = input('Enter number of applied moments: ');
M_load = zeros(1,numM); aM = zeros(1,numM);
for i = 1:numM
    M_load(i) = input(['Mag of Moment #' num2str(i) ' [N*m] (+ CCW): ']);
    aM(i)     = input(['Loc of Moment #' num2str(i) ' [m]: ']);
end

%% -----------------------------
% 5. Compute Reactions
%% -----------------------------
F_ext = sum(P_load) + sum(w .* (bW - aW));
R1 = 0; R2 = 0; M_wall = 0;

if isCantilever
    x1 = supLoc(1);
    R1 = -F_ext;
    M_loads_about_x1 = sum(P_load .* (aP - x1)) + ...
                       sum(w .* (bW - aW) .* ((aW + bW)/2 - x1)) + ...
                       sum(M_load);
    M_wall = -M_loads_about_x1;
    
    fprintf('\nComputed Reactions (Fixed at %.2fm):\n', x1);
    fprintf('Force R = %.3f N\n', R1);
    fprintf('Moment M = %.3f N*m\n', M_wall);
else
    x1 = supLoc(1); x2 = supLoc(2);
    M_loads_about_x1 = sum(P_load .* (aP - x1)) + ...
                       sum(w .* (bW - aW) .* ((aW + bW)/2 - x1)) + ...
                       sum(M_load);
    R2 = -M_loads_about_x1 / (x2 - x1);
    R1 = -F_ext - R2;
    
    fprintf('\nComputed Reactions:\n');
    fprintf('R1 (at %.2fm) = %.3f N\n', x1, R1);
    fprintf('R2 (at %.2fm) = %.3f N\n', x2, R2);
end

%% -----------------------------
% 6. Shear and Moment Equations
%% -----------------------------
V = zeros(size(x)); Mx = zeros(size(x));
if isCantilever
    V  = V  + R1 * macaulay(x,supLoc(1),0);
    Mx = Mx + R1 * macaulay(x,supLoc(1),1) + M_wall * macaulay(x,supLoc(1),0);
else
    V  = V  + R1 * macaulay(x,supLoc(1),0) + R2 * macaulay(x,supLoc(2),0);
    Mx = Mx + R1 * macaulay(x,supLoc(1),1) + R2 * macaulay(x,supLoc(2),1);
end

for i = 1:numP
    V = V + P_load(i) * macaulay(x,aP(i),0);
    Mx = Mx + P_load(i) * macaulay(x,aP(i),1);
end
for i = 1:numW
    V = V + w(i) * (macaulay(x,aW(i),1) - macaulay(x,bW(i),1));
    Mx = Mx + (w(i)/2) * (macaulay(x,aW(i),2) - macaulay(x,bW(i),2));
end
for i = 1:numM
    Mx = Mx + M_load(i) * macaulay(x,aM(i),0);
end

%% -----------------------------
% 7. Analytical Integration (C1, C2)
%% -----------------------------
EI_theta_terms = zeros(size(x)); EI_y_terms = zeros(size(x));
addTerm = @(mag, loc, n) deal((mag / (n+1)) .* macaulay(x, loc, n+1), ...
                              (mag / ((n+1)*(n+2))) .* macaulay(x, loc, n+2));

if isCantilever
    [t, y_t] = addTerm(R1, supLoc(1), 1);
    EI_theta_terms = EI_theta_terms + t; EI_y_terms = EI_y_terms + y_t;
    [t, y_t] = addTerm(M_wall, supLoc(1), 0);
    EI_theta_terms = EI_theta_terms + t; EI_y_terms = EI_y_terms + y_t;
else
    [t, y_t] = addTerm(R1, supLoc(1), 1);
    EI_theta_terms = EI_theta_terms + t; EI_y_terms = EI_y_terms + y_t;
    [t, y_t] = addTerm(R2, supLoc(2), 1);
    EI_theta_terms = EI_theta_terms + t; EI_y_terms = EI_y_terms + y_t;
end

for i = 1:numP
    [t, y_t] = addTerm(P_load(i), aP(i), 1);
    EI_theta_terms = EI_theta_terms + t; EI_y_terms = EI_y_terms + y_t;
end
for i = 1:numM
    [t, y_t] = addTerm(M_load(i), aM(i), 0);
    EI_theta_terms = EI_theta_terms + t; EI_y_terms = EI_y_terms + y_t;
end
for i = 1:numW
    [t1, y1] = addTerm(w(i)/2, aW(i), 2);
    [t2, y2] = addTerm(-w(i)/2, bW(i), 2);
    EI_theta_terms = EI_theta_terms + t1 + t2; EI_y_terms = EI_y_terms + y1 + y2;
end

if isCantilever
    x1 = supLoc(1); [~, idx1] = min(abs(x - x1));
    C1 = -EI_theta_terms(idx1);
    C2 = -EI_y_terms(idx1) - (C1 * x1);
else
    x1 = supLoc(1); x2 = supLoc(2);
    [~, idx1] = min(abs(x - x1)); [~, idx2] = min(abs(x - x2));
    consts = [x1, 1; x2, 1] \ [-EI_y_terms(idx1); -EI_y_terms(idx2)];
    C1 = consts(1); C2 = consts(2);
end

fprintf('----------------------------\n');
fprintf('Integration Constants:\n');
fprintf('C1 (Slope Constant * EI)      = %.5e\n', C1);
fprintf('C2 (Deflection Constant * EI) = %.5e\n', C2);
fprintf('----------------------------\n');

theta = (EI_theta_terms + C1) / EI;
y = (EI_y_terms + C1*x + C2) / EI;

%% -----------------------------
% 8. Plotting
%% -----------------------------
sgtitle('Resultant Shear and Moment','FontSize',18,'FontWeight','bold')
% Shear
subplot(2,2,1); plot(x,V,'b','LineWidth',2); yline(0); grid on; 
title('Shear Diagram'); ylabel('V [lbf]'); axis square; xlabel('x [in]')
ax1 = gca; ax1.YAxis.Exponent = 0; ytickformat('%.2f');

% Moment
subplot(2,2,2); plot(x,Mx,'r','LineWidth',2); yline(0); grid on; 
title('Moment Diagram'); ylabel('M [lbf·in]'); axis square; xlabel('x [in]')
ax2 = gca; ax2.YAxis.Exponent = 0; ytickformat('%.2f');

%% Slope
%subplot(2,2,3); plot(x,theta,'Color','#77AC30','LineWidth',2); yline(0); grid on; 
%title('Slope Diagram'); ylabel('\theta [rad]'); axis square;
%ax3 = gca; ax3.YAxis.Exponent = 0; ytickformat('%.8f');

%% Deflection
%subplot(2,2,4); plot(x,y,'m','LineWidth',2); yline(0); grid on; 
%title('Deflection Diagram'); ylabel('y [in]'); axis square;
%ax4 = gca; ax4.YAxis.Exponent = 0; ytickformat('%.8f');