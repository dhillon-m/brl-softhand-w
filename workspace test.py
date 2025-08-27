import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# Symbolic setup
# -----------------------------------------------------------------------------
theta1, theta2 = sp.symbols('theta1 theta2', real=True)

def distal_DH(a, alpha, d, theta):
    """
    Standard DH homogeneous transform (assumed from context).
    a: link length
    alpha: link twist
    d: link offset
    theta: joint angle
    Returns a 4x4 sympy Matrix.
    """
    ca = sp.cos(alpha); sa = sp.sin(alpha)
    ct = sp.cos(theta); st = sp.sin(theta)
    return sp.Matrix([
        [ ct, -st*ca,  st*sa, a*ct],
        [ st,  ct*ca, -ct*sa, a*st],
        [  0,     sa,     ca,    d],
        [  0,      0,      0,    1]
    ])

# Link parameters (convert mm to m for plotting with (m) labels)
L1 = 34 / 1000.0
L2 = 48 / 1000.0

T01 = distal_DH(L1, sp.pi/2, 0, theta1)
T12 = distal_DH(L2, 0,       0, theta2)
T02 = sp.simplify(T01 * T12)

# (Row, Col) extraction replicating MATLAB (3,4), (2,4), (1,4) => 0-based (2,3),(1,3),(0,3)
px_expr = sp.simplify(T02[2, 3])
py_expr = sp.simplify(T02[1, 3])
pz_expr = sp.simplify(T02[0, 3])

# Lambdify (vectorizable with numpy)
px_func = sp.lambdify((theta1, theta2), px_expr, modules='numpy')
py_func = sp.lambdify((theta1, theta2), py_expr, modules='numpy')
pz_func = sp.lambdify((theta1, theta2), pz_expr, modules='numpy')

# -----------------------------------------------------------------------------
# Numerical evaluation
# -----------------------------------------------------------------------------
step = 1 * np.pi / 180.0  # 1 degree in radians

# Use arange with inclusive end handling
q1 = np.arange(-np.pi/6, np.pi/6 + step/2, step)   # -30° to +30°
q2 = np.arange(-np.pi/2, np.pi/2 + step/2, step)   # -90° to +90°

theta1_grid, theta2_grid = np.meshgrid(q1, q2, indexing='ij')
t1_flat = theta1_grid.ravel()
t2_flat = theta2_grid.ravel()

# Vectorized forward kinematics
px = px_func(t1_flat, t2_flat)
py = py_func(t1_flat, t2_flat)
pz = pz_func(t1_flat, t2_flat)

# -----------------------------------------------------------------------------
# Plotting
# -----------------------------------------------------------------------------
fig = plt.figure(figsize=(6, 5))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(px, py, pz, s=2, marker='o', alpha=0.1, edgecolors='none')
ax.set_title('3D Workspace View')
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
# Attempt to enforce equal aspect ratio
max_range = np.array([px.max()-px.min(), py.max()-py.min(), pz.max()-pz.min()]).max()
mid_x = (px.max()+px.min())/2
mid_y = (py.max()+py.min())/2
mid_z = (pz.max()+pz.min())/2
ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
ax.set_ylim(mid_y - max_range/2, mid_y + max_range/2)
ax.set_zlim(mid_z - max_range/2, mid_z + max_range/2)
ax.grid(True)
plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------
# Optional: print simplified expressions (comment out if not needed)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("px(theta1, theta2) =", sp.simplify(px_expr))
    print("py(theta1, theta2) =", sp.simplify(py_expr))
    print("pz(theta1, theta2) =", sp.simplify(pz_expr))