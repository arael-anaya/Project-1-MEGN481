import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Macaulay (singularity) function
# -----------------------------
def macaulay(x, a, n):
    """
    <x - a>^n
    """
    return np.where(x >= a, (x - a)**n, 0.0)


# -----------------------------
# Beam definition
# -----------------------------
L = 10.0                     # beam length
x = np.linspace(0, L, 2000)  # x-domain

# -----------------------------
# Reactions / Loads (EDIT HERE)
# -----------------------------

# Reactions (positive = upward)
RA = 5.0     # reaction at x=0
RB = 3.0     # reaction at x=10

# Point loads (negative = downward)
P1 = -8.0
a1 = 4.0     # location

# Distributed load
w = -2.0     # lbf/ft
a2 = 6.0     # start
b2 = 9.0     # end

# Applied moment
M0 = 10.0    # positive CCW
a3 = 2.0


# -----------------------------
# Bending moment M(x)
# -----------------------------
M = (
    RA * macaulay(x, 0, 1)                 # reaction at A
  + RB * macaulay(x, L, 1)                 # reaction at B
  + P1 * macaulay(x, a1, 1)                # point load
  + (w / 2) * (macaulay(x, a2, 2) - macaulay(x, b2, 2))  # distributed load
  + M0 * macaulay(x, a3, 0)                # applied moment
)

# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(10, 4))
plt.plot(x, M, linewidth=2)
plt.axhline(0, linewidth=0.8)
plt.xlabel("x (ft)")
plt.ylabel("Moment M(x)")
plt.title("Bending Moment Diagram (Singularity Functions)")
plt.grid(True)
plt.show()

print("gooning my shit")