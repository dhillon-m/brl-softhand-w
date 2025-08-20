import os
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_joint_angles(df, title, xlim, ylim):
    joint_cols = [f'joint_{i}_deg' for i in range(1, 7)]
    plt.figure(figsize=(10, 6))
    missing = []
    for idx, col in enumerate(joint_cols, 1):
        if col in df.columns:
            if df[col].notnull().any():
                plt.plot(df['time_s'], df[col], label=f'Joint {idx}')
            else:
                print(f"Column {col} is present but empty in {title}")
        else:
            missing.append(col)
    if missing:
        print(f"Missing joint columns in {title}: {missing}")
    plt.title(f"UR5 Joint Angles")
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (deg)")
    plt.legend()
    plt.grid(True)
    plt.xlim(xlim)
    plt.ylim(ylim)
    import numpy as np
    import matplotlib.ticker as ticker
    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax.grid(which='major', axis='x', linestyle='-', color='gray')
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    # Only annotate configuration change for rotation plots
    if title == 'Without Wrist Actuation':
        def get_joint3_min(df, start, end):
            if 'joint_3_deg' in df.columns:
                mask = (df['time_s'] >= start) & (df['time_s'] <= end)
                vals = df.loc[mask, 'joint_3_deg']
                if not vals.empty:
                    return vals.min()
            return ylim[0]
        for start, end in [(18, 31), (38, 51)]:
            ax.axvspan(start, end, color='red', alpha=0.2)
            joint3_min = get_joint3_min(df, start, end)
            y_text = joint3_min - (ylim[1] - ylim[0]) * 0.05
            ax.text((start+end)/2, y_text, 'Configuration Change', color='red',
                    ha='center', va='top', fontsize=10, fontweight='bold', rotation=0,
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='red'))
    elif title == 'With Wrist Actuation':
        def get_joint3_min(df, start, end):
            if 'joint_3_deg' in df.columns:
                mask = (df['time_s'] >= start) & (df['time_s'] <= end)
                vals = df.loc[mask, 'joint_3_deg']
                if not vals.empty:
                    return vals.min()
            return ylim[0]
        start, end = 18, 31
        ax.axvspan(start, end, color='red', alpha=0.2)
        joint3_min = get_joint3_min(df, start, end)
        y_text = joint3_min - (ylim[1] - ylim[0]) * 0.05
        ax.text((start+end)/2, y_text, 'Configuration Change', color='red',
                ha='center', va='top', fontsize=10, fontweight='bold', rotation=0,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='red'))
    # No annotation for stack plots

