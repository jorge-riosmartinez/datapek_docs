import os
import subprocess
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from tkinter import filedialog
from procesamiento_datos.imu_processor import IMUDataProcessor

# Set CustomTkinter appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Modern color scheme
COLORS = {
    "primary": "#2E7D32",  # Modern forest green
    "secondary": "#81C784",  # Light green
    "accent": "#FFCC80",  # Light orange
    "background": "#1E2B24",  # Dark green-gray
    "text": "#FFFFFF",  # White
    "text_dark": "#000000"  # Black
}

DATA_DIR = "./data"  # Folder to save data


def show_message(title, message):
    dialog = ctk.CTkToplevel(root)
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.transient(root)
    
    frame = ctk.CTkFrame(dialog)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    ctk.CTkLabel(frame, text=message, font=ctk.CTkFont(size=14)).pack(pady=20)
    
    btn = ctk.CTkButton(frame, text="Aceptar", command=dialog.destroy)
    btn.pack(pady=10)
    
    # Center the dialog
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    # Wait for the window to be visible before grabbing
    dialog.deiconify()
    dialog.focus_force()  # Give it focus
    dialog.wait_visibility()  # Wait until the window is visible
    dialog.grab_set()  # Now grab can work
    dialog.wait_window()  # Wait for the window to be closed

# Function to start the test based on user input
def start_test():
    # Get user input
    nombre_perro = entry_perro.get().strip()
    nombre_prueba = entry_prueba.get().strip()
    duracion = entry_duracion.get().strip()

    if not nombre_perro or not nombre_prueba or not duracion.isdigit():
        show_message("Error", "Todos los campos deben completarse correctamente.")
        return
    
    duracion = int(duracion)

    # Create folder if not exists (for dog and test)
    dog_folder = os.path.join(DATA_DIR, nombre_perro)  # Folder for the dog
    os.makedirs(dog_folder, exist_ok=True)
    
    # Create the folder for the test inside the dog folder
    test_folder = os.path.join(dog_folder, nombre_prueba)
    os.makedirs(test_folder, exist_ok=True)

    # Build command
    options = []
    if var_imu.get():
        options.append("--imu")
    if var_camara.get():
        options.append("--camara")
    if var_audio.get():
        options.append("--audio")
    if var_temperatura.get():
        options.append("--temperatura")

    command = ["python", "firmware/adquisicion_datos.py", "-n", nombre_perro, "-p", nombre_prueba, "-d", str(duracion)] + options

    show_message("Ejecutando", f"Iniciando prueba...\n\n{' '.join(command)}")

    # Run command in subprocess (non-blocking)
    try:
        subprocess.Popen(command)
        
        # milisecs NOT seconds
        root.after(duracion * 1000, show_test_finished)
        
        show_message("Éxito", "Prueba iniciada correctamente.")
    except Exception as e:
        show_message("Error", f"Error al ejecutar la prueba:\n{e}")


def show_test_finished():
    show_message("Prueba finalizada", "El tiempo de la prueba ha finalizado.")

