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

processed_vals = None
processed_idxs = None
processed_type = None  

dft_magnitude = None
dft_phase = None
dft_freqs = None
dft_sampling_freq = None

def show_moving_average_window():
    """Open a window to input window size for moving average."""
    if not logic.cur_vals:
        messagebox.showerror("Error", "No signal available. Load or generate a signal first.")
        return

    input_window = Toplevel(rootWin)
    input_window.title("Moving Average")
    input_window.geometry("300x150")
    input_window.resizable(False, False)

    Label(input_window, text="Window Size:", font=("Segoe UI", 10)).pack(pady=10)
    window_entry = Entry(input_window, width=20)
    window_entry.pack()
    window_entry.insert(0, "3")

    def apply_moving_avg():
        global processed_vals, processed_idxs, processed_type
        try:
            window_size = int(window_entry.get())
            if window_size <= 0:
                raise ValueError("Window size must be positive")
            
            result = logic.moving_average(logic.cur_vals, window_size)
            processed_vals = result
            processed_idxs = logic.cur_idxs[:]
            processed_type = "moving_avg"
            
            input_window.destroy()
            plot_processed()
            messagebox.showinfo("Success", f"Moving average applied (window={window_size})")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    Button(input_window, text="Apply", command=apply_moving_avg, width=12).pack(pady=10)
    Button(input_window, text="Cancel", command=input_window.destroy, width=12).pack()

def plot_processed():
    """Plot processed signal safely."""
    clear_plot_area()

    if processed_vals is None or processed_idxs is None:
        default_ploting_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        return

    # Remove old default label if present
    try:
        default_ploting_label.place_forget()
    except:
        pass

    fig, ax = plt.subplots(2, 1, figsize=(7, 7), dpi=100)

    # Top: original vs processed
    ax[0].stem(logic.cur_idxs, logic.cur_vals, linefmt='C0-', markerfmt='C0o', basefmt=" ", label="Original")
    ax[0].stem(processed_idxs, processed_vals, linefmt='C1--', markerfmt='C1s', basefmt=" ", label="Processed")
    
    title_map = {
        "moving_avg": "Moving Average",
        "first_deriv": "First Derivative: y(n) = x(n) - x(n-1)",
        "second_deriv": "Second Derivative: y(n) = x(n+1) - 2x(n) + x(n-1)",
        "convolution": "Convolution"
    }
    ax[0].set_title(title_map.get(processed_type, "Processed Signal"))
    ax[0].set_ylabel("Amplitude")
    ax[0].grid(True)
    ax[0].legend()

    # Bottom: processed signal only
    ax[1].stem(processed_idxs, processed_vals, linefmt='C2-', markerfmt='C2o', basefmt=" ")
    ax[1].plot(processed_idxs, processed_vals, marker='o', linestyle='-', color='C2', alpha=0.6)
    ax[1].set_title(f"{title_map.get(processed_type, 'Processed')} Signal (Continuous)")
    ax[1].set_xlabel("Sample Index")
    ax[1].set_ylabel("Amplitude")
    ax[1].grid(True)

    plt.tight_layout()

    # Create canvas
    canvas = FigureCanvasTkAgg(fig, master=remaining_space_frame)
    canvas.draw()

    # Pack safely
    widget = canvas.get_tk_widget()
    widget.pack(fill='both', expand=True)