def plot_end_effector_path(df, title, xlim, ylim, zlim):
    pos_cols = ['x_mm', 'y_mm', 'z_mm']
    missing = [col for col in pos_cols if col not in df.columns]
    if not missing:
        if df[pos_cols].notnull().any().any():
            import numpy as np
            from matplotlib import cm
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            x = df['x_mm'].values
            y = df['y_mm'].values
            z = df['z_mm'].values
            t = df['time_s'].values if 'time_s' in df.columns else np.arange(len(x))
            norm = plt.Normalize(t.min(), t.max())
            colors = cm.viridis(norm(t))
            # Swap y and z axes for stack plots
            if 'Stack' in title:
                for i in range(len(x)-1):
                    ax.plot(x[i:i+2], z[i:i+2], y[i:i+2], color=colors[i])
                ax.set_title(f"Stack Test End Effector Path - {title}")
                ax.set_xlabel('X (mm)')
                ax.set_ylabel('Y (mm)')
                ax.set_zlabel('Z (mm)')
                ax.set_xlim(xlim)
                ax.set_ylim(zlim)
                ax.set_zlim(ylim)
            else:
                for i in range(len(x)-1):
                    ax.plot(x[i:i+2], y[i:i+2], z[i:i+2], color=colors[i])
                ax.set_title(f"Rotation Test End Effector Path - {title}")
                ax.set_xlabel('X (mm)')
                ax.set_ylabel('Y (mm)')
                ax.set_zlabel('Z (mm)')
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                ax.set_zlim(zlim)
            import matplotlib.ticker as ticker
            ax.xaxis.set_major_locator(ticker.MultipleLocator(50))
            ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
            ax.grid(which='major', axis='x', linestyle='-', color='gray')
            mappable = cm.ScalarMappable(norm=norm, cmap=cm.viridis)
            cbar = fig.colorbar(mappable, ax=ax, pad=0.1, shrink=0.6)
            cbar.set_label('Time (s)')
        else:
            print(f"End effector columns are present but empty in {title}")
    else:
        print(f"Missing columns in {title}: {missing}")

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    # Rotation test files
    wrist_csv = os.path.join(base_dir, 'rot_lrg_wrist.csv')
    no_wrist_csv = os.path.join(base_dir, 'rot_lrg_no_wrist.csv')
    # Stack test files
    stack_wrist_csv = os.path.join(base_dir, 'stack_wrist.csv')
    stack_no_wrist_csv = os.path.join(base_dir, 'stack_no_wrist.csv')

    import numpy as np
    def plot_from_files(file_label_pairs, stack=False):
        dfs = []
        times = []
        for csv_path, label in file_label_pairs:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                dfs.append((df, label))
                times.append(df['time_s'].values)
            else:
                print(f"CSV file not found: {csv_path}")
                dfs.append((None, label))
                times.append(np.array([]))
        max_time = max([t.max() if t.size > 0 else 0 for t in times])
        min_time = min([t.min() if t.size > 0 else 0 for t in times])
        xlim = (min_time, max_time)
        padded_dfs = []
        for (df, label), t in zip(dfs, times):
            if df is None or t.size == 0:
                padded_dfs.append((None, label))
                continue
            if t.max() < max_time:
                last_row = df.iloc[-1]
                pad_times = np.arange(t.max(), max_time + (t[1]-t[0] if len(t)>1 else 0), t[1]-t[0] if len(t)>1 else 0.01)
                pad_rows = pd.DataFrame([last_row.values]*len(pad_times), columns=df.columns)
                pad_rows['time_s'] = pad_times
                df = pd.concat([df, pad_rows], ignore_index=True)
            padded_dfs.append((df, label))
        joint_cols = [f'joint_{i}_deg' for i in range(1, 7)]
        pos_cols = ['x_mm', 'y_mm', 'z_mm']
        all_joint_vals = np.concatenate([df[joint_cols].values.flatten() for df, _ in padded_dfs if df is not None and all(col in df.columns for col in joint_cols)])
        ylim_joint = (np.nanmin(all_joint_vals), np.nanmax(all_joint_vals)) if all_joint_vals.size > 0 else (0, 1)
        all_x = np.concatenate([df['x_mm'].values for df, _ in padded_dfs if df is not None and 'x_mm' in df.columns])
        all_y = np.concatenate([df['y_mm'].values for df, _ in padded_dfs if df is not None and 'y_mm' in df.columns])
        all_z = np.concatenate([df['z_mm'].values for df, _ in padded_dfs if df is not None and 'z_mm' in df.columns])
        xlim_3d = (np.nanmin(all_x), np.nanmax(all_x)) if all_x.size > 0 else (0, 1)
        ylim_3d = (np.nanmin(all_y), np.nanmax(all_y)) if all_y.size > 0 else (0, 1)
        zlim_3d = (np.nanmin(all_z), np.nanmax(all_z)) if all_z.size > 0 else (0, 1)
        for df, label in padded_dfs:
            if df is not None:
                plot_joint_angles(df, label if not stack else f'Stack {label}', xlim, ylim_joint)
                plot_end_effector_path(df, label if not stack else f'Stack {label}', xlim_3d, ylim_3d, zlim_3d)

    # Plot rotation test
    plot_from_files([
        (wrist_csv, 'With Wrist Actuation'),
        (no_wrist_csv, 'Without Wrist Actuation')
    ], stack=False)
    # Plot stack test
    plot_from_files([
        (stack_wrist_csv, 'With Wrist Actuation'),
        (stack_no_wrist_csv, 'Without Wrist Actuation')
    ], stack=True)
    plt.show()

if __name__ == "__main__":
    main()
