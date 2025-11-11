# main_gui.py
from tkinter import *
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import matplotlib.pyplot as plt
import logic

selected_path = "" 

quantized_vals = None
quant_error = None
encoded_levels = None
quant_levels = None
quant_bits = None

def clear_plot_area():
    for w in remaining_space_frame.winfo_children():
        w.destroy()

def browse():
    global selected_path
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not path:
        return
    filepath.set(path.split("/")[-1])
    selected_path = path

def show_quantization_window():
    """Open a window to input number of bits or levels and perform quantization.

    The user can choose either:
    - Number of bits: compute levels = 2**bits
    - Number of levels: use directly

    After quantization, the GUI displays:
    - Original vs Quantized signal
    - Quantization error (original - quantized)
    - Encoded levels (integer codes)
    """
    global quantized_vals, quant_error, encoded_levels, quant_levels, quant_bits

    if not logic.cur_vals:
        messagebox.showerror("Error", "No signal available to quantize. Load or generate a signal first.")
        return

    input_window = Toplevel(rootWin)
    input_window.title("Signal Quantization")
    input_window.geometry("350x260")
    input_window.resizable(False, False)

    mode_var = StringVar(value="bits")

    Radiobutton(input_window, text="Number of bits", variable=mode_var, value="bits").pack(anchor=W, padx=10, pady=(10,0))
    bits_entry = Entry(input_window, width=20)
    bits_entry.pack(padx=10, pady=2)
    bits_entry.insert(0, "8")

    Radiobutton(input_window, text="Number of levels", variable=mode_var, value="levels").pack(anchor=W, padx=10, pady=(10,0))
    levels_entry = Entry(input_window, width=20)
    levels_entry.pack(padx=10, pady=2)
    levels_entry.insert(0, "256")

    Label(input_window, text="(Quantization is uniform over signal range)", font=("Segoe UI", 8)).pack(pady=(6,0))

    def do_quantize():
        nonlocal mode_var, bits_entry, levels_entry
        global quantized_vals, quant_error, encoded_levels, quant_levels, quant_bits
        try:
            mode = mode_var.get()
            if mode == "bits":
                b = int(bits_entry.get())
                if b <= 0:
                    raise ValueError("Bits must be positive")
                L = 2 ** b
                quant_bits = b
                quant_levels = L
            else:
                L = int(levels_entry.get())
                if L <= 1:
                    raise ValueError("Levels must be integer > 1")
                quant_bits = None
                quant_levels = L

            # perform uniform quantization on logic.cur_vals
            x = logic.cur_vals
            xmin = min(x)
            xmax = max(x)
            if xmax == xmin:
                # degenerate: all samples equal -> single level
                step = 0.0
                q_vals = [xmin for _ in x]
                codes = [0 for _ in x]
                errors = [0.0 for _ in x]
            else:
                step = (xmax - xmin) / quant_levels
                # mid-rise quantizer: reconstruction levels at xmin + (i+0.5)*step
                q_vals = []
                codes = []
                errors = []
                for xi in x:
                    idx = int((xi - xmin) / step)
                    if idx < 0:
                        idx = 0
                    if idx >= quant_levels:
                        idx = quant_levels - 1
                    recon = xmin + (idx + 0.5) * step
                    q_vals.append(recon)
                    codes.append(idx)
                    errors.append(xi - recon)

            quantized_vals = q_vals
            quant_error = errors
            encoded_levels = codes

            input_window.destroy()
            plot_quantization()
        except ValueError as ve:
            messagebox.showerror("Error", f"Invalid input: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Quantization failed: {e}")

    Button(input_window, text="Quantize", command=do_quantize, width=12).pack(pady=10)
    Button(input_window, text="Cancel", command=input_window.destroy, width=12).pack()


