import numpy as np
from scipy.optimize import minimize

def key_force_from_torque(T, d):
    r = d / 2
    return T / r

def key_von_mises(T, d, L, w, H):

    F = key_force_from_torque(T, d)

    # --- Shear ---
    A_shear = L * w
    tau = F / A_shear
    sigma_vm_shear = np.sqrt(3) * tau

    # --- Bearing ---
    A_bearing = L * (H / 2)
    sigma_bearing = F / A_bearing
    sigma_vm_bearing = sigma_bearing

    return max(sigma_vm_shear, sigma_vm_bearing)

def optimize_key_geometry(T, d, Sy, target_fos,
                            bounds_L, bounds_w, bounds_H):

    def objective(x):
        L, w, H = x
        return L * w * H   # minimize volume

    def fos_constraint(x):
        L, w, H = x
        sigma_vm = key_von_mises(T, d, L, w, H)
        fos = Sy / sigma_vm
        return fos - target_fos

    constraints = [
        {'type': 'ineq', 'fun': fos_constraint}
    ]

    bounds = [bounds_L, bounds_w, bounds_H]

    x0 = [
        np.mean(bounds_L),
        np.mean(bounds_w),
        np.mean(bounds_H)
    ]

    result = minimize(objective, x0,
                        bounds=bounds,
                        constraints=constraints)

    return result.x, result