# Function to create a detailed analysis report window
def create_report_window(dog_name, test_name, processed_data):
    report_window = ctk.CTkToplevel(root)
    report_window.title(f"Análisis de IMU - {dog_name}/{test_name}")
    report_window.geometry("1000x800")
    report_window.configure(fg_color=COLORS["background"])
    
    # Create a frame for the content with some padding
    main_frame = ctk.CTkFrame(report_window, corner_radius=10)
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    # Header with dog and test information
    header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=10, pady=(10, 5))
    
    ctk.CTkLabel(
        header_frame, 
        text=f"{dog_name} - {test_name}", 
        font=ctk.CTkFont(size=20, weight="bold")
    ).pack(side="left", padx=10)
    
    # Create a notebook for tabs with improved styling
    notebook = ctk.CTkTabview(main_frame, corner_radius=5, segmented_button_fg_color=COLORS["secondary"])
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create tabs
    tab_raw = notebook.add("Datos Brutos")
    tab_3d = notebook.add("Vista 3D")
    tab_accel = notebook.add("Acelerómetro")
    tab_gyro = notebook.add("Giroscopio")
    tab_path = notebook.add("Trayectoria")  # New tab for path visualization
    tab_stats = notebook.add("Estadísticas")
    
    # Tab 1: Raw Data Display with treeview
    raw_frame = ctk.CTkFrame(tab_raw)
    raw_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create a Treeview widget (table)
    from tkinter import ttk
    
    # Style configuration for the treeview
    style = ttk.Style()
    style.configure("Treeview", 
                    background=COLORS["background"],
                    foreground=COLORS["text"],
                    fieldbackground=COLORS["background"])
    style.configure("Treeview.Heading", 
                    background=COLORS["secondary"],
                    foreground=COLORS["text"])
    
    # Create treeview with scrollbars
    tree_frame = ctk.CTkFrame(raw_frame)
    tree_frame.pack(fill="both", expand=True)
    
    tree = ttk.Treeview(tree_frame)
    
    # Add scrollbars
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    vsb.pack(side='right', fill='y')
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    hsb.pack(side='bottom', fill='x')
    
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.pack(fill="both", expand=True)
    
    # Configure columns
    tree["columns"] = list(processed_data.columns)
    tree.column("#0", width=60, stretch=tk.NO)
    tree.heading("#0", text="Índice")
    
    # Set up column headers and widths
    for col in processed_data.columns:
        tree.column(col, width=80, anchor=tk.CENTER)
        tree.heading(col, text=col)
    
    # Insert data (first 100 rows)
    for i, (idx, row) in enumerate(processed_data.head(100).iterrows()):
        values = [row[col] for col in processed_data.columns]
        tree.insert("", i, text=str(idx), values=values)
    
    # Tab 2: Interactive 3D Scatter Plot
    fig_3d = plt.Figure(figsize=(7, 6), facecolor=COLORS["background"])
    ax_3d = fig_3d.add_subplot(111, projection='3d')
    
    # Create an enhanced scatter plot with larger markers and better coloring
    scatter = ax_3d.scatter(
        processed_data['acc_x'], 
        processed_data['acc_y'], 
        processed_data['acc_z'], 
        c=processed_data.index,  # Color by index for gradient effect
        cmap='viridis',
        marker='o', 
        alpha=0.8,
        s=30  # Larger point size
    )
    
    ax_3d.set_xlabel('Accel X', color=COLORS["text"], fontsize=12)
    ax_3d.set_ylabel('Accel Y', color=COLORS["text"], fontsize=12)
    ax_3d.set_zlabel('Accel Z', color=COLORS["text"], fontsize=12)
    ax_3d.set_title('Vista 3D de aceleración', color=COLORS["text"], fontsize=14)
    ax_3d.grid(True, alpha=0.3)
    ax_3d.set_facecolor(COLORS["background"])
    
    # Set tick colors
    ax_3d.tick_params(axis='x', colors=COLORS["text"])
    ax_3d.tick_params(axis='y', colors=COLORS["text"])
    ax_3d.tick_params(axis='z', colors=COLORS["text"])
    
    canvas_frame_3d = ctk.CTkFrame(tab_3d)
    canvas_frame_3d.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create figure canvas
    canvas_3d = FigureCanvasTkAgg(fig_3d, master=canvas_frame_3d)
    canvas_3d.draw()
    canvas_3d.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Add navigation toolbar for 3D plot
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
    toolbar_frame = ctk.CTkFrame(canvas_frame_3d)
    toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
    toolbar = NavigationToolbar2Tk(canvas_3d, toolbar_frame)
    toolbar.update()
    
    # Add tooltip annotations for the 3D plot
    tooltip_frame = ctk.CTkFrame(canvas_frame_3d)
    tooltip_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    tooltip_label = ctk.CTkLabel(tooltip_frame, text="Haga clic en un punto para ver detalles", font=ctk.CTkFont(size=12))
    tooltip_label.pack(side=tk.LEFT, padx=5)
    
    # Add annotation for points
    annot_3d = ax_3d.annotate("", xy=(0,0), xytext=(10,10),
                      textcoords="offset points",
                      bbox=dict(boxstyle="round", fc="w", alpha=0.7),
                      arrowprops=dict(arrowstyle="->"))
    annot_3d.set_visible(False)
    
    # Function to handle click events for 3D plot
    def on_click_3d(event):
        if event.inaxes == ax_3d:
            # Use picking for 3D plots
            cont, ind = scatter._picker(event)
            if cont:
                idx = ind["ind"][0]  # Take the first hit
                point_data = processed_data.iloc[idx]
                tooltip_text = f"Punto {idx}: X={point_data['acc_x']:.2f}, Y={point_data['acc_y']:.2f}, Z={point_data['acc_z']:.2f}"
                tooltip_label.configure(text=tooltip_text)
                
                # Update annotation
                annot_3d.xy = (point_data['acc_x'], point_data['acc_y'])
                annot_3d.set_text(tooltip_text)
                annot_3d.set_visible(True)
                fig_3d.canvas.draw_idle()
    
    fig_3d.canvas.mpl_connect('button_press_event', on_click_3d)
    
    # Tab 3: Interactive Accelerometer Time Series
    fig_accel = plt.Figure(figsize=(7, 5), facecolor=COLORS["background"])
    ax_accel = fig_accel.add_subplot(111)
    
    # Plot with clearer lines and markers for better visibility
    lines_accel = []
    lines_accel.append(ax_accel.plot(processed_data['timestamp'], processed_data['acc_x'], 
                          color=COLORS["primary"], lw=2, marker='.', markersize=3, label='X')[0])
    lines_accel.append(ax_accel.plot(processed_data['timestamp'], processed_data['acc_y'], 
                          color=COLORS["secondary"], lw=2, marker='.', markersize=3, label='Y')[0])
    lines_accel.append(ax_accel.plot(processed_data['timestamp'], processed_data['acc_z'], 
                          color=COLORS["accent"], lw=2, marker='.', markersize=3, label='Z')[0])
    
    ax_accel.set_title('Datos de acelerómetro', color=COLORS["text"], fontsize=14)
    ax_accel.set_xlabel('Tiempo (ms)', color=COLORS["text"], fontsize=12)
    ax_accel.set_ylabel('Aceleración (g)', color=COLORS["text"], fontsize=12)
    ax_accel.legend(['X', 'Y', 'Z'], loc='upper right')
    ax_accel.grid(True, alpha=0.3)
    ax_accel.set_facecolor(COLORS["background"])
    
    # Set tick colors
    ax_accel.tick_params(axis='x', colors=COLORS["text"])
    ax_accel.tick_params(axis='y', colors=COLORS["text"])
    
    # Add annotation for points
    annot_accel = ax_accel.annotate("", xy=(0,0), xytext=(10,10),
                           textcoords="offset points",
                           bbox=dict(boxstyle="round", fc="w", alpha=0.7),
                           arrowprops=dict(arrowstyle="->"))
    annot_accel.set_visible(False)
    
    canvas_frame_accel = ctk.CTkFrame(tab_accel)
    canvas_frame_accel.pack(fill="both", expand=True, padx=10, pady=10)
    
    canvas_accel = FigureCanvasTkAgg(fig_accel, master=canvas_frame_accel)
    canvas_accel.draw()
    canvas_accel.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Add navigation toolbar for accelerometer plot
    toolbar_frame_accel = ctk.CTkFrame(canvas_frame_accel)
    toolbar_frame_accel.pack(side=tk.BOTTOM, fill=tk.X)
    toolbar_accel = NavigationToolbar2Tk(canvas_accel, toolbar_frame_accel)
    toolbar_accel.update()
    
    # Add instruction label
    info_label_accel = ctk.CTkLabel(
        canvas_frame_accel, 
        text="Haga clic en un punto para ver detalles", 
        font=ctk.CTkFont(size=12)
    )
    info_label_accel.pack(side=tk.BOTTOM, pady=5)
    
    # Function to handle click for accelerometer plot
    def on_click_accel(event):
        if event.inaxes == ax_accel:
            for line in lines_accel:
                cont, ind = line.contains(event)
                if cont:
                    x, y = line.get_data()
                    idx = ind["ind"][0]
                    timestamp = x[idx]
                    value = y[idx]
                    row_idx = processed_data[processed_data['timestamp'] == timestamp].index[0]
                    
                    # Update annotation
                    annot_accel.xy = (timestamp, value)
                    text = f"T: {timestamp:.2f}\nVal: {value:.2f}\nIdx: {row_idx}"
                    annot_accel.set_text(text)
                    annot_accel.set_visible(True)
                    
                    # Update info label
                    info_label_accel.configure(text=f"Punto seleccionado: T={timestamp:.2f}ms, Valor={value:.2f}, Índice={row_idx}")
                    
                    fig_accel.canvas.draw_idle()
                    return
    
    fig_accel.canvas.mpl_connect("button_press_event", on_click_accel)
    
    # Tab 4: Interactive Gyroscope Time Series (similar to accelerometer)
    fig_gyro = plt.Figure(figsize=(7, 5), facecolor=COLORS["background"])
    ax_gyro = fig_gyro.add_subplot(111)
    
    lines_gyro = []
    lines_gyro.append(ax_gyro.plot(processed_data['timestamp'], processed_data['gyro_x'], 
                         color=COLORS["primary"], lw=2, marker='.', markersize=3, label='X')[0])
    lines_gyro.append(ax_gyro.plot(processed_data['timestamp'], processed_data['gyro_y'], 
                         color=COLORS["secondary"], lw=2, marker='.', markersize=3, label='Y')[0])
    lines_gyro.append(ax_gyro.plot(processed_data['timestamp'], processed_data['gyro_z'], 
                         color=COLORS["accent"], lw=2, marker='.', markersize=3, label='Z')[0])
    
    ax_gyro.set_title('Datos de giroscopio', color=COLORS["text"], fontsize=14)
    ax_gyro.set_xlabel('Tiempo (ms)', color=COLORS["text"], fontsize=12)
    ax_gyro.set_ylabel('Velocidad angular (°/s)', color=COLORS["text"], fontsize=12)
    ax_gyro.legend(['X', 'Y', 'Z'], loc='upper right')
    ax_gyro.grid(True, alpha=0.3)
    ax_gyro.set_facecolor(COLORS["background"])
    
    # Set tick colors
    ax_gyro.tick_params(axis='x', colors=COLORS["text"])
    ax_gyro.tick_params(axis='y', colors=COLORS["text"])
    
    # Add annotation for points
    annot_gyro = ax_gyro.annotate("", xy=(0,0), xytext=(10,10),
                         textcoords="offset points",
                         bbox=dict(boxstyle="round", fc="w", alpha=0.7),
                         arrowprops=dict(arrowstyle="->"))
    annot_gyro.set_visible(False)
    
    canvas_frame_gyro = ctk.CTkFrame(tab_gyro)
    canvas_frame_gyro.pack(fill="both", expand=True, padx=10, pady=10)
    
    canvas_gyro = FigureCanvasTkAgg(fig_gyro, master=canvas_frame_gyro)
    canvas_gyro.draw()
    canvas_gyro.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Add navigation toolbar for gyroscope plot
    toolbar_frame_gyro = ctk.CTkFrame(canvas_frame_gyro)
    toolbar_frame_gyro.pack(side=tk.BOTTOM, fill=tk.X)
    toolbar_gyro = NavigationToolbar2Tk(canvas_gyro, toolbar_frame_gyro)
    toolbar_gyro.update()
    
    # Add instruction label
    info_label_gyro = ctk.CTkLabel(
        canvas_frame_gyro, 
        text="Haga clic en un punto para ver detalles", 
        font=ctk.CTkFont(size=12)
    )
    info_label_gyro.pack(side=tk.BOTTOM, pady=5)
    
    # Function to handle click for gyroscope plot
    def on_click_gyro(event):
        if event.inaxes == ax_gyro:
            for line in lines_gyro:
                cont, ind = line.contains(event)
                if cont:
                    x, y = line.get_data()
                    idx = ind["ind"][0]
                    timestamp = x[idx]
                    value = y[idx]
                    row_idx = processed_data[processed_data['timestamp'] == timestamp].index[0]
                    
                    # Update annotation
                    annot_gyro.xy = (timestamp, value)
                    text = f"T: {timestamp:.2f}\nVal: {value:.2f}\nIdx: {row_idx}"
                    annot_gyro.set_text(text)
                    annot_gyro.set_visible(True)
                    
                    # Update info label
                    info_label_gyro.configure(text=f"Punto seleccionado: T={timestamp:.2f}ms, Valor={value:.2f}, Índice={row_idx}")
                    
                    fig_gyro.canvas.draw_idle()
                    return
    
    fig_gyro.canvas.mpl_connect("button_press_event", on_click_gyro)
    
    # Tab 5: Path Visualization with Quaternions
    import numpy as np
    
    canvas_frame_path = ctk.CTkFrame(tab_path)
    canvas_frame_path.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Function to convert quaternions to rotation matrices
    def quaternion_to_rotation_matrix(q0, q1, q2, q3):
        # Normalize quaternion
        norm = np.sqrt(q0**2 + q1**2 + q2**2 + q3**2)
        q0 = q0 / norm
        q1 = q1 / norm
        q2 = q2 / norm
        q3 = q3 / norm
        
        # Quaternion to rotation matrix
        rotation_matrix = np.array([
            [1 - 2*q2**2 - 2*q3**2, 2*q1*q2 - 2*q3*q0, 2*q1*q3 + 2*q2*q0],
            [2*q1*q2 + 2*q3*q0, 1 - 2*q1**2 - 2*q3**2, 2*q2*q3 - 2*q1*q0],
            [2*q1*q3 - 2*q2*q0, 2*q2*q3 + 2*q1*q0, 1 - 2*q1**2 - 2*q2**2]
        ])
        
        return rotation_matrix
    
    # Use quaternions to calculate position by integrating orientation and acceleration
    # This is a simplified method - for a real implementation, you'd want to use more 
    # sophisticated methods like a proper IMU fusion algorithm
    
    # Create the plot
    fig_path = plt.Figure(figsize=(7, 6), facecolor=COLORS["background"])
    ax_path = fig_path.add_subplot(111, projection='3d')
    
    # We'll reconstruct the path by integrating
    positions = np.zeros((len(processed_data), 3))
    velocities = np.zeros((len(processed_data), 3))
    dt = np.diff(processed_data['timestamp'].values) / 1000  # Convert to seconds
    dt = np.append(dt, dt[-1])  # Add one more element to match the length
    
    # Initial position
    positions[0] = [0, 0, 0]
  
    # For each timestep
    for i in range(1, len(processed_data)):
        # Get quaternion components
        q0 = processed_data.iloc[i]['q1']
        q1 = processed_data.iloc[i]['q2']
        q2 = processed_data.iloc[i]['q3']
        q3 = processed_data.iloc[i]['q4']
        
        # Get acceleration in sensor frame
        acc_sensor = np.array([
            processed_data.iloc[i]['acc_x'],
            processed_data.iloc[i]['acc_y'],
            processed_data.iloc[i]['acc_z']
        ])
        
        # Convert to world frame using quaternion
        rotation_matrix = quaternion_to_rotation_matrix(q0, q1, q2, q3)
        acc_world = rotation_matrix.dot(acc_sensor)
        
        
        # Remove gravity (approximate)
        acc_world[2] = acc_world[2] - 9.81  # Subtract gravity from Z axis
        
        # Integrate acceleration to get velocity
        velocities[i] = velocities[i-1] + acc_world * dt[i-1]
        
        # Simple low-pass filter to reduce drift
        if i > 3:  # Apply after a few samples
            velocities[i] = 0.95 * velocities[i] + 0.05 * velocities[i-1]
            
            # Zero-velocity update - if acceleration magnitude is very small,
            # assume we're stationary and reset velocity to reduce drift
            if np.linalg.norm(acc_sensor) < 0.1:  # Threshold
                velocities[i] = [0, 0, 0]
        
        # Integrate velocity to get position
        positions[i] = positions[i-1] + velocities[i] * dt[i-1]
    
    # Define colors based on comp_pred column
    color_dict = {'acostado': 'red', 'sentado': 'blue', 'caminando': 'green'}
    colors = [color_dict.get(state, 'gray') for state in processed_data['comp_pred']]
    
    # Create a colormap for the movement type
    from matplotlib.colors import ListedColormap
    unique_states = processed_data['comp_pred'].unique()
    state_to_num = {state: i for i, state in enumerate(unique_states)}
    color_indices = [state_to_num[state] for state in processed_data['comp_pred']]
    state_colors = ['red' if s == 'acostado' else 'blue' if s == 'sentado' else 'green' for s in unique_states]
    cmap = ListedColormap(state_colors)
    
    # Plot the path with colors based on the state
    scatter_path = ax_path.scatter(
        positions[:, 0], 
        positions[:, 1], 
        positions[:, 2],
        c=color_indices,
        cmap=cmap,
        s=30,
        alpha=0.8
    )
    
    # Connect points with lines to show path more clearly
    ax_path.plot(positions[:, 0], positions[:, 1], positions[:, 2], 'k-', alpha=0.3, linewidth=1)
    
    # Label the start and end points
    ax_path.scatter(positions[0, 0], positions[0, 1], positions[0, 2], color='cyan', s=100, label='Inicio')
    ax_path.scatter(positions[-1, 0], positions[-1, 1], positions[-1, 2], color='magenta', s=100, label='Fin')
    
    # Set labels and title
    ax_path.set_xlabel('X (m)', color=COLORS["text"], fontsize=12)
    ax_path.set_ylabel('Y (m)', color=COLORS["text"], fontsize=12)
    ax_path.set_zlabel('Z (m)', color=COLORS["text"], fontsize=12)
    ax_path.set_title('Trayectoria del Perro', color=COLORS["text"], fontsize=14)
    
    # Add a legend for the states
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Acostado'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Sentado'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Caminando'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='cyan', markersize=10, label='Inicio'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='magenta', markersize=10, label='Fin')
    ]
    ax_path.legend(handles=legend_elements, loc='upper right')
    
    # Make the plot look nice
    ax_path.grid(True, alpha=0.3)
    ax_path.set_facecolor(COLORS["background"])
    ax_path.tick_params(axis='x', colors=COLORS["text"])
    ax_path.tick_params(axis='y', colors=COLORS["text"])
    ax_path.tick_params(axis='z', colors=COLORS["text"])
    
    # Create canvas for the plot
    canvas_path = FigureCanvasTkAgg(fig_path, master=canvas_frame_path)
    canvas_path.draw()
    canvas_path.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Add navigation toolbar
    toolbar_frame_path = ctk.CTkFrame(canvas_frame_path)
    toolbar_frame_path.pack(side=tk.BOTTOM, fill=tk.X)
    toolbar_path = NavigationToolbar2Tk(canvas_path, toolbar_frame_path)
    toolbar_path.update()
    
    # Add instruction label
    info_label_path = ctk.CTkLabel(
        canvas_frame_path, 
        text="Haga clic en un punto para ver detalles", 
        font=ctk.CTkFont(size=12)
    )
    info_label_path.pack(side=tk.BOTTOM, pady=5)
    
    # Create annotation capability
    annot_path = ax_path.annotate("", xy=(0,0), xytext=(10,10),
                      textcoords="offset points",
                      bbox=dict(boxstyle="round", fc="w", alpha=0.7),
                      arrowprops=dict(arrowstyle="->"))
    annot_path.set_visible(False)
    
    # Function to handle click for path plot
    def on_click_path(event):
        if event.inaxes == ax_path:
            cont, ind = scatter_path.contains(event)
            if cont:
                idx = ind["ind"][0]
                pos = positions[idx]
                state = processed_data.iloc[idx]['comp_pred']
                
                # Update annotation
                annot_path.xy = (pos[0], pos[1])
                text = (f"Punto: {idx}\n"
                        f"Posición: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})\n"
                        f"Estado: {state}\n"
                        f"Tiempo: {processed_data.iloc[idx]['timestamp']:.1f}ms")
                annot_path.set_text(text)
                annot_path.set_visible(True)
                
                # Update info label
                info_label_path.configure(text=f"Punto {idx}: {state} - Tiempo: {processed_data.iloc[idx]['timestamp']:.1f}ms")
                
                fig_path.canvas.draw_idle()
    
    fig_path.canvas.mpl_connect('button_press_event', on_click_path)
    
    # Add controls for path visualization
    controls_frame = ctk.CTkFrame(canvas_frame_path)
    controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 5))
    
    # Checkbox to filter by state
    state_filters = {}
    for i, state in enumerate(['acostado', 'sentado', 'caminando']):
        var = tk.BooleanVar(value=True)
        state_filters[state] = var
        
        color = color_dict.get(state, 'gray')
        checkbutton = ctk.CTkCheckBox(
            controls_frame,
            text=state.capitalize(),
            variable=var,
            onvalue=True,
            offvalue=False,
            fg_color=color,
            hover_color=color,
            text_color=COLORS["text"]
        )
        checkbutton.pack(side=tk.LEFT, padx=10)
    
    # Function to update the plot based on state filters
    def update_path_filter():
        visible_states = [state for state, var in state_filters.items() if var.get()]
        
        # Filter data
        mask = processed_data['comp_pred'].isin(visible_states)
        
        # Update scatter plot
        scatter_path._offsets3d = (positions[mask, 0], positions[mask, 1], positions[mask, 2])
        
        # Get filtered color indices
        filtered_indices = np.array(color_indices)[mask]
        scatter_path.set_array(np.array(filtered_indices))
        
        # Redraw
        fig_path.canvas.draw_idle()
    
    # Add filter button
    filter_button = ctk.CTkButton(
        controls_frame,
        text="Aplicar Filtros",
        command=update_path_filter,
        fg_color=COLORS["primary"],
        hover_color=COLORS["secondary"]
    )
    filter_button.pack(side=tk.RIGHT, padx=10)
    
    # Tab 6: Statistics with improved tables
    stats_frame = ctk.CTkScrollableFrame(tab_stats)
    stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Calculate statistics
    accel_stats = processed_data[['acc_x', 'acc_y', 'acc_z']].describe()
    gyro_stats = processed_data[['gyro_x', 'gyro_y', 'gyro_z']].describe()
    quat_stats = processed_data[['q1', 'q2', 'q3', 'q4']].describe()  # Add quaternion stats
    
    # Accelerometer statistics table
    ctk.CTkLabel(
        stats_frame, 
        text="Estadísticas de Acelerómetro", 
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=(10, 5), anchor="w")
    
    # Create treeview for accelerometer stats
    accel_tree_frame = ctk.CTkFrame(stats_frame)
    # Function to create a detailed analysis report window