def plot_quantization():
    """Plot original vs quantized, quantization error, and encoded levels."""
    clear_plot_area()

    if not logic.cur_idxs or not logic.cur_vals:
        default_ploting_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        return

    if quantized_vals is None or quant_error is None or encoded_levels is None:
        plot_accumulated()
        return

    fig, ax = plt.subplots(3, 1, figsize=(7, 8), dpi=100)

    # Top: original vs quantized
    ax[0].stem(logic.cur_idxs, logic.cur_vals, linefmt='C0-', markerfmt='C0o', basefmt=" ", label="Original")
    ax[0].stem(logic.cur_idxs, quantized_vals, linefmt='C1--', markerfmt='C1s', basefmt=" ", label="Quantized")
    title_info = f"Quantized Signal (levels={quant_levels}" + (f", bits={quant_bits})" if quant_bits is not None else ")")
    ax[0].set_title("Original vs Quantized - " + title_info)
    ax[0].set_ylabel("Amplitude")
    ax[0].grid(True)
    ax[0].legend()

    # Middle: quantization error
    ax[1].stem(logic.cur_idxs, quant_error, linefmt='C2-', markerfmt='C2o', basefmt=" ")
    ax[1].set_title("Quantization Error (original - quantized)")
    ax[1].set_ylabel("Error")
    ax[1].grid(True)

    # Bottom: encoded integer levels
    ax[2].stem(logic.cur_idxs, encoded_levels, linefmt='C3-', markerfmt='C3o', basefmt=" ")
    ax[2].set_title("Encoded Levels (integer codes)")
    ax[2].set_xlabel("Sample Index")
    ax[2].set_ylabel("Level Code")
    ax[2].grid(True)

    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=remaining_space_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)


def add_signal_clicked():
    """Read the currently browsed file and add it to the accumulated signal."""
    global selected_path
    if not selected_path:
        messagebox.showerror("Error", "No file selected to add.")
        return

    idxs = []
    vals = []
    try:
        logic.read_signal(selected_path, idxs, vals)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file: {e}")
        return

    if not idxs or not vals:
        messagebox.showerror("Error", "Selected file contains no data.")
        return
    
    logic.add_signal(idxs, vals)
    messagebox.showinfo("Added", f"Signal added to accumulation. Accumulated samples: {len(logic.cur_idxs)}")

def subtract_signal_clicked():
    """Subtract the currently browsed file's signal from the accumulated signal."""
    global selected_path
    if not selected_path:
        messagebox.showerror("Error", "No file selected to subtract.")
        return

    idxs = []
    vals = []
    try:
        logic.read_signal(selected_path, idxs, vals)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file: {e}")
        return
    
    logic.sub_signal(idxs, vals)
    messagebox.showinfo("Subtracted", "Signal subtracted from accumulation.")
    plot_accumulated()

def advance_signal_clicked():
    """Advance the accumulated signal by k steps."""
    try:
        k = int(shift_entry.get())
        if k < 0:
            messagebox.showerror("Error", "k must be non-negative.")
            return
        logic.advance_signal(logic.cur_idxs, logic.cur_vals, k)
        messagebox.showinfo("Advanced", f"Signal advanced by {k} steps.")
        plot_accumulated()
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid integer for k.")

def delay_signal_clicked():
    """Delay the accumulated signal by k steps."""
    try:
        k = int(shift_entry.get())
        if k < 0:
            messagebox.showerror("Error", "k must be non-negative.")
            return
        logic.delay_signal(logic.cur_idxs, logic.cur_vals, k)
        messagebox.showinfo("Delayed", f"Signal delayed by {k} steps.")
        plot_accumulated()
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid integer for k.")

def fold_signal_clicked():
    """Fold (time-reverse) the accumulated signal."""
    if not logic.cur_idxs or not logic.cur_vals:
        messagebox.showerror("Error", "No accumulated signal to fold.")
        return
    try:
        logic.fold_signal(logic.cur_idxs, logic.cur_vals)
        messagebox.showinfo("Folded", "Signal has been folded.")
        plot_accumulated()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fold signal: {e}")

def multiply_signal_clicked():
    """Multiply the accumulated signal by a scalar."""
    try:
        factor = float(multiply_entry.get())
        logic.multiply(logic.cur_vals, factor)
        messagebox.showinfo("Multiplied", f"Signal multiplied by {factor}.")
        plot_accumulated()
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")