def show_derivative_window():
    """Open a window to choose first or second derivative."""
    if not logic.cur_vals:
        messagebox.showerror("Error", "No signal available. Load or generate a signal first.")
        return

    deriv_window = Toplevel(rootWin)
    deriv_window.title("Sharpening - Derivative")
    deriv_window.geometry("300x150")
    deriv_window.resizable(False, False)

    Label(deriv_window, text="Select Derivative:", font=("Segoe UI", 10)).pack(pady=10)

    def apply_first():
        global processed_vals, processed_idxs, processed_type
        try:
            # use the new return-style API
            result = logic.first_derivative(logic.cur_vals)
            processed_vals = result
            # indices for first derivative are shifted: original indices from 1..end
            processed_idxs = logic.cur_idxs[1:]
            processed_type = "first_deriv"
            deriv_window.destroy()
            plot_processed()
            messagebox.showinfo("Success", "First derivative applied: y(n) = x(n) - x(n-1)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def apply_second():
        global processed_vals, processed_idxs, processed_type
        try:
            result = logic.second_derivative(logic.cur_vals)
            processed_vals = result
            # indices for second derivative correspond to original indices 1..len-2
            processed_idxs = logic.cur_idxs[1:-1]
            processed_type = "second_deriv"
            deriv_window.destroy()
            plot_processed()
            messagebox.showinfo("Success", "Second derivative applied: y(n) = x(n+1) - 2x(n) + x(n-1)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    Button(deriv_window, text="First Derivative", command=apply_first, width=20).pack(padx=10, pady=5)
    Button(deriv_window, text="Second Derivative", command=apply_second, width=20).pack(padx=10, pady=5)
    Button(deriv_window, text="Cancel", command=deriv_window.destroy, width=20).pack(padx=10, pady=5)
    
def show_convolution_window():
    """Open a window to select second signal for convolution."""
    if not logic.cur_vals:
        messagebox.showerror("Error", "No signal available. Load or generate a signal first.")
        
        return

    conv_window = Toplevel(rootWin)
    conv_window.title("Convolution")
    conv_window.geometry("300x180")
    conv_window.resizable(False, False)

    Label(conv_window, text="Load second signal for convolution:", font=("Segoe UI", 10)).pack(pady=10)
    
    selected_signal2_path = [None]
    
    def browse_signal2():
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            selected_signal2_path[0] = path
            Label(conv_window, text=path.split("/")[-1], font=("Segoe UI", 8), fg="green").pack()

    Button(conv_window, text="Browse Signal 2", command=browse_signal2, width=20).pack(padx=10, pady=5)

    def apply_convolution():
        global processed_vals, processed_idxs, processed_type
        try:
            if not selected_signal2_path[0]:
                messagebox.showerror("Error", "Please select a second signal.")
                return

            # Read second signal
            idxs2 = []
            vals2 = []
            logic.read_signal(selected_signal2_path[0], idxs2, vals2)

            # Convolve
            result_vals, result_idxs = logic.convolve_signals(logic.cur_vals, vals2)
            processed_vals = result_vals
            processed_idxs = result_idxs
            processed_type = "convolution"
            
            conv_window.destroy()
            rootWin.after(50, plot_processed)  # Safe delay
            messagebox.showinfo("Success", f"Convolution applied. Output length: {len(result_vals)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    Button(conv_window, text="Apply Convolution", command=apply_convolution, width=20).pack(padx=10, pady=5)
    Button(conv_window, text="Cancel", command=conv_window.destroy, width=20).pack(padx=10, pady=5)

def clear_plot_area():
    """Safely destroy all widgets in the plot area."""
    for widget in remaining_space_frame.winfo_children():
        try:
            widget.destroy()
        except:
            pass  # In case widget is already gone


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

def show_dft_window():
    """Ask sampling freq, compute DFT, and plot magnitude & phase vs frequency."""
    if not logic.cur_vals:
        messagebox.showerror("Error", "No signal available. Load or generate a signal first.")
        return

    win = Toplevel(rootWin)
    win.title("Compute DFT")
    win.geometry("300x140")
    win.resizable(False, False)

    Label(win, text="Sampling frequency (Hz):", font=("Segoe UI", 10)).pack(pady=8)
    fs_entry = Entry(win, width=20)
    fs_entry.pack()
    fs_entry.insert(0, "100.0")

    def do_dft():
        nonlocal fs_entry, win
        try:
            fs = float(fs_entry.get())
            if fs <= 0:
                raise ValueError("Sampling frequency must be positive.")
            X = logic.dft(logic.cur_vals)
            N = len(X)
            freqs = [k * fs / N for k in range(N)]
            mags = [abs(v) for v in X]
            phases = [cmath_phase(v) for v in X]

            # store global for potential later use
            global dft_magnitude, dft_phase, dft_freqs, dft_sampling_freq, dft_spectrum
            dft_magnitude = mags
            dft_phase = phases
            dft_freqs = freqs
            dft_sampling_freq = fs
            dft_spectrum = X

            win.destroy()
            plot_dft_results()
        except ValueError as ve:
            messagebox.showerror("Error", f"Invalid input: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"DFT failed: {e}")

    Button(win, text="Compute DFT", command=do_dft, width=12).pack(pady=8)
    Button(win, text="Cancel", command=win.destroy, width=12).pack()

def cmath_phase(c):
    """Return phase in radians for complex number (keeps defined if c==0)."""
    import math
    try:
        import cmath
        if c == 0:
            return 0.0
        return cmath.phase(c)
    except Exception:
        return 0.0

def plot_dft_results():
    """Plot frequency vs magnitude and frequency vs phase."""
    clear_plot_area()
    if dft_freqs is None or dft_magnitude is None or dft_phase is None:
        default_ploting_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        return

    fig, ax = plt.subplots(2, 1, figsize=(7, 6), dpi=100)
    ax[0].stem(dft_freqs, dft_magnitude, basefmt=" ")
    ax[0].set_title("DFT - Magnitude")
    ax[0].set_xlabel("Frequency (Hz)")
    ax[0].set_ylabel("Amplitude")
    ax[0].grid(True)

    ax[1].stem(dft_freqs, dft_phase, basefmt=" ")
    ax[1].set_title("DFT - Phase (radians)")
    ax[1].set_xlabel("Frequency (Hz)")
    ax[1].set_ylabel("Phase (rad)")
    ax[1].grid(True)

    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=remaining_space_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

def show_idft_window():
    """Reconstruct time-domain signal from last computed DFT (or ask user to compute DFT first)."""
    global dft_spectrum
    if 'dft_spectrum' not in globals() or dft_spectrum is None:
        messagebox.showerror("Error", "No DFT spectrum available. Compute DFT first.")
        return

    try:
        x_recon = logic.dft(dft_spectrum, True)
        # set processed for plotting overlay
        global processed_vals, processed_idxs, processed_type
        processed_vals = x_recon
        processed_idxs = logic.cur_idxs[:]  # spectrum length equals original N if used same length
        processed_type = "idft_reconstruction"
        plot_processed()
        messagebox.showinfo("Reconstructed", "Signal reconstructed using IDFT and plotted.")
    except Exception as e:
        messagebox.showerror("Error", f"IDFT failed: {e}")

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

# --- Signal Processing Section ---
processing_section = LabelFrame(left_panel, text="Signal Processing", font=("Segoe UI", 10, "bold"), bg="#E8E8E8", fg="#333")
processing_section.pack(fill=X, pady=10)

moving_avg_button = Button(processing_section, text="Moving Average", command=show_moving_average_window, width=20, bg="#E91E63", fg="white")
moving_avg_button.pack(padx=5, pady=3)

derivative_button = Button(processing_section, text="Sharpening (Derivative)", command=show_derivative_window, width=20, bg="#FF5722", fg="white")
derivative_button.pack(padx=5, pady=3)

convolution_button = Button(processing_section, text="Convolution", command=show_convolution_window, width=20, bg="#673AB7", fg="white")
convolution_button.pack(padx=5, pady=3)

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

dft_button = Button(processing_section, text="DFT (Frequency)", command=lambda: show_dft_window(), width=20, bg="#3F51B5", fg="white")
dft_button.pack(padx=5, pady=3)

idft_button = Button(processing_section, text="IDFT (Reconstruct)", command=lambda: show_idft_window(), width=20, bg="#607D8B", fg="white")
idft_button.pack(padx=5, pady=3)

rootWin.mainloop()