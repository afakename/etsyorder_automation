import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

# Load CSV file
def load_csv():
    global df
    file_path = filedialog.askopenfilename(title="Select Etsy CSV File", filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        display_orders()
        messagebox.showinfo("Success", "CSV Loaded Successfully")

# Display Orders in Listbox
def display_orders():
    listbox.delete(0, tk.END)
    for index, row in df.iterrows():
        order_info = f"{row['Order ID']} - {row['Buyer']} - {row['Variations']}"
        listbox.insert(tk.END, order_info)

# Mark Selected Order as Processed
def mark_processed():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Select an Order to Process")
        return
    index = selected[0]
    df.at[index, 'Processed'] = 'Yes'
    display_orders()
    messagebox.showinfo("Success", "Order Marked as Processed")

# Save Updated CSV
def save_csv():
    save_path = filedialog.asksaveasfilename(title="Save Updated CSV", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if save_path:
        df.to_csv(save_path, index=False)
        messagebox.showinfo("Success", "CSV Saved Successfully")

# Create GUI Window
root = tk.Tk()
root.title("Etsy Order Tracker")
root.geometry("500x400")

# Buttons & Listbox
btn_load = tk.Button(root, text="Load CSV", command=load_csv)
btn_load.pack(pady=5)

listbox = tk.Listbox(root, width=60, height=15)
listbox.pack(pady=5)

btn_process = tk.Button(root, text="Mark as Processed", command=mark_processed)
btn_process.pack(pady=5)

btn_save = tk.Button(root, text="Save CSV", command=save_csv)
btn_save.pack(pady=5)

# Run App
root.mainloop()