def generate_signal(wave_type, amplitude, analog_freq, sampling_freq, theta):
    """Generate a sinusoidal or cosinusoidal signal and add it to the accumulated signal."""
    if sampling_freq < 2 * analog_freq:
        messagebox.showerror("Error", f"Sampling frequency ({sampling_freq} Hz) must be at least twice the analog frequency ({analog_freq} Hz).")
        return

    num_samples = 100
    idxs = list(range(num_samples))
    normalized_freq = float(analog_freq) / sampling_freq
    vals = []

    if wave_type == "sine":
        vals = [amplitude * math.sin(2 * math.pi * normalized_freq * i + theta) for i in idxs]
    else:  # cosine
        vals = [amplitude * math.cos(2 * math.pi * normalized_freq * i + theta) for i in idxs]

    logic.add_signal(idxs, vals)
    messagebox.showinfo("Generated", f"{wave_type.capitalize()} wave generated and added. Samples: {len(idxs)}")
    plot_accumulated()

def show_signal_input_window(wave_type):
    """Open a window to input parameters for generating a sine or cosine wave."""
    input_window = Toplevel(rootWin)
    input_window.title(f"Generate {wave_type.capitalize()} Wave")
    input_window.geometry("300x250")
    input_window.resizable(False, False)

    Label(input_window, text="Amplitude (A):", font=("Segoe UI", 10)).pack(pady=5)
    amplitude_entry = Entry(input_window, width=15)
    amplitude_entry.pack()

    Label(input_window, text="Analog Frequency (F, Hz):", font=("Segoe UI", 10)).pack(pady=5)
    analog_freq_entry = Entry(input_window, width=15)
    analog_freq_entry.pack()

    Label(input_window, text="Sampling Frequency (Fs, Hz):", font=("Segoe UI", 10)).pack(pady=5)
    sampling_freq_entry = Entry(input_window, width=15)
    sampling_freq_entry.pack()

    Label(input_window, text="Phase Shift (theta, radians):", font=("Segoe UI", 10)).pack(pady=5)
    theta_entry = Entry(input_window, width=15)
    theta_entry.pack()

    def submit():
        try:
            amplitude = float(amplitude_entry.get())
            analog_freq = float(analog_freq_entry.get())
            sampling_freq = float(sampling_freq_entry.get())
            theta = float(theta_entry.get())
            generate_signal(wave_type, amplitude, analog_freq, sampling_freq, theta)
            input_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all fields.")

    Button(input_window, text="Generate", command=submit, width=10).pack(pady=10)
    Button(input_window, text="Cancel", command=input_window.destroy, width=10).pack(pady=5)

def plot_accumulated():
    """Plot the accumulated signal as two subplots: discrete and continuous."""
    clear_plot_area()

    if not logic.cur_idxs or not logic.cur_vals:
        default_ploting_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        return

    fig, ax = plt.subplots(2, 1, figsize=(6, 6), dpi=100)

    ax[0].stem(logic.cur_idxs, logic.cur_vals, label="Discrete Signal", basefmt=" ")
    ax[0].set_title("Discrete Accumulated Signal")
    ax[0].set_xlabel("Sample Index")
    ax[0].set_ylabel("Sample Value")
    ax[0].grid(True)
    ax[0].legend()

    ax[1].plot(logic.cur_idxs, logic.cur_vals, marker='o', label="Continuous Signal")
    ax[1].set_title("Continuous Accumulated Signal")
    ax[1].set_xlabel("Sample Index")
    ax[1].set_ylabel("Sample Value")
    ax[1].grid(True)
    ax[1].legend()

    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=remaining_space_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

def reset_accumulated():
    logic.cur_idxs.clear()
    logic.cur_vals.clear()
    clear_plot_area()
    default_ploting_label.place(relx=0.5, rely=0.5, anchor=CENTER)
    messagebox.showinfo("Reset", "Accumulated signal cleared.")

# =================================================================
# GUI SETUP - Organized Layout
# =================================================================
rootWin = Tk()
rootWin.title("Signal Accumulator")
rootWin.geometry("900x600")

# Menubar
menubar = Menu(rootWin)
rootWin.config(menu=menubar)

signal_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Signal Generation", menu=signal_menu)
signal_menu.add_command(label="Sine Wave", command=lambda: show_signal_input_window("sine"))
signal_menu.add_command(label="Cosine Wave", command=lambda: show_signal_input_window("cosine"))

menubar.add_command(label="Quantize Signal", command=show_quantization_window)

filepath = StringVar(value="No signal selected")

# =================================================================
# MAIN LAYOUT: Split into left (controls) and right (plot)
# =================================================================
left_panel = Frame(rootWin, bg="#E8E8E8", width=250)
left_panel.pack(side=LEFT, fill=Y, padx=10, pady=10)
left_panel.pack_propagate(False)

