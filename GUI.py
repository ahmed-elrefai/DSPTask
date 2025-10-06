from tkinter import *
from tkinter import filedialog
from logic import read_signal, add_signals
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
import matplotlib.pyplot as plt

signal1_path = ""
signal2_path = ""

def plot_signal(idxs1, vals1, idxs2=None, vals2=None):
    # Clear previous plot (if any)
    for widget in remaining_space_frame.winfo_children():
        widget.destroy()
    
    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(6,3), dpi=100)
    ax.plot(idxs1, vals1, marker='o', color='blue', label="Signal 1")

    if idxs2 is not None and vals2 is not None:
        ax.plot(idxs2, vals2, marker='o', color='orange', label="Signal 2")

    ax.set_title("Signal Visualization")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Sample Value")
    ax.grid(True)
    ax.legend()

    # Embed in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=remaining_space_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)



def browse(label_num):
    global signal1_path, signal2_path

    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not path:
        return
    
    if label_num == 1:
        filepath.set(path.split("/")[-1])
        signal1_path = path
    elif label_num == 2:
        filepath2.set(path.split("/")[-1])
        signal2_path = path


def plot():
    global signal1_path, signal2_path
    idxs1 = []
    vals1 = []
    idxs2 = []
    vals2 = []
    if signal1_path and signal2_path:
        read_signal(signal1_path, idxs1, vals1)
        read_signal(signal2_path, idxs2, vals2)
        plot_signal(idxs1, vals1, idxs2, vals2)
    elif signal1_path:
        read_signal(signal1_path, idxs1, vals1)
        plot_signal(idxs1, vals1)
    elif signal2_path:
        read_signal(signal2_path, idxs2, vals2)
        plot_signal(idxs2, vals2)
    else:
        messagebox.showerror("err","no files selected")

def display_signal_sum():
    global signal1_path, signal2_path
    idxs1 = []
    idxs2 = []
    vals1 = []
    vals2 = []

    result = []
    result_idx = []
    read_signal(signal1_path, idxs1, vals1)
    read_signal(signal2_path, idxs2, vals2)
    result, result_idx = add_signals(idxs1,vals1,idxs2, vals2)
    plot_signal(result_idx, result)


rootWin = Tk()
rootWin.title("Task1")
rootWin.geometry("700x500")

# STRINGVARS
filepath = StringVar()
filepath.set("signal slot 1")
filepath2 = StringVar()
filepath2.set("signal slot 2")

# FRAMES
browse_frame = Frame(rootWin, background="#8E8E8E", height=100)
browse_frame.pack(side=BOTTOM, fill=X)
browse_frame.pack_propagate(False)

remaining_space_frame = Frame(rootWin, background="#FEFEFE")
remaining_space_frame.pack(side=LEFT, fill=BOTH, expand=True)

# LABELS
filepath_label1 = Label(browse_frame, textvariable=filepath, font=("Segoe UI", 11))
filepath_label1.place(relx=0.02, rely=0.3, anchor=W)
filepath_label2 = Label(browse_frame, textvariable=filepath2, font=("Segoe UI", 11))
filepath_label2.place(relx=0.02, rely=0.7, anchor=W)

default_ploting_label = Label(
    remaining_space_frame,
    text="no plots yet",
    font=("Segoe UI", 12, "italic"),
    background="#FEFEFE",
    fg="#555555"
)
default_ploting_label.place(relx=0.5, rely=0.5, anchor=CENTER)

# BUTTONS
browse_button1 = Button(browse_frame, text="Browse", command=lambda: browse(1), width=10)
browse_button1.place(relx=0.42, rely=0.3, anchor=E)
browse_button2 = Button(browse_frame, text="Browse", command=lambda: browse(2), width=10)
browse_button2.place(relx=0.42, rely=0.7, anchor=E)
plot_button = Button(browse_frame, text="Plot", command=plot, width=10)
plot_button.place(relx=0.5, rely=0.5, anchor=W)
add_button = Button(browse_frame, text="Add Signals", command=display_signal_sum, width=10)
add_button.place(relx=0.7, rely=0.3, anchor=W)
rootWin.mainloop()
