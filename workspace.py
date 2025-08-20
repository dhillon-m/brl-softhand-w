########################################
# Workspace visualisation for RR wrist #
########################################

import numpy as np
import matplotlib.pyplot as plt

# Parameters (in mm)
offset = 34      # Distance between deviation and flexion axes
palm_height = 48 # Distance from flexion axis to palm center

# Joint limits (in degrees)
deviation_min, deviation_max = -30, 30
flexion_min, flexion_max = -90, 90

# Resolution
num_deviation = (deviation_max - deviation_min)
num_flexion = (flexion_max - flexion_min)

# Generate joint angle grids
deviation_angles = np.linspace(np.radians(deviation_min), np.radians(deviation_max), num_deviation)
flexion_angles = np.linspace(np.radians(flexion_min), np.radians(flexion_max), num_flexion)

# Meshgrid for all combinations
D, F = np.meshgrid(deviation_angles, flexion_angles)


# Forward kinematics using rotation matrices
# For each DoF, compute position step by step
X = np.zeros_like(D)
Y = np.zeros_like(D)
Z = np.zeros_like(D)
for i in range(D.shape[0]):
	for j in range(D.shape[1]):
		theta_dev = D[i, j]  # deviation
		theta_flex = F[i, j]  # flexion
		
		# Step 1: move to flexion axis (offset along z)
		flexion_axis = np.array([0, 0, offset])
		
		# Step 2: rotate at flexion axis
		Ry = np.array([
			[np.cos(theta_flex), 0, np.sin(theta_flex)],
			[0, 1, 0],
			[-np.sin(theta_flex), 0, np.cos(theta_flex)]
		])
		palm_local = np.array([0, 0, palm_height])
		palm_after_flexion = flexion_axis + Ry @ palm_local
		
		# Step 3: rotate at deviation axis
		Rx = np.array([
			[1, 0, 0],
			[0, np.cos(theta_dev), -np.sin(theta_dev)],
			[0, np.sin(theta_dev),  np.cos(theta_dev)]
		])
		palm_global = Rx @ palm_after_flexion
		X[i, j], Y[i, j], Z[i, j] = palm_global

# Plot
fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(X, Y, Z, s=1, c=F, cmap='viridis', alpha=0.7)
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')
ax.set_title('Wrist Workspace')
plt.tight_layout()
plt.show()
