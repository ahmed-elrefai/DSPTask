# main_gui.py (or replace your current GUI file)
from tkinter import *
from tkinter import filedialog, messagebox
import logic                # import module (we mutate lists in logic)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

selected_path = ""   # currently browsed file path

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

browse_button = Button(browse_frame, text="Browse", command=browse, width=10)
browse_button.place(relx=0.28, rely=0.3, anchor=E)

add_button = Button(browse_frame, text="Add Signal", command=add_signal_clicked, width=12)
add_button.place(relx=0.48, rely=0.3, anchor=W)

plot_button = Button(browse_frame, text="Plot Accumulated", command=plot_accumulated, width=14)
plot_button.place(relx=0.68, rely=0.3, anchor=W)

reset_button = Button(browse_frame, text="Reset", command=reset_accumulated, width=8)
reset_button.place(relx=0.88, rely=0.3, anchor=W)

rootWin.mainloop()
