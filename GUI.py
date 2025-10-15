# main_gui.py
from tkinter import *
from tkinter import filedialog, messagebox
import logic
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

selected_path = ""  # currently browsed file path

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

def add_signal_clicked():
    """Read the currently browsed file and add it to the accumulated signal.
       This updates logic.cur_idxs / logic.cur_vals but does NOT plot."""
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

    logic.add_signal(idxs, vals)  # mutate the accumulated lists in logic
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
    plot_accumulated()  # Update plot after subtraction

def advance_signal_clicked():
    """Advance the accumulated signal by k steps."""
    try:
        k = int(shift_entry.get())  # Get k from the entry field
        if k < 0:
            messagebox.showerror("Error", "Please enter a non-negative integer for k.")
            return
        logic.advance_signal(logic.cur_idxs, logic.cur_vals, k)
        messagebox.showinfo("Advanced", f"Signal advanced by {k} steps.")
        plot_accumulated()  # Update plot after advancing
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid integer for k.")

def delay_signal_clicked():
    """Delay the accumulated signal by k steps."""
    try:
        k = int(shift_entry.get())  # Get k from the entry field
        if k < 0:
            messagebox.showerror("Error", "Please enter a non-negative integer for k.")
            return
        logic.delay_signal(logic.cur_idxs, logic.cur_vals, k)
        messagebox.showinfo("Delayed", f"Signal delayed by {k} steps.")
        plot_accumulated()  # Update plot after delaying
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

def plot_accumulated():
    """Plot the accumulated signal (logic.cur_idxs / logic.cur_vals)."""
    clear_plot_area()

    if not logic.cur_idxs or not logic.cur_vals:
        # No accumulated data yet
        no_label = Label(
            remaining_space_frame,
            text="No accumulated signal.\nUse Browse → Add Signal to accumulate signals.",
            font=("Segoe UI", 12, "italic"),
            background="#FEFEFE",
            fg="#555555",
            justify=CENTER
        )
        no_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        return

    fig, ax = plt.subplots(figsize=(6,3), dpi=100)
    ax.plot(logic.cur_idxs, logic.cur_vals, marker='o', label="Accumulated Signal")
    ax.set_title("Accumulated Signal")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Sample Value")
    ax.grid(True)
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=remaining_space_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

def reset_accumulated():
    logic.cur_idxs.clear()
    logic.cur_vals.clear()
    clear_plot_area()
    default_ploting_label.place(relx=0.5, rely=0.5, anchor=CENTER)
    messagebox.showinfo("Reset", "Accumulated signal cleared.")

# ----------------- GUI setup -----------------
rootWin = Tk()
rootWin.title("Signal Accumulator")
rootWin.geometry("700x500")

filepath = StringVar(value="No signal selected")

browse_frame = Frame(rootWin, background="#8E8E8E", height=100)
browse_frame.pack(side=BOTTOM, fill=X)
browse_frame.pack_propagate(False)

remaining_space_frame = Frame(rootWin, background="#FEFEFE")
remaining_space_frame.pack(side=LEFT, fill=BOTH, expand=True)

filepath_label = Label(browse_frame, textvariable=filepath, font=("Segoe UI", 11))
filepath_label.place(relx=0.02, rely=0.3, anchor=W)

default_ploting_label = Label(
    remaining_space_frame,
    text="No plots yet",
    font=("Segoe UI", 12, "italic"),
    background="#FEFEFE",
    fg="#555555"
)
default_ploting_label.place(relx=0.5, rely=0.5, anchor=CENTER)

# ----------------- Buttons -----------------
browse_button = Button(browse_frame, text="Browse", command=browse, width=10)
browse_button.place(relx=0.25, rely=0.3, anchor=E)

add_button = Button(browse_frame, text="Add Signal", command=add_signal_clicked, width=12)
add_button.place(relx=0.40, rely=0.3, anchor=W)

subtract_button = Button(browse_frame, text="Subtract Signal", command=subtract_signal_clicked, width=14)
subtract_button.place(relx=0.55, rely=0.3, anchor=W)

plot_button = Button(browse_frame, text="Plot Accumulated", command=plot_accumulated, width=14)
plot_button.place(relx=0.73, rely=0.3, anchor=W)

reset_button = Button(browse_frame, text="Reset", command=reset_accumulated, width=8)
reset_button.place(relx=0.88, rely=0.3, anchor=W)

# ----------------- Multiply section -----------------
multiply_label = Label(browse_frame, text="Multiply by:", font=("Segoe UI", 10), bg="#8E8E8E", fg="white")
multiply_label.place(relx=0.25, rely=0.7, anchor=E)

multiply_entry = Entry(browse_frame, width=10)
multiply_entry.place(relx=0.33, rely=0.7, anchor=W)

multiply_button = Button(
    browse_frame,
    text="Apply",
    command=lambda: (logic.multiply(logic.cur_vals, float(multiply_entry.get())), plot_accumulated()),
    width=10
)
multiply_button.place(relx=0.47, rely=0.7, anchor=W)

# ----------------- Shift section -----------------
shift_label = Label(browse_frame, text="Shift by k:", font=("Segoe UI", 10), bg="#8E8E8E", fg="white")
shift_label.place(relx=0.60, rely=0.7, anchor=E)  # Adjusted relx to make space for fold button

shift_entry = Entry(browse_frame, width=10)
shift_entry.place(relx=0.68, rely=0.7, anchor=W)  # Adjusted relx

advance_button = Button(
    browse_frame,
    text=">",
    command=advance_signal_clicked,
    width=5
)
advance_button.place(relx=0.78, rely=0.7, anchor=W)  # Adjusted relx

delay_button = Button(
    browse_frame,
    text="<",
    command=delay_signal_clicked,
    width=5
)
delay_button.place(relx=0.85, rely=0.7, anchor=W)  # Adjusted relx

# ----------------- Fold button (NEW) -----------------
fold_button = Button(
    browse_frame,
    text="Fold",
    command=fold_signal_clicked,
    width=8
)
fold_button.place(relx=0.92, rely=0.7, anchor=W)

rootWin.mainloop()