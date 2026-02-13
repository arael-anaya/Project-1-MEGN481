import numpy as np
from scipy.optimize import minimize

STANDARD_KEYS = [
    (0.0625, 0.0625),      # 1/16" x 1/16"
    (0.09375, 0.09375),    # 3/32" x 3/32"
    (0.09375, 0.1875),     # 3/32" x 3/16"
    (0.125, 0.125),        # 1/8" x 1/8"
    (0.125, 0.1875),       # 1/8" x 3/16"
    (0.125, 0.25),         # 1/8" x 1/4"
    (0.15625, 0.15625),    # 5/32" x 5/32"
    (0.15625, 0.3125),     # 5/32" x 5/16"
    (0.1875, 0.1875),      # 3/16" x 3/16"
    (0.1875, 0.25),        # 3/16" x 1/4"
    (0.1875, 0.3125),      # 3/16" x 5/16"
    (0.1875, 0.375),       # 3/16" x 3/8"
    (0.25, 0.25),          # 1/4" x 1/4"
    (0.25, 0.3125),        # 1/4" x 5/16"
    (0.25, 0.375),         # 1/4" x 3/8"
    (0.25, 0.5),           # 1/4" x 1/2"
    (0.28125, 0.28125),    # 9/32" x 9/32"
    (0.3125, 0.3125),      # 5/16" x 5/16"
    (0.3125, 0.375),       # 5/16" x 3/8"
    (0.3125, 0.4375),      # 5/16" x 7/16"
    (0.375, 0.375),        # 3/8" x 3/8"
    (0.375, 0.5),          # 3/8" x 1/2"
    (0.375, 0.625),        # 3/8" x 5/8"
    (0.4375, 0.4375),      # 7/16" x 7/16"
    (0.4375, 0.75),        # 7/16" x 3/4"
    (0.5, 0.5),            # 1/2" x 1/2"
    (0.5, 0.75),           # 1/2" x 3/4"
    (0.5625, 0.5625),      # 9/16" x 9/16"
    (0.625, 0.625),        # 5/8" x 5/8"
    (0.6875, 0.6875),      # 11/16" x 11/16"
    (0.75, 0.75),          # 3/4" x 3/4"
    (0.8125, 0.8125),      # 13/16" x 13/16"
    (0.875, 0.875),        # 7/8" x 7/8"
    (1.0, 1.0),            # 1" x 1"
    (1.25, 1.25),          # 1 1/4" x 1 1/4"
]



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


def optimize_key_length(T, d, w, h, Sy, target_fos, L_bounds):
    L_low, L_high = L_bounds


    def fos(L):
        sigma_vm = key_von_mises(T, d, L, w, h)
        return Sy / sigma_vm

    L_mid = 0

    for _ in range(100):
        L_mid = 0.5 * (L_low + L_high)
        if fos(L_mid) > target_fos:
            L_high = L_mid
        else:
            L_low = L_mid

    return L_mid



def optimize_key_height(T, d, L, w, Sy, target_fos):
    """
    Solve for minimum key height H to meet target FoS.
    """

    def fos(H):
        sigma_vm = key_von_mises(T, d, L, w, H)
        return Sy / sigma_vm

    H_low = 0.01
    H_high = 2.0
    H_mid = 0.0

    for _ in range(100):
        H_mid = 0.5 * (H_low + H_high)

        if fos(H_mid) > target_fos:
            H_high = H_mid
        else:
            H_low = H_mid

    return H_mid


def snap_to_standard(required_w, required_H):
    for w_std, H_std in STANDARD_KEYS:
        if w_std >= required_w and H_std >= required_H:
            return w_std, H_std
    return STANDARD_KEYS[-1]  # fallback to largest


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


def discrete_key_design(T, d, Sy, target_fos,
                        bounds_L, bounds_w, bounds_H):


    solution, result = optimize_key_geometry(
        T, d, Sy, target_fos,
        bounds_L, bounds_w, bounds_H
    )

    if not result.success:
        raise RuntimeError("Key optimization did not converge.")


    L_cont, w_cont, H_cont = solution


    w_snap, H_snap = snap_to_standard(w_cont, H_cont)


    sigma_vm = key_von_mises(T, d, L_cont, w_snap, H_snap)
    fos = Sy / sigma_vm

    # If snapping lowered FoS below target, increase length
    if fos < target_fos:
        L_required = optimize_key_length(
            T, d, w_snap, H_snap, Sy, target_fos,
            L_bounds=bounds_L
        )

    else:
        L_required = L_cont

    sigma_vm = key_von_mises(T, d, L_required, w_snap, H_snap)
    fos = Sy / sigma_vm

    return L_required, w_snap, H_snap , fos