remaining_space_frame = Frame(rootWin, bg="#FEFEFE")
remaining_space_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

default_ploting_label = Label(
    remaining_space_frame,
    text="No plots yet",
    font=("Segoe UI", 12, "italic"),
    bg="#FEFEFE",
    fg="#555555"
)
default_ploting_label.place(relx=0.5, rely=0.5, anchor=CENTER)

# =================================================================
# LEFT PANEL - CONTROL SECTIONS
# =================================================================

# --- File Management Section ---
file_section = LabelFrame(left_panel, text="File Management", font=("Segoe UI", 10, "bold"), bg="#E8E8E8", fg="#333")
file_section.pack(fill=X, pady=10)

filepath_label = Label(file_section, textvariable=filepath, font=("Segoe UI", 9), bg="#E8E8E8", wraplength=200, justify=LEFT)
filepath_label.pack(padx=5, pady=5)

browse_button = Button(file_section, text="Browse File", command=browse, width=20, bg="#4CAF50", fg="white")
browse_button.pack(padx=5, pady=3)

# --- Signal Operations Section ---
signal_ops_section = LabelFrame(left_panel, text="Signal Operations", font=("Segoe UI", 10, "bold"), bg="#E8E8E8", fg="#333")
signal_ops_section.pack(fill=X, pady=10)

add_button = Button(signal_ops_section, text="Add Signal", command=add_signal_clicked, width=20, bg="#2196F3", fg="white")
add_button.pack(padx=5, pady=3)

subtract_button = Button(signal_ops_section, text="Subtract Signal", command=subtract_signal_clicked, width=20, bg="#FF9800", fg="white")
subtract_button.pack(padx=5, pady=3)

# --- Arithmetic Operations Section ---
arithmetic_section = LabelFrame(left_panel, text="Arithmetic", font=("Segoe UI", 10, "bold"), bg="#E8E8E8", fg="#333")
arithmetic_section.pack(fill=X, pady=10)

Label(arithmetic_section, text="Multiply by:", font=("Segoe UI", 9), bg="#E8E8E8").pack(padx=5, pady=3)
multiply_entry = Entry(arithmetic_section, width=20)
multiply_entry.pack(padx=5, pady=2)

multiply_button = Button(arithmetic_section, text="Apply Multiply", command=multiply_signal_clicked, width=20, bg="#9C27B0", fg="white")
multiply_button.pack(padx=5, pady=3)

# --- Time Domain Operations Section ---
time_section = LabelFrame(left_panel, text="Time Domain Ops", font=("Segoe UI", 10, "bold"), bg="#E8E8E8", fg="#333")
time_section.pack(fill=X, pady=10)

Label(time_section, text="Shift by k:", font=("Segoe UI", 9), bg="#E8E8E8").pack(padx=5, pady=3)
shift_entry = Entry(time_section, width=20)
shift_entry.pack(padx=5, pady=2)

shift_buttons_frame = Frame(time_section, bg="#E8E8E8")
shift_buttons_frame.pack(fill=X, padx=5, pady=3)

advance_button = Button(shift_buttons_frame, text="Advance >", command=advance_signal_clicked, width=9, bg="#00BCD4", fg="white")
advance_button.pack(side=LEFT, padx=2)

delay_button = Button(shift_buttons_frame, text="Delay <", command=delay_signal_clicked, width=9, bg="#00BCD4", fg="white")
delay_button.pack(side=LEFT, padx=2)

fold_button = Button(time_section, text="Fold Signal", command=fold_signal_clicked, width=20, bg="#795548", fg="white")
fold_button.pack(padx=5, pady=3)

# --- Plot & Reset Section ---
plot_section = LabelFrame(left_panel, text="Display", font=("Segoe UI", 10, "bold"), bg="#E8E8E8", fg="#333")
plot_section.pack(fill=X, pady=10)

plot_button = Button(plot_section, text="Plot Accumulated", command=plot_accumulated, width=20, bg="#4CAF50", fg="white")
plot_button.pack(padx=5, pady=3)

reset_button = Button(plot_section, text="Reset All", command=reset_accumulated, width=20, bg="#F44336", fg="white")
reset_button.pack(padx=5, pady=3)

rootWin.mainloop()