def create_report_window(dog_name, test_name, processed_data):
    report_window = ctk.CTkToplevel(root)
    report_window.title(f"Análisis de IMU - {dog_name}/{test_name}")
    report_window.geometry("1000x800")
    report_window.configure(fg_color=COLORS["background"])
    
    # Create a frame for the content with some padding
    main_frame = ctk.CTkFrame(report_window, corner_radius=10)
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    # Header with dog and test information
    header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=10, pady=(10, 5))
    
    ctk.CTkLabel(
        header_frame, 
        text=f"{dog_name} - {test_name}", 
        font=ctk.CTkFont(size=20, weight="bold")
    ).pack(side="left", padx=10)
    
    # Create a notebook for tabs with improved styling
    notebook = ctk.CTkTabview(main_frame, corner_radius=5, segmented_button_fg_color=COLORS["secondary"])
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create tabs
    tab_raw = notebook.add("Datos Brutos")
    tab_3d = notebook.add("Vista 3D")
    tab_accel = notebook.add("Acelerómetro")
    tab_gyro = notebook.add("Giroscopio")
    tab_path = notebook.add("Trayectoria")  # New tab for path visualization
    tab_stats = notebook.add("Estadísticas")
    
    # Tab 1: Raw Data Display with treeview
    raw_frame = ctk.CTkFrame(tab_raw)
    raw_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create a Treeview widget (table)
    from tkinter import ttk
    
    # Style configuration for the treeview
    style = ttk.Style()
    style.configure("Treeview", 
                    background=COLORS["background"],
                    foreground=COLORS["text"],
                    fieldbackground=COLORS["background"])
    style.configure("Treeview.Heading", 
                    background=COLORS["secondary"],
                    foreground=COLORS["text"])
    
    # Create treeview with scrollbars
    tree_frame = ctk.CTkFrame(raw_frame)
    tree_frame.pack(fill="both", expand=True)
    
    tree = ttk.Treeview(tree_frame)
    
    # Add scrollbars
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    vsb.pack(side='right', fill='y')
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    hsb.pack(side='bottom', fill='x')
    
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.pack(fill="both", expand=True)
    
    # Configure columns
    tree["columns"] = list(processed_data.columns)
    tree.column("#0", width=60, stretch=tk.NO)
    tree.heading("#0", text="Índice")
    
    # Set up column headers and widths
    for col in processed_data.columns:
        tree.column(col, width=80, anchor=tk.CENTER)
        tree.heading(col, text=col)
    
    # Insert data (first 100 rows)
    for i, (idx, row) in enumerate(processed_data.head(100).iterrows()):
        values = [row[col] for col in processed_data.columns]
        tree.insert("", i, text=str(idx), values=values)
    
    # Tab 2: Interactive 3D Scatter Plot
    fig_3d = plt.Figure(figsize=(7, 6), facecolor=COLORS["background"])
    ax_3d = fig_3d.add_subplot(111, projection='3d')
    
    # Create an enhanced scatter plot with larger markers and better coloring
    scatter = ax_3d.scatter(
        processed_data['acc_x'], 
        processed_data['acc_y'], 
        processed_data['acc_z'], 
        c=processed_data.index,  # Color by index for gradient effect
        cmap='viridis',
        marker='o', 
        alpha=0.8,
        s=30  # Larger point size
    )
    
    ax_3d.set_xlabel('Accel X', color=COLORS["text"], fontsize=12)
    ax_3d.set_ylabel('Accel Y', color=COLORS["text"], fontsize=12)
    ax_3d.set_zlabel('Accel Z', color=COLORS["text"], fontsize=12)
    ax_3d.set_title('Vista 3D de aceleración', color=COLORS["text"], fontsize=14)
    ax_3d.grid(True, alpha=0.3)
    ax_3d.set_facecolor(COLORS["background"])
    
    # Set tick colors
    ax_3d.tick_params(axis='x', colors=COLORS["text"])
    ax_3d.tick_params(axis='y', colors=COLORS["text"])
    ax_3d.tick_params(axis='z', colors=COLORS["text"])
    
    canvas_frame_3d = ctk.CTkFrame(tab_3d)
    canvas_frame_3d.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create figure canvas
    canvas_3d = FigureCanvasTkAgg(fig_3d, master=canvas_frame_3d)
    canvas_3d.draw()
    canvas_3d.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Add navigation toolbar for 3D plot
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
    toolbar_frame = ctk.CTkFrame(canvas_frame_3d)
    toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
    toolbar = NavigationToolbar2Tk(canvas_3d, toolbar_frame)
    toolbar.update()
    
    # Add tooltip annotations for the 3D plot
    tooltip_frame = ctk.CTkFrame(canvas_frame_3d)
    tooltip_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    tooltip_label = ctk.CTkLabel(tooltip_frame, text="Haga clic en un punto para ver detalles", font=ctk.CTkFont(size=12))
    tooltip_label.pack(side=tk.LEFT, padx=5)
    
    # Add annotation for points
    annot_3d = ax_3d.annotate("", xy=(0,0), xytext=(10,10),
                      textcoords="offset points",
                      bbox=dict(boxstyle="round", fc="w", alpha=0.7),
                      arrowprops=dict(arrowstyle="->"))
    annot_3d.set_visible(False)
    
    # Function to handle click events for 3D plot
    def on_click_3d(event):
        if event.inaxes == ax_3d:
            # Use picking for 3D plots
            cont, ind = scatter._picker(event)
            if cont:
                idx = ind["ind"][0]  # Take the first hit
                point_data = processed_data.iloc[idx]
                tooltip_text = f"Punto {idx}: X={point_data['acc_x']:.2f}, Y={point_data['acc_y']:.2f}, Z={point_data['acc_z']:.2f}"
                tooltip_label.configure(text=tooltip_text)
                
                # Update annotation
                annot_3d.xy = (point_data['acc_x'], point_data['acc_y'])
                annot_3d.set_text(tooltip_text)
                annot_3d.set_visible(True)
                fig_3d.canvas.draw_idle()
    
    fig_3d.canvas.mpl_connect('button_press_event', on_click_3d)
    
    # Tab 3: Interactive Accelerometer Time Series
    fig_accel = plt.Figure(figsize=(7, 5), facecolor=COLORS["background"])
    ax_accel = fig_accel.add_subplot(111)
    
    # Plot with clearer lines and markers for better visibility
    lines_accel = []
    lines_accel.append(ax_accel.plot(processed_data['timestamp'], processed_data['acc_x'], 
                          color=COLORS["primary"], lw=2, marker='.', markersize=3, label='X')[0])
    lines_accel.append(ax_accel.plot(processed_data['timestamp'], processed_data['acc_y'], 
                          color=COLORS["secondary"], lw=2, marker='.', markersize=3, label='Y')[0])
    lines_accel.append(ax_accel.plot(processed_data['timestamp'], processed_data['acc_z'], 
                          color=COLORS["accent"], lw=2, marker='.', markersize=3, label='Z')[0])
    
    ax_accel.set_title('Datos de acelerómetro', color=COLORS["text"], fontsize=14)
    ax_accel.set_xlabel('Tiempo (ms)', color=COLORS["text"], fontsize=12)
    ax_accel.set_ylabel('Aceleración (g)', color=COLORS["text"], fontsize=12)
    ax_accel.legend(['X', 'Y', 'Z'], loc='upper right')
    ax_accel.grid(True, alpha=0.3)
    ax_accel.set_facecolor(COLORS["background"])
    
    # Set tick colors
    ax_accel.tick_params(axis='x', colors=COLORS["text"])
    ax_accel.tick_params(axis='y', colors=COLORS["text"])
    
    # Add annotation for points
    annot_accel = ax_accel.annotate("", xy=(0,0), xytext=(10,10),
                           textcoords="offset points",
                           bbox=dict(boxstyle="round", fc="w", alpha=0.7),
                           arrowprops=dict(arrowstyle="->"))
    annot_accel.set_visible(False)
    
    canvas_frame_accel = ctk.CTkFrame(tab_accel)
    canvas_frame_accel.pack(fill="both", expand=True, padx=10, pady=10)
    
    canvas_accel = FigureCanvasTkAgg(fig_accel, master=canvas_frame_accel)
    canvas_accel.draw()
    canvas_accel.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Add navigation toolbar for accelerometer plot
    toolbar_frame_accel = ctk.CTkFrame(canvas_frame_accel)
    toolbar_frame_accel.pack(side=tk.BOTTOM, fill=tk.X)
    toolbar_accel = NavigationToolbar2Tk(canvas_accel, toolbar_frame_accel)
    toolbar_accel.update()
    
    # Add instruction label
    info_label_accel = ctk.CTkLabel(
        canvas_frame_accel, 
        text="Haga clic en un punto para ver detalles", 
        font=ctk.CTkFont(size=12)
    )
    info_label_accel.pack(side=tk.BOTTOM, pady=5)
    
    # Function to handle click for accelerometer plot
    def on_click_accel(event):
        if event.inaxes == ax_accel:
            for line in lines_accel:
                cont, ind = line.contains(event)
                if cont:
                    x, y = line.get_data()
                    idx = ind["ind"][0]
                    timestamp = x[idx]
                    value = y[idx]
                    row_idx = processed_data[processed_data['timestamp'] == timestamp].index[0]
                    
                    # Update annotation
                    annot_accel.xy = (timestamp, value)
                    text = f"T: {timestamp:.2f}\nVal: {value:.2f}\nIdx: {row_idx}"
                    annot_accel.set_text(text)
                    annot_accel.set_visible(True)
                    
                    # Update info label
                    info_label_accel.configure(text=f"Punto seleccionado: T={timestamp:.2f}ms, Valor={value:.2f}, Índice={row_idx}")
                    
                    fig_accel.canvas.draw_idle()
                    return
    
    fig_accel.canvas.mpl_connect("button_press_event", on_click_accel)
    
    # Tab 4: Interactive Gyroscope Time Series (similar to accelerometer)
    fig_gyro = plt.Figure(figsize=(7, 5), facecolor=COLORS["background"])
    ax_gyro = fig_gyro.add_subplot(111)
    
    lines_gyro = []
    lines_gyro.append(ax_gyro.plot(processed_data['timestamp'], processed_data['gyro_x'], 
                         color=COLORS["primary"], lw=2, marker='.', markersize=3, label='X')[0])
    lines_gyro.append(ax_gyro.plot(processed_data['timestamp'], processed_data['gyro_y'], 
                         color=COLORS["secondary"], lw=2, marker='.', markersize=3, label='Y')[0])
    lines_gyro.append(ax_gyro.plot(processed_data['timestamp'], processed_data['gyro_z'], 
                         color=COLORS["accent"], lw=2, marker='.', markersize=3, label='Z')[0])
    
    ax_gyro.set_title('Datos de giroscopio', color=COLORS["text"], fontsize=14)
    ax_gyro.set_xlabel('Tiempo (ms)', color=COLORS["text"], fontsize=12)
    ax_gyro.set_ylabel('Velocidad angular (°/s)', color=COLORS["text"], fontsize=12)
    ax_gyro.legend(['X', 'Y', 'Z'], loc='upper right')
    ax_gyro.grid(True, alpha=0.3)
    ax_gyro.set_facecolor(COLORS["background"])
    
    # Set tick colors
    ax_gyro.tick_params(axis='x', colors=COLORS["text"])
    ax_gyro.tick_params(axis='y', colors=COLORS["text"])
    
    # Add annotation for points
    annot_gyro = ax_gyro.annotate("", xy=(0,0), xytext=(10,10),
                         textcoords="offset points",
                         bbox=dict(boxstyle="round", fc="w", alpha=0.7),
                         arrowprops=dict(arrowstyle="->"))
    annot_gyro.set_visible(False)
    
    canvas_frame_gyro = ctk.CTkFrame(tab_gyro)
    canvas_frame_gyro.pack(fill="both", expand=True, padx=10, pady=10)
    
    canvas_gyro = FigureCanvasTkAgg(fig_gyro, master=canvas_frame_gyro)
    canvas_gyro.draw()
    canvas_gyro.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Add navigation toolbar for gyroscope plot
    toolbar_frame_gyro = ctk.CTkFrame(canvas_frame_gyro)
    toolbar_frame_gyro.pack(side=tk.BOTTOM, fill=tk.X)
    toolbar_gyro = NavigationToolbar2Tk(canvas_gyro, toolbar_frame_gyro)
    toolbar_gyro.update()
    
    # Add instruction label
    info_label_gyro = ctk.CTkLabel(
        canvas_frame_gyro, 
        text="Haga clic en un punto para ver detalles", 
        font=ctk.CTkFont(size=12)
    )
    info_label_gyro.pack(side=tk.BOTTOM, pady=5)
    
    # Function to handle click for gyroscope plot
    def on_click_gyro(event):
        if event.inaxes == ax_gyro:
            for line in lines_gyro:
                cont, ind = line.contains(event)
                if cont:
                    x, y = line.get_data()
                    idx = ind["ind"][0]
                    timestamp = x[idx]
                    value = y[idx]
                    row_idx = processed_data[processed_data['timestamp'] == timestamp].index[0]
                    
                    # Update annotation
                    annot_gyro.xy = (timestamp, value)
                    text = f"T: {timestamp:.2f}\nVal: {value:.2f}\nIdx: {row_idx}"
                    annot_gyro.set_text(text)
                    annot_gyro.set_visible(True)
                    
                    # Update info label
                    info_label_gyro.configure(text=f"Punto seleccionado: T={timestamp:.2f}ms, Valor={value:.2f}, Índice={row_idx}")
                    
                    fig_gyro.canvas.draw_idle()
                    return
    
    fig_gyro.canvas.mpl_connect("button_press_event", on_click_gyro)
    
    # Tab 5: Path Visualization with Quaternions
    import numpy as np
    
    canvas_frame_path = ctk.CTkFrame(tab_path)
    canvas_frame_path.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Function to convert quaternions to rotation matrices
    def quaternion_to_rotation_matrix(q0, q1, q2, q3):
        # Normalize quaternion
        norm = np.sqrt(q0**2 + q1**2 + q2**2 + q3**2)
        q0 = q0 / norm
        q1 = q1 / norm
        q2 = q2 / norm
        q3 = q3 / norm
        
        # Quaternion to rotation matrix
        rotation_matrix = np.array([
            [1 - 2*q2**2 - 2*q3**2, 2*q1*q2 - 2*q3*q0, 2*q1*q3 + 2*q2*q0],
            [2*q1*q2 + 2*q3*q0, 1 - 2*q1**2 - 2*q3**2, 2*q2*q3 - 2*q1*q0],
            [2*q1*q3 - 2*q2*q0, 2*q2*q3 + 2*q1*q0, 1 - 2*q1**2 - 2*q2**2]
        ])
        
        return rotation_matrix
    
    # Use quaternions to calculate position by integrating orientation and acceleration
    # This is a simplified method - for a real implementation, you'd want to use more 
    # sophisticated methods like a proper IMU fusion algorithm
    
    # Create the plot
    fig_path = plt.Figure(figsize=(7, 6), facecolor=COLORS["background"])
    ax_path = fig_path.add_subplot(111, projection='3d')
    
    # We'll reconstruct the path by integrating
    positions = np.zeros((len(processed_data), 3))
    velocities = np.zeros((len(processed_data), 3))
    dt = np.diff(processed_data['timestamp'].values) / 1000  # Convert to seconds
    dt = np.append(dt, dt[-1])  # Add one more element to match the length
    
    # Initial position
    positions[0] = [0, 0, 0]
    
    # For each timestep
    for i in range(1, len(processed_data)):
        # Get quaternion components
        q4 = processed_data.iloc[i]['q4']
        q4 = processed_data.iloc[i]['q4']
        q4 = processed_data.iloc[i]['q4']
        q4 = processed_data.iloc[i]['q4']
        
        # Get acceleration in sensor frame
        acc_sensor = np.array([
            processed_data.iloc[i]['acc_x'],
            processed_data.iloc[i]['acc_y'],
            processed_data.iloc[i]['acc_z']
        ])
        
        # Convert to world frame using quaternion
        rotation_matrix = quaternion_to_rotation_matrix(q4, q4, q4, q4)
        acc_world = rotation_matrix.dot(acc_sensor)
        
        # Remove gravity (approximate)
        acc_world[2] = acc_world[2] - 9.81  # Subtract gravity from Z axis
        
        # Integrate acceleration to get velocity
        velocities[i] = velocities[i-1] + acc_world * dt[i-1]
        
        # Simple low-pass filter to reduce drift
        if i > 3:  # Apply after a few samples
            velocities[i] = 0.95 * velocities[i] + 0.05 * velocities[i-1]
            
            # Zero-velocity update - if acceleration magnitude is very small,
            # assume we're stationary and reset velocity to reduce drift
            if np.linalg.norm(acc_sensor) < 0.1:  # Threshold
                velocities[i] = [0, 0, 0]
        
        # Integrate velocity to get position
        positions[i] = positions[i-1] + velocities[i] * dt[i-1]
    
    # Define colors based on comp_pred column
    color_dict = {'acostado': 'red', 'sentado': 'blue', 'caminando': 'green'}
    colors = [color_dict.get(state, 'gray') for state in processed_data['comp_pred']]
    
    # Create a colormap for the movement type
    from matplotlib.colors import ListedColormap
    unique_states = processed_data['comp_pred'].unique()
    state_to_num = {state: i for i, state in enumerate(unique_states)}
    color_indices = [state_to_num[state] for state in processed_data['comp_pred']]
    state_colors = ['red' if s == 'acostado' else 'blue' if s == 'sentado' else 'green' for s in unique_states]
    cmap = ListedColormap(state_colors)
    
    # Plot the path with colors based on the state
    scatter_path = ax_path.scatter(
        positions[:, 0], 
        positions[:, 1], 
        positions[:, 2],
        c=color_indices,
        cmap=cmap,
        s=30,
        alpha=0.8
    )
    
    # Connect points with lines to show path more clearly
    ax_path.plot(positions[:, 0], positions[:, 1], positions[:, 2], 'k-', alpha=0.3, linewidth=1)
    
    # Label the start and end points
    ax_path.scatter(positions[0, 0], positions[0, 1], positions[0, 2], color='cyan', s=100, label='Inicio')
    ax_path.scatter(positions[-1, 0], positions[-1, 1], positions[-1, 2], color='magenta', s=100, label='Fin')
    
    # Set labels and title
    ax_path.set_xlabel('X (m)', color=COLORS["text"], fontsize=12)
    ax_path.set_ylabel('Y (m)', color=COLORS["text"], fontsize=12)
    ax_path.set_zlabel('Z (m)', color=COLORS["text"], fontsize=12)
    ax_path.set_title('Trayectoria del Perro', color=COLORS["text"], fontsize=14)
    
    # Add a legend for the states
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Acostado'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Sentado'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Caminando'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='cyan', markersize=10, label='Inicio'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='magenta', markersize=10, label='Fin')
    ]
    ax_path.legend(handles=legend_elements, loc='upper right')
    
    # Make the plot look nice
    ax_path.grid(True, alpha=0.3)
    ax_path.set_facecolor(COLORS["background"])
    ax_path.tick_params(axis='x', colors=COLORS["text"])
    ax_path.tick_params(axis='y', colors=COLORS["text"])
    ax_path.tick_params(axis='z', colors=COLORS["text"])
    
    # Create canvas for the plot
    canvas_path = FigureCanvasTkAgg(fig_path, master=canvas_frame_path)
    canvas_path.draw()
    canvas_path.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Add navigation toolbar
    toolbar_frame_path = ctk.CTkFrame(canvas_frame_path)
    toolbar_frame_path.pack(side=tk.BOTTOM, fill=tk.X)
    toolbar_path = NavigationToolbar2Tk(canvas_path, toolbar_frame_path)
    toolbar_path.update()
    
    # Add instruction label
    info_label_path = ctk.CTkLabel(
        canvas_frame_path, 
        text="Haga clic en un punto para ver detalles", 
        font=ctk.CTkFont(size=12)
    )
    info_label_path.pack(side=tk.BOTTOM, pady=5)
    
    # Create annotation capability
    annot_path = ax_path.annotate("", xy=(0,0), xytext=(10,10),
                      textcoords="offset points",
                      bbox=dict(boxstyle="round", fc="w", alpha=0.7),
                      arrowprops=dict(arrowstyle="->"))
    annot_path.set_visible(False)
    
    # Function to handle click for path plot
    def on_click_path(event):
        if event.inaxes == ax_path:
            cont, ind = scatter_path.contains(event)
            if cont:
                idx = ind["ind"][0]
                pos = positions[idx]
                state = processed_data.iloc[idx]['comp_pred']
                
                # Update annotation
                annot_path.xy = (pos[0], pos[1])
                text = (f"Punto: {idx}\n"
                        f"Posición: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})\n"
                        f"Estado: {state}\n"
                        f"Tiempo: {processed_data.iloc[idx]['timestamp']:.1f}ms")
                annot_path.set_text(text)
                annot_path.set_visible(True)
                
                # Update info label
                info_label_path.configure(text=f"Punto {idx}: {state} - Tiempo: {processed_data.iloc[idx]['timestamp']:.1f}ms")
                
                fig_path.canvas.draw_idle()
    
    fig_path.canvas.mpl_connect('button_press_event', on_click_path)
    
    # Add controls for path visualization
    controls_frame = ctk.CTkFrame(canvas_frame_path)
    controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 5))
    
    # Checkbox to filter by state
    state_filters = {}
    for i, state in enumerate(['acostado', 'sentado', 'caminando']):
        var = tk.BooleanVar(value=True)
        state_filters[state] = var
        
        color = color_dict.get(state, 'gray')
        checkbutton = ctk.CTkCheckBox(
            controls_frame,
            text=state.capitalize(),
            variable=var,
            onvalue=True,
            offvalue=False,
            fg_color=color,
            hover_color=color,
            text_color=COLORS["text"]
        )
        checkbutton.pack(side=tk.LEFT, padx=10)
    
    # Function to update the plot based on state filters
    def update_path_filter():
        visible_states = [state for state, var in state_filters.items() if var.get()]
        
        # Filter data
        mask = processed_data['comp_pred'].isin(visible_states)
        
        # Update scatter plot
        scatter_path._offsets3d = (positions[mask, 0], positions[mask, 1], positions[mask, 2])
        
        # Get filtered color indices
        filtered_indices = np.array(color_indices)[mask]
        scatter_path.set_array(np.array(filtered_indices))
        
        # Redraw
        fig_path.canvas.draw_idle()
    
    # Add filter button
    filter_button = ctk.CTkButton(
        controls_frame,
        text="Aplicar Filtros",
        command=update_path_filter,
        fg_color=COLORS["primary"],
        hover_color=COLORS["secondary"]
    )
    filter_button.pack(side=tk.RIGHT, padx=10)
    
    # Tab 6: Statistics with improved tables
    stats_frame = ctk.CTkScrollableFrame(tab_stats)
    stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Calculate statistics
    accel_stats = processed_data[['acc_x', 'acc_y', 'acc_z']].describe()
    gyro_stats = processed_data[['gyro_x', 'gyro_y', 'gyro_z']].describe()
    quat_stats = processed_data[['q1', 'q2', 'q3', 'q4']].describe()  # Add quaternion stats
    
    # Accelerometer statistics table
    ctk.CTkLabel(
        stats_frame, 
        text="Estadísticas de Acelerómetro", 
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=(10, 5), anchor="w")
    
    # Create treeview for accelerometer stats
    accel_tree_frame = ctk.CTkFrame(stats_frame)
    accel_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    accel_tree = ttk.Treeview(accel_tree_frame)
    
    # Configure columns for accelerometer stats
    accel_tree["columns"] = ["Stat", "X", "Y", "Z"]
    accel_tree.column("#0", width=0, stretch=tk.NO)
    accel_tree.column("Stat", width=100, anchor=tk.W)
    accel_tree.column("X", width=100, anchor=tk.CENTER)
    accel_tree.column("Y", width=100, anchor=tk.CENTER)
    accel_tree.column("Z", width=100, anchor=tk.CENTER)
    
    # Configure headers
    accel_tree.heading("#0", text="")
    accel_tree.heading("Stat", text="Estadística")
    accel_tree.heading("X", text="X")
    accel_tree.heading("Y", text="Y")
    accel_tree.heading("Z", text="Z")
    
    # Add stats rows
    for idx, row_name in enumerate(accel_stats.index):
        values = [row_name]
        values.extend([f"{accel_stats.loc[row_name, col]:.4f}" for col in ['acc_x', 'acc_y', 'acc_z']])
        accel_tree.insert("", idx, text="", values=values)
    
    accel_tree.pack(fill="both", expand=True)
    
    # Gyroscope statistics table
    ctk.CTkLabel(
        stats_frame, 
        text="Estadísticas de Giroscopio", 
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=(20, 5), anchor="w")
    
    gyro_tree_frame = ctk.CTkFrame(stats_frame)
    gyro_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    gyro_tree = ttk.Treeview(gyro_tree_frame)
    
    # Configure columns for gyroscope stats
    gyro_tree["columns"] = ["Stat", "X", "Y", "Z"]
    gyro_tree.column("#0", width=0, stretch=tk.NO)
    gyro_tree.column("Stat", width=100, anchor=tk.W)
    gyro_tree.column("X", width=100, anchor=tk.CENTER)
    gyro_tree.column("Y", width=100, anchor=tk.CENTER)
    gyro_tree.column("Z", width=100, anchor=tk.CENTER)
    
    # Configure headers
    gyro_tree.heading("#0", text="")
    gyro_tree.heading("Stat", text="Estadística")
    gyro_tree.heading("X", text="X")
    gyro_tree.heading("Y", text="Y")
    gyro_tree.heading("Z", text="Z")
    
    # Add stats rows
    for idx, row_name in enumerate(gyro_stats.index):
        values = [row_name]
        values.extend([f"{gyro_stats.loc[row_name, col]:.4f}" for col in ['gyro_x', 'gyro_y', 'gyro_z']])
        gyro_tree.insert("", idx, text="", values=values)
    
    gyro_tree.pack(fill="both", expand=True)
    
    # Quaternion statistics table
    ctk.CTkLabel(
        stats_frame, 
        text="Estadísticas de Cuaterniones", 
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=(20, 5), anchor="w")
    
    quat_tree_frame = ctk.CTkFrame(stats_frame)
    quat_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    quat_tree = ttk.Treeview(quat_tree_frame)
    
    # Configure columns for quaternion stats
    quat_tree["columns"] = ["Stat", "Q1", "Q2", "Q3", "Q4"]
    quat_tree.column("#0", width=0, stretch=tk.NO)
    quat_tree.column("Stat", width=100, anchor=tk.W)
    quat_tree.column("Q1", width=75, anchor=tk.CENTER)
    quat_tree.column("Q2", width=75, anchor=tk.CENTER)
    quat_tree.column("Q3", width=75, anchor=tk.CENTER)
    quat_tree.column("Q4", width=75, anchor=tk.CENTER)
    
    # Configure headers
    quat_tree.heading("#0", text="")
    quat_tree.heading("Stat", text="Estadística")
    quat_tree.heading("Q1", text="Q1")
    quat_tree.heading("Q2", text="Q2")
    quat_tree.heading("Q3", text="Q3")
    quat_tree.heading("Q4", text="Q4")
    
    # Add stats rows
    for idx, row_name in enumerate(quat_stats.index):
        values = [row_name]
        values.extend([f"{quat_stats.loc[row_name, col]:.4f}" for col in ['q1', 'q2', 'q3', 'q4']])
        quat_tree.insert("", idx, text="", values=values)
    
    quat_tree.pack(fill="both", expand=True)
    
    # Add behavior statistics section
    ctk.CTkLabel(
        stats_frame, 
        text="Estadísticas de Comportamiento", 
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=(20, 5), anchor="w")
    
    # Calculate behavior statistics
    behavior_counts = processed_data['comp_pred'].value_counts()
    behavior_percentages = behavior_counts / len(processed_data) * 100
    
    behavior_frame = ctk.CTkFrame(stats_frame)
    behavior_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    behavior_tree = ttk.Treeview(behavior_frame)
    
    # Configure columns for behavior stats
    behavior_tree["columns"] = ["Behavior", "Count", "Percentage"]
    behavior_tree.column("#0", width=0, stretch=tk.NO)
    behavior_tree.column("Behavior", width=150, anchor=tk.W)
    behavior_tree.column("Count", width=100, anchor=tk.CENTER)
    behavior_tree.column("Percentage", width=150, anchor=tk.CENTER)
    
    # Configure headers
    behavior_tree.heading("#0", text="")
    behavior_tree.heading("Behavior", text="Comportamiento")
    behavior_tree.heading("Count", text="Cantidad")
    behavior_tree.heading("Percentage", text="Porcentaje")
    
    # Add behavior rows
    for idx, behavior in enumerate(behavior_counts.index):
        count = behavior_counts[behavior]
        percentage = behavior_percentages[behavior]
        behavior_tree.insert("", idx, text="", values=[behavior, count, f"{percentage:.2f}%"])
    
    behavior_tree.pack(fill="both", expand=True)
    
    # Add Summary Statistics
    ctk.CTkLabel(
        stats_frame, 
        text="Resumen General", 
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=(20, 5), anchor="w")
    
    # Calculate some general statistics for the test
    total_duration = processed_data['timestamp'].max() - processed_data['timestamp'].min()
    sample_rate = len(processed_data) / (total_duration / 1000)  # samples per second
    
    # Peak acceleration and angular velocity
    peak_accel = max(
        processed_data['acc_x'].abs().max(),
        processed_data['acc_y'].abs().max(),
        processed_data['acc_z'].abs().max()
    )
    
    peak_gyro = max(
        processed_data['gyro_x'].abs().max(),
        processed_data['gyro_y'].abs().max(),
        processed_data['gyro_z'].abs().max()
    )
    
    # Summary data
    summary_data = {
        "Duración total": f"{total_duration:.2f} ms ({total_duration/1000:.2f} s)",
        "Frecuencia de muestreo": f"{sample_rate:.2f} Hz",
        "Total de muestras": f"{len(processed_data)}",
        "Aceleración máxima": f"{peak_accel:.4f} g",
        "Velocidad angular máxima": f"{peak_gyro:.4f} °/s",
        "Comportamiento predominante": behavior_counts.idxmax()
    }
    
    # Create summary frame with grid layout
    summary_frame = ctk.CTkFrame(stats_frame)
    summary_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Display summary stats in a grid
    for idx, (key, value) in enumerate(summary_data.items()):
        ctk.CTkLabel(
            summary_frame, 
            text=key, 
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).grid(row=idx, column=0, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(
            summary_frame, 
            text=value, 
            font=ctk.CTkFont(size=14),
            anchor="w"
        ).grid(row=idx, column=1, sticky="w", padx=10, pady=5)
    
    # Add export button
    export_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    export_frame.pack(fill="x", padx=10, pady=(5, 10))
    
    # Export button
    export_button = ctk.CTkButton(
        export_frame,
        text="Exportar Análisis",
        font=ctk.CTkFont(size=14),
        fg_color=COLORS["primary"],
        hover_color=COLORS["secondary"],
        command=lambda: export_analysis(dog_name, test_name, processed_data)
    )
    export_button.pack(side="right", padx=10)
    
    # Function to export analysis
    def export_analysis(dog_name, test_name, data):
        # Create timestamp for filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dog_name}_{test_name}_analysis_{timestamp}"
        
        # Ask user for save location
        save_path = filedialog.asksaveasfilename(
            initialfile=filename,
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if save_path:
            if save_path.endswith('.xlsx'):
                # Export to Excel with multiple sheets
                with pd.ExcelWriter(save_path) as writer:
                    # Raw data
                    data.to_excel(writer, sheet_name='Raw_Data', index=True)
                    
                    # Stats
                    accel_stats.to_excel(writer, sheet_name='Accel_Stats')
                    gyro_stats.to_excel(writer, sheet_name='Gyro_Stats')
                    quat_stats.to_excel(writer, sheet_name='Quat_Stats')
                    
                    # Behavior stats
                    pd.DataFrame({
                        'Behavior': behavior_counts.index,
                        'Count': behavior_counts.values,
                        'Percentage': behavior_percentages.values
                    }).to_excel(writer, sheet_name='Behavior_Stats', index=False)
                    
                    # Summary
                    pd.DataFrame({
                        'Metric': summary_data.keys(),
                        'Value': summary_data.values()
                    }).to_excel(writer, sheet_name='Summary', index=False)
            
            elif save_path.endswith('.csv'):
                # Export to CSV (just raw data)
                data.to_csv(save_path, index=True)
            
            messagebox.showinfo("Exportación Exitosa", f"Análisis exportado a {save_path}")
    
    return report_window

# Function to show available tests in the "data" folder
def show_available_tests():
    clear_frame()  # Clears the current content

    form_frame = ctk.CTkFrame(main_content_frame)
    form_frame.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(form_frame, text="Pruebas disponibles", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 20))

    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        dogs = os.listdir(DATA_DIR)
        available_dogs = [dog for dog in dogs if os.path.isdir(os.path.join(DATA_DIR, dog))]

        if available_dogs:
            # Create a scrollable frame inside the main content
            scrollable_frame = ctk.CTkScrollableFrame(form_frame, height=400)
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

            dog_vars = {}  # Store the test variables for each dog
            
            for dog in available_dogs:
                dog_frame = ctk.CTkFrame(scrollable_frame)
                dog_frame.pack(pady=10, fill="x", expand=True)

                ctk.CTkLabel(dog_frame, text=dog, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5, anchor="w")

                # List available tests for each dog
                test_folder_path = os.path.join(DATA_DIR, dog)
                tests = os.listdir(test_folder_path)
                available_tests = [test for test in tests if os.path.isdir(os.path.join(test_folder_path, test))]

                if available_tests:
                    # Create a dropdown menu for selecting a test for each dog
                    test_var = ctk.StringVar(value="Seleccione una prueba")
                    dog_vars[dog] = test_var

                    test_option_menu = ctk.CTkOptionMenu(
                        dog_frame, 
                        values=available_tests,
                        variable=test_var,
                        width=200
                    )
                    test_option_menu.pack(pady=5, side="left", padx=10)

                    # Button to analyze selected test
                    def create_analyze_command(dog_name, var):
                        return lambda: analyze_selected_test(dog_name, var)

                    analyze_button = ctk.CTkButton(
                        dog_frame, 
                        text="Analizar",
                        command=create_analyze_command(dog, test_var),
                        fg_color=COLORS["primary"],
                        hover_color=COLORS["secondary"]
                    )
                    analyze_button.pack(pady=5, side="left", padx=5)
                else:
                    ctk.CTkLabel(dog_frame, text="No hay pruebas disponibles").pack(pady=5, anchor="w")

            # Button to go back to the main screen
            ctk.CTkButton(
                form_frame, 
                text="Regresar", 
                command=show_main_screen,
                fg_color="#FF5722",
                hover_color="#E64A19",
                width=200
            ).pack(pady=20)
        else:
            show_message("No hay perros", "No se encontraron perros en la carpeta de datos.")

    except Exception as e:
        show_message("Error", f"Error al listar los perros:\n{e}")


# Function to process IMU data and show the report
def process_and_show_report(dog_name, test_name):
    try:
        # Initialize the IMU data processor
        processor = IMUDataProcessor(DATA_DIR)
        
        # Process the IMU data
        processed_data = processor.process_imu_data(dog_name, test_name)
        
        if processed_data is not None:
            # Create a report window with the processed data
            create_report_window(dog_name, test_name, processed_data)
        else:
            show_message("Error", f"No se pudo procesar los datos IMU para la prueba {test_name} del perro {dog_name}.")
    except Exception as e:
        show_message("Error", f"Error al procesar datos IMU:\n{e}")


def analyze_selected_test(dog_name, test_var):
    selected_test = test_var.get()
    if selected_test and selected_test != "Seleccione una prueba":
        process_and_show_report(dog_name, selected_test)
    else:
        show_message("Selección inválida", "Por favor, seleccione una prueba.")

# Function to show input fields after choosing the test type
def show_input_fields():
    # Hide the main content
    clear_frame()
    
    # Create a new frame for the form
    form_frame = ctk.CTkFrame(main_content_frame)
    form_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    ctk.CTkLabel(form_frame, text="Nueva Prueba", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 20))
    
    # Input fields
    input_frame = ctk.CTkFrame(form_frame)
    input_frame.pack(fill="x", padx=20, pady=10)
    
    # Dog name input
    dog_frame = ctk.CTkFrame(input_frame)
    dog_frame.pack(fill="x", pady=10)
    
    ctk.CTkLabel(dog_frame, text="Nombre del perro:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
    
    global entry_perro
    entry_perro = ctk.CTkEntry(dog_frame, font=ctk.CTkFont(size=14), width=250)
    entry_perro.pack(side="left", padx=10, fill="x", expand=True)
    
    # Test name input
    test_frame = ctk.CTkFrame(input_frame)
    test_frame.pack(fill="x", pady=10)
    
    ctk.CTkLabel(test_frame, text="Nombre de la prueba:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
    
    global entry_prueba
    entry_prueba = ctk.CTkEntry(test_frame, font=ctk.CTkFont(size=14), width=250)
    entry_prueba.pack(side="left", padx=10, fill="x", expand=True)
    
    # Duration input
    duration_frame = ctk.CTkFrame(input_frame)
    duration_frame.pack(fill="x", pady=10)
    
    ctk.CTkLabel(duration_frame, text="Duración (segundos):", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
    
    global entry_duracion
    entry_duracion = ctk.CTkEntry(duration_frame, font=ctk.CTkFont(size=14), width=250)
    entry_duracion.pack(side="left", padx=10, fill="x", expand=True)
    
    # Sensor selection
    sensors_frame = ctk.CTkFrame(form_frame)
    sensors_frame.pack(fill="x", padx=20, pady=20)
    
    ctk.CTkLabel(sensors_frame, text="Sensores a utilizar:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))
    
    # Checkboxes for selecting sensors
    global var_imu, var_camara, var_audio, var_temperatura
    var_imu = ctk.BooleanVar(value=True)  # Default IMU enabled
    var_camara = ctk.BooleanVar()
    var_audio = ctk.BooleanVar()
    var_temperatura = ctk.BooleanVar()
    
    checkbox_frame = ctk.CTkFrame(sensors_frame)
    checkbox_frame.pack(fill="x", pady=5)
    
    # Create a grid for checkboxes
    ctk.CTkCheckBox(checkbox_frame, text="IMU", variable=var_imu, font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=20, pady=10, sticky="w")
    ctk.CTkCheckBox(checkbox_frame, text="Cámara", variable=var_camara, font=ctk.CTkFont(size=14)).grid(row=0, column=1, padx=20, pady=10, sticky="w")
    ctk.CTkCheckBox(checkbox_frame, text="Micrófono", variable=var_audio, font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=20, pady=10, sticky="w")
    ctk.CTkCheckBox(checkbox_frame, text="Temperatura", variable=var_temperatura, font=ctk.CTkFont(size=14)).grid(row=1, column=1, padx=20, pady=10, sticky="w")
    
    # Buttons
    button_frame = ctk.CTkFrame(form_frame)
    button_frame.pack(fill="x", pady=20)
    
    ctk.CTkButton(
        button_frame, 
        text="Regresar", 
        command=show_main_screen,
        fg_color="#FF5722",
        hover_color="#E64A19",
        width=150
    ).pack(side="left", padx=20)
    
    ctk.CTkButton(
        button_frame, 
        text="Iniciar prueba", 
        command=start_test,
        fg_color=COLORS["primary"],
        hover_color=COLORS["secondary"],
        width=150
    ).pack(side="right", padx=20)

# Function to clear the main content frame
def clear_frame():
    for widget in main_content_frame.winfo_children():
        widget.destroy()

# Function to show the main screen
def show_main_screen():
    # Clear the frame first
    clear_frame()
    
    # Show the logo
    if logo_image:
        logo_label = ctk.CTkLabel(main_content_frame, image=logo_image, text="")
        logo_label.pack(pady=(30, 15))
    
    # Welcome message
    ctk.CTkLabel(
        main_content_frame, 
        text="Sistema de Monitoreo Canino", 
        font=ctk.CTkFont(size=24, weight="bold")
    ).pack(pady=(0, 30))
    
    # Buttons for main actions
    button_frame = ctk.CTkFrame(main_content_frame)
    button_frame.pack(pady=20)
    
    # Test buttons
    ctk.CTkButton(
        button_frame,
        text="Nueva Prueba",
        command=show_input_fields,
        fg_color=COLORS["primary"],
        hover_color=COLORS["secondary"],
        font=ctk.CTkFont(size=16),
        width=250,
        height=50
    ).pack(pady=10)
    
    ctk.CTkButton(
        button_frame,
        text="Ver Pruebas Disponibles",
        command=show_available_tests,
        fg_color=COLORS["primary"],
        hover_color=COLORS["secondary"],
        font=ctk.CTkFont(size=16),
        width=250,
        height=50
    ).pack(pady=10)
    
    ctk.CTkButton(
        button_frame,
        text="Cerrar Aplicación",
        command=root.quit,
        fg_color="#FF5722",
        hover_color="#E64A19",
        font=ctk.CTkFont(size=16),
        width=250,
        height=50
    ).pack(pady=10)
    
    # Version info at the bottom
    ctk.CTkLabel(
        main_content_frame, 
        text="DataPek System v1.0", 
        font=ctk.CTkFont(size=12)
    ).pack(side="bottom", pady=10)

# Initialize the GUI
root = ctk.CTk()
root.title("Sistema de Monitoreo Canino")
root.geometry("700x700")
root.minsize(600, 500)

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Create a main container frame
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Create header frame
header_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["primary"], height=80)
header_frame.pack(fill="x", padx=10, pady=(10, 0))
header_frame.pack_propagate(False)  # Fixed height

# Set app title in header
title_label = ctk.CTkLabel(
    header_frame, 
    text="DataPek - Sistema de Monitoreo Canino",
    font=ctk.CTkFont(size=20, weight="bold"),
    text_color=COLORS["text"]
)
title_label.pack(side="left", padx=20, pady=10)

# Create main content frame
main_content_frame = ctk.CTkFrame(main_frame)
main_content_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Try to load the logo image
logo_image = None
try:
    logo_img = Image.open("datapek_logo.png")
    logo_img = logo_img.resize((150, 150), Image.Resampling.LANCZOS)
    logo_image = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(150, 150))
except Exception as e:
    print(f"Error loading logo: {e}")

# Show main screen
show_main_screen()

# Start the main loop
if __name__ == "__main__":
    root.mainloop()
