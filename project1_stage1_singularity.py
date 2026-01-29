
"""
MEGN 481 Project 1 — Stage 1 (Load Analysis)
Singularity-function shear & moment diagrams in XY and XZ planes + resultant diagrams.

How to run (from this folder):
    python project1_stage1_singularity.py

Outputs:
    plots/XY_shear.png
    plots/XY_moment.png
    plots/XZ_shear.png
    plots/XZ_moment.png
    plots/resultant_shear.png
    plots/resultant_moment.png
    plots/torque.png
    stage1_summary_values.csv   (values at key x locations)

Notes
- Coordinates follow the figure: x along shaft, y up, z as shown in the axis triad.
- Forces are point loads (lbf). Moments are in lbf*in.
- All x locations are in inches.
- Edit the "INPUTS" section to match your interpretation if your instructor specifies a different sign or magnitude.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



# Helpers: Macaulay / Heaviside

def H(x: np.ndarray, a: float) -> np.ndarray:
    """Heaviside step: 0 for x<a, 1 for x>=a."""
    return (x >= a).astype(float)

def macaulay(x: np.ndarray, a: float, n: int) -> np.ndarray:
    """<x-a>^n where < > is 0 if x<a."""
    y = x - a
    y = np.where(y >= 0, y, 0.0)
    return y**n


# Problem Inputs
L = 15.0  # total shaft length, in

# Support (bearing) locations (center of bearing)
x_b1 = 2.25
x_b2 = 12.75

# Key/gear locations 
x_gear = 10.38
x_snapring = 11.00

# End locations where wheel forces/torques act
x_left = 0.0
x_right = 15.0

# Driver load, 150 lbf total
F_driver_total = 150.0
F_end_y_each = F_driver_total / 2.0 

F_end_z_each = 0.0

# Gear forces 
F_gear_radial_y = -240.0   
F_gear_tangential_z = -740.0 

wheel_radius = 15.0 / 2.0
T_each_wheel = (F_driver_total / 2.0) * wheel_radius  # in-lbf

T_left = +T_each_wheel
T_right = +T_each_wheel
T_gear = -(T_left + T_right)  # enforce equilibrium


# Solve bearing reactions
def solve_two_support_reactions(x1, x2, loads):
    """
    Solve reactions R1, R2 for a simply-supported beam with point loads.
    loads = [(F, xF), ...] with +F positive (up or +z depending on plane).
    Equilibrium:
        R1 + R2 + sum(Fi) = 0
        Moments about x1: R2*(x2-x1) + sum(Fi*(xF-x1)) = 0
    """
    sumF = sum(F for F, _ in loads)
    sumM_about_x1 = sum(F * (xF - x1) for F, xF in loads)
    R2 = -(sumM_about_x1) / (x2 - x1)
    R1 = -sumF - R2
    return R1, R2


# Loads in Y (XY-plane bending)
loads_y = [
    (F_end_y_each, x_left),
    (F_end_y_each, x_right),
    (F_gear_radial_y, x_gear),
]
R1y, R2y = solve_two_support_reactions(x_b1, x_b2, loads_y)

# Loads in Z (XZ-plane bending)
loads_z = [
    (F_end_z_each, x_left),
    (F_end_z_each, x_right),
    (F_gear_tangential_z, x_gear),
]
R1z, R2z = solve_two_support_reactions(x_b1, x_b2, loads_z)

# Build shear & moment functions
def shear_from_point_loads(x, point_loads):
    """
    V(x) = sum Fi * H(x-a)
    point_loads = [(Fi, a), ...]
    """
    V = np.zeros_like(x, dtype=float)
    for F, a in point_loads:
        V += F * H(x, a)
    return V

def moment_from_point_loads(x, point_loads):
    """
    M(x) = sum Fi * <x-a>^1
    point_loads = [(Fi, a), ...]
    """
    M = np.zeros_like(x, dtype=float)
    for F, a in point_loads:
        M += F * macaulay(x, a, 1)
    return M

pl_y = loads_y + [(R1y, x_b1), (R2y, x_b2)]
pl_z = loads_z + [(R1z, x_b1), (R2z, x_b2)]

pl_T = [(T_left, x_left), (T_gear, x_gear), (T_right, x_right)]


def torque_from_step_torques(x, step_torques):
    """
    Internal torque T(x) for applied torques along x:
        T(x) = sum Ti * H(x-ai)
    """
    T = np.zeros_like(x, dtype=float)
    for Ti, a in step_torques:
        T += Ti * H(x, a)
    return T


x = np.linspace(0, L, 2001)

Vy = shear_from_point_loads(x, pl_y)
My = moment_from_point_loads(x, pl_y)

Vz = shear_from_point_loads(x, pl_z)
Mz = moment_from_point_loads(x, pl_z)

Vr = np.sqrt(Vy**2 + Vz**2)
Mr = np.sqrt(My**2 + Mz**2)

T = torque_from_step_torques(x, pl_T)



outdir = Path("plots")
outdir.mkdir(exist_ok=True)

def save_plot(x, y, title, ylabel, fname):
    plt.figure()
    plt.plot(x, y)
    plt.axhline(0, linewidth=1)
    plt.xlim(0, L)
    plt.xlabel("x (in)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(outdir / fname, dpi=200)
    plt.close()

save_plot(x, Vy, "Shear Diagram (XY plane): V_y(x)", "V_y (lbf)", "XY_shear.png")
save_plot(x, My, "Moment Diagram (XY plane): M_y(x)", "M_y (lbf·in)", "XY_moment.png")

save_plot(x, Vz, "Shear Diagram (XZ plane): V_z(x)", "V_z (lbf)", "XZ_shear.png")
save_plot(x, Mz, "Moment Diagram (XZ plane): M_z(x)", "M_z (lbf·in)", "XZ_moment.png")

save_plot(x, Vr, "Resultant Shear Diagram: V_r(x) = sqrt(Vy^2+Vz^2)", "V_r (lbf)", "resultant_shear.png")
save_plot(x, Mr, "Resultant Moment Diagram: M_r(x) = sqrt(My^2+Mz^2)", "M_r (lbf·in)", "resultant_moment.png")

save_plot(x, T, "Torque Diagram: T(x)", "T (lbf·in)", "torque.png")


# -----------------------------
# Table values at key x-locations
# -----------------------------
key_x = np.array([0.00, 1.75, 2.25, 2.75, 9.75, 10.38, 11.00, 12.25, 12.75, 13.25, 15.00])

def interp_at(x_query, x_grid, y_grid):
    return np.interp(x_query, x_grid, y_grid)

df = pd.DataFrame({
    "x_in": key_x,
    "Vy_lbf": interp_at(key_x, x, Vy),
    "My_lbf_in": interp_at(key_x, x, My),
    "Vz_lbf": interp_at(key_x, x, Vz),
    "Mz_lbf_in": interp_at(key_x, x, Mz),
    "Vr_lbf": interp_at(key_x, x, Vr),
    "Mr_lbf_in": interp_at(key_x, x, Mr),
    "T_lbf_in": interp_at(key_x, x, T),
})

df.to_csv("stage1_summary_values.csv", index=False)

# Print a short statics check for you to paste into your writeup
print("\n=== Bearing reactions (solved by statics) ===")
print(f"R1y @ x={x_b1:.2f} in: {R1y:+.3f} lbf")
print(f"R2y @ x={x_b2:.2f} in: {R2y:+.3f} lbf")
print(f"R1z @ x={x_b1:.2f} in: {R1z:+.3f} lbf")
print(f"R2z @ x={x_b2:.2f} in: {R2z:+.3f} lbf")
print("\nTorque inputs:")
print(f"T_left  @ x={x_left:.2f} in: {T_left:+.3f} lbf·in")
print(f"T_gear  @ x={x_gear:.2f} in: {T_gear:+.3f} lbf·in")
print(f"T_right @ x={x_right:.2f} in: {T_right:+.3f} lbf·in")

print("\nWrote plots to ./plots and values to stage1_summary_values.csv\n")
