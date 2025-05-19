# Copyright (c) 2025, John Simonis
# This code was written by John Simonis for the GreyGoo research project at The Ohio State University.
# See LICENSE.txt for more information.

import openpyxl
import pandas as pd
import numpy as np
import time
import os
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import matplotlib.cm as cm
from math import radians, cos, sin
from scipy.interpolate import RectBivariateSpline

# Create and initialize an Excel workbook with column headers for magnetic field data
def setup_excel(filename):
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Magnetic Field Data"
    sheet.append([
        "Trial", "Angle (deg)", "Sensor Height (cm)", "Radius (cm)",
        "B_x (uT)", "B_y (uT)", "B_z (uT)", "Mag (uT)",
        "B_x (G)", "B_y (G)", "B_z (G)", "Mag (G)"
    ])
    return wb, sheet

# Begin calibration process by sending command and waiting for the Magnetometer's response
# Print relevant output and errors during the process
def calibrate_sensor(ser, log_func=print, timeout=30):
    log_func("\n[Calibrating sensor — keep it still and away from magnets...]")

    try:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.1)
        ser.write(b'c')
        time.sleep(0.3)
    except Exception as e:
        log_func(f"[Serial write error] {e}")
        return

    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            log_func("[✘ Timeout waiting for calibration response]")
            break
        try:
            if ser.in_waiting > 0:
                raw = ser.readline()
                line = raw.decode('utf-8', errors='replace').strip()
                if line:
                    log_func(line)
                    if any(k in line for k in ("Baseline", "aseline", "line:")) or len(line.split()) == 3:
                        log_func("[✔ Calibration complete]")
                        break
            else:
                time.sleep(0.1)
        except Exception as e:
            log_func(f"[Decode error] {e}")
            break

# Run a full magnetic field measurement trial by rotating the turn table 360 degrees
# Parse sensor values and store them in the Excel sheet
def run_trial(ser, sheet, trial, height, radius, log_func=print):
    log_func(f"[Running trial '{trial}' — rotating and recording magnetic field...]")

    try:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.1)
        ser.write(b'r')
        time.sleep(0.3)
    except Exception as e:
        log_func(f"[Serial write error] {e}")
        return

    while True:
        try:
            if ser.in_waiting > 0:
                raw = ser.readline()
                line = raw.decode('utf-8', errors='replace').strip()
                if not line or '|' not in line:
                    continue

                log_func(line)
                angle_str, vec_str, mag_str = map(str.strip, line.split('|'))
                angle = int(angle_str)
                dx_ut, dy_ut, dz_ut = map(int, vec_str.split())
                mag_ut = float(mag_str)

                dx_g = dx_ut * 0.01
                dy_g = dy_ut * 0.01
                dz_g = dz_ut * 0.01
                mag_g = mag_ut * 0.01

                sheet.append([
                    trial, angle, height, radius,
                    dx_ut, dy_ut, dz_ut, mag_ut,
                    dx_g, dy_g, dz_g, mag_g
                ])

                if angle == 359:
                    log_func("[✔ Trial complete]")
                    break
            else:
                time.sleep(0.1)
        except Exception as e:
            log_func(f"[Error parsing line] -> {e}")
            break

