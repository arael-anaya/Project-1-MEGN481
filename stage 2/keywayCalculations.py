import numpy as np


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


def optimize_key_length(T, d, w, h, Sy, target_fos):
    """
    Solve for minimum key length L to meet target FoS.
    """

    def fos(L):
        sigma_vm = key_von_mises(T, d, L, w, h)
        return Sy / sigma_vm

    L_low = 0.01
    L_high = 5.0
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