# Plot the magnetic field data in 3D using different visualizations based on 'plot_choice'
def plot_data(df, filename_base, plot_choice, output_dir="", log_func=print):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    mags = df["Mag (G)"].values  # magnitude column
    norm = plt.Normalize(mags.min(), mags.max())  # color normalization
    colors = cm.viridis(norm(mags))  # apply colormap

    # containers for plotting
    all_x, all_y, all_z = [], [], []
    end_x, end_y, end_z = [], [], []
    mesh_mags = []

    VECTOR_SCALE = 0.05
    HEIGHT_MIN = df["Sensor Height (cm)"].min()
    HEIGHT_MAX = df["Sensor Height (cm)"].max()
    CENTER_HEIGHT = (HEIGHT_MIN + HEIGHT_MAX) / 2

    for i, row in df.iterrows():
        angle = row["Angle (deg)"]
        if angle >= 360:
            continue

        angle_rad = radians(angle)
        r = row["Radius (cm)"]

        # polar to Cartesian transformation
        x0 = -r * cos(angle_rad)
        z0 = r * sin(angle_rad)
        y0 = row["Sensor Height (cm)"]

        # magnetic vector components
        bx = row["B_x (G)"]
        by = row["B_y (G)"]
        bz = row["B_z (G)"]
        mag = np.sqrt(bx**2 + by**2 + bz**2)  # compute magnitude

        if mag == 0:
            continue

        # Plot mode 1: scalar points
        if plot_choice == "1":
            ax.scatter(x0, z0, y0, color=colors[i], s=20)
            all_x.append(x0)
            all_y.append(z0)
            all_z.append(y0)

        # Plot mode 2: unit vector directions
        elif plot_choice == "2":
            dx = bx / mag
            dy = bz / mag
            dz = by / mag
            ax.quiver(x0, z0, y0, dx, dy, dz, length=0.75, color=colors[i], normalize=False)
            all_x.extend([x0, x0 + dx])
            all_y.extend([z0, z0 + dy])
            all_z.extend([y0, y0 + dz])

        # Plot mode 3: scaled vector displacements
        elif plot_choice == "3":
            dx = bx * VECTOR_SCALE
            dy = bz * VECTOR_SCALE
            dz = by * VECTOR_SCALE
            ax.quiver(x0, z0, y0, dx, dy, dz, color=colors[i], normalize=False)
            all_x.extend([x0, x0 + dx])
            all_y.extend([z0, z0 + dy])
            all_z.extend([y0, y0 + dz])

        # Plot mode 4: mesh based on magnitude-deformed radius
        elif plot_choice == "4":
            MAG_SCALE = 0.85
            mag_normalized = mag / mags.max()
            shrink_factor = (1 - MAG_SCALE * (1 - mag_normalized))

            x_def = x0 * shrink_factor
            y_def = CENTER_HEIGHT + (y0 - CENTER_HEIGHT) * shrink_factor
            z_def = z0 * shrink_factor

            end_x.append(x_def)
            end_y.append(y_def)
            end_z.append(z_def)
            mesh_mags.append(mag)

    # If mesh mode, construct surface from collected points
    if plot_choice == "4":
        if len(end_x) < 4:
            log_func("[✘ Not enough points to form a mesh.]")
            return

        n_points = len(end_x)
        angles_per_layer = 360
        if n_points % angles_per_layer != 0:
            log_func(f"[✘ Point count {n_points} not divisible by {angles_per_layer}]")
            return

        n_layers = n_points // angles_per_layer
        log_func(f"[✔ Arranging as {angles_per_layer} angles × {n_layers} heights]")

        # reshape and add seam point for smooth wrapping
        X = np.array(end_x).reshape((n_layers, angles_per_layer))
        Y = np.array(end_y).reshape((n_layers, angles_per_layer))
        Z = np.array(end_z).reshape((n_layers, angles_per_layer))
        mesh_mags = np.array(mesh_mags).reshape((n_layers, angles_per_layer))

        X = np.hstack([X, X[:, 0:1]])
        Y = np.hstack([Y, Y[:, 0:1]])
        Z = np.hstack([Z, Z[:, 0:1]])
        mesh_mags = np.hstack([mesh_mags, mesh_mags[:, 0:1]])

        # generate high-res interpolation grids
        v = np.arange(X.shape[0])
        u = np.arange(X.shape[1])
        v_hr = np.linspace(0, X.shape[0]-1, X.shape[0]*4)
        u_hr = np.linspace(0, X.shape[1]-1, X.shape[1]*4)

        # Bivariate spline smoothing for each axis and magnitude
        kx = min(3, len(v)-1)
        ky = min(3, len(u)-1)

        sC = RectBivariateSpline(v, u, mesh_mags, kx=kx, ky=ky)
        sX = RectBivariateSpline(v, u, X, kx=kx, ky=ky)
        sY = RectBivariateSpline(v, u, Y, kx=kx, ky=ky)
        sZ = RectBivariateSpline(v, u, Z, kx=kx, ky=ky)

        C_hr = sC(v_hr, u_hr)
        X_hr = sX(v_hr, u_hr)
        Y_hr = sY(v_hr, u_hr)
        Z_hr = sZ(v_hr, u_hr)

        # generate color mapping and surface plot
        norm_hr = plt.Normalize(C_hr.min(), C_hr.max())
        colors_hr = cm.viridis(norm_hr(C_hr))

        surf = ax.plot_surface(
            X_hr, Z_hr, Y_hr,
            facecolors=colors_hr,
            rcount=X_hr.shape[0], ccount=X_hr.shape[1],
            linewidth=0, antialiased=False, shade=False, alpha=1.0
        )
        surf.set_alpha(1.0)

        all_x = X.flatten()
        all_y = Z.flatten()
        all_z = Y.flatten()

    # Set 3D axis limits and labels
    if len(all_x) > 0:
        RADIUS = df["Radius (cm)"].iloc[0]
        ax.set_xlim(-RADIUS*1.2, RADIUS*1.2)
        ax.set_ylim(-RADIUS*1.2, RADIUS*1.2)
        ax.set_zlim(HEIGHT_MIN-1, HEIGHT_MAX+1)
        ax.set_box_aspect([1,1,1])

    titles = {
        "1": "3D Magnetic Field Scalar Plot",
        "2": "3D Magnetic Field Vector Field (Unit Vectors)",
        "3": "3D Magnetic Field Vector Field (True Displacement)",
        "4": "3D Magnetic Field Mesh (Magnitude Deformation)"
    }
    ax.set_title(titles.get(plot_choice, "Magnetic Field Plot"), pad=20)

    ax.set_xlabel("Left ← X → Right")
    ax.set_ylabel("Backward Z Forward")
    ax.set_zlabel("Down ← Y → Up")
    plt.tight_layout()

    # Add colorbar to indicate field strength
    sm = ScalarMappable(cmap=cm.viridis, norm=norm)
    sm.set_array(mags)
    cbar = plt.colorbar(sm, ax=ax, pad=0.1)
    cbar.set_label("Magnetic Field Magnitude (Gauss)")

    # Save image with appropriate naming scheme
    plot_types = {"1":"scalar", "2":"unit_vector", "3":"true_vector", "4":"mesh_shrink"}
    plot_tag = plot_types.get(plot_choice, "unknown")
    graph_filename = f"{filename_base}_vector_field_{plot_tag}.png"
    graph_path = os.path.join(output_dir, graph_filename)
    plt.savefig(graph_path, dpi=300, bbox_inches='tight')
    log_func(f"[✔ Saved plot as '{graph_path}']")

    plt.show()
