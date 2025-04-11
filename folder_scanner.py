import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def build_ascii_tree(directory, prefix="", is_last=True, is_root=False):
    """
    Recursively return a list of lines for an ASCII-like directory tree.
    
    Parameters:
      directory: Path to a directory (string)
      prefix:    Current prefix to display before items (string)
      is_last:   Is this directory the last item at its level? (bool)
      is_root:   Is this the very first call for the top directory? (bool)
    """
    lines = []

    # The name to display:
    if is_root:
        name = "."  # Display a dot for the root
    else:
        # For sub-directories, show only the basename
        name = os.path.basename(directory)

    # Determine which prefix to use for this directory
    connector = "└── " if is_last else "├── "

    # If this is the root directory (very top), show just a dot
    # Otherwise, show prefix + connector + name
    if is_root:
        lines.append(name) 
    else:
        lines.append(prefix + connector + name)

    # Gather all entries in the directory
    try:
        entries = sorted(os.listdir(directory))
    except PermissionError:
        # If we lack permission, indicate that
        lines.append(prefix + "    [Access Denied]")
        return lines

    # Separate directories and files for nicer grouping (dirs first)
    dirs = [e for e in entries if os.path.isdir(os.path.join(directory, e))]
    files = [e for e in entries if os.path.isfile(os.path.join(directory, e))]

    # We'll combine them back but keep dirs first
    combined = dirs + files

    # For each child item, figure out if it's the last one at this level
    for i, entry in enumerate(combined):
        entry_path = os.path.join(directory, entry)

        # Determine if this is the last item in the combined list
        child_is_last = (i == len(combined) - 1)

        # Choose the next prefix
        if is_root:
            # Root has no lines above it, so just an empty prefix
            next_prefix = ""
        else:
            # If this item is not the last, add "│   ", else "    "
            next_prefix = prefix + ("    " if is_last else "│   ")

        # If it's a directory, recurse
        if os.path.isdir(entry_path):
            lines.extend(build_ascii_tree(
                entry_path,
                prefix=next_prefix,
                is_last=child_is_last,
                is_root=False
            ))
        else:
            # It's a file, so just add it
            file_connector = "└── " if child_is_last else "├── "
            lines.append(next_prefix + file_connector + entry)

    return lines

def browse_folder():
    """Prompt the user to pick a folder to scan."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_var.set(folder_selected)
        display_box.delete("1.0", tk.END)  # Clear display on new selection

def scan_and_display():
    """Scan the chosen folder and display its content (ASCII tree)."""
    folder_path = folder_var.get()
    if not folder_path or not os.path.isdir(folder_path):
        messagebox.showerror("Error", "Please select a valid folder path.")
        return
    
    # Clear the display box
    display_box.delete("1.0", tk.END)
    
    # Build the ASCII tree
    tree_lines = build_ascii_tree(folder_path, prefix="", is_last=True, is_root=True)
    if tree_lines:
        # Insert the lines into the text box
        for line in tree_lines:
            display_box.insert(tk.END, line + "\n")
    else:
        display_box.insert(tk.END, "No items found in the selected folder.")

def save_to_file():
    """Prompt user to select a text file path and save the displayed tree to it."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if file_path:
        # Get the text from the display box
        text_content = display_box.get("1.0", tk.END).rstrip("\n")
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text_content)
            messagebox.showinfo("Success", f"Folder tree saved to: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

# Main application window
root = tk.Tk()
root.title("ASCII Tree Folder Scanner")

folder_var = tk.StringVar()

# Frame for folder selection
folder_frame = tk.Frame(root)
folder_frame.pack(pady=10, padx=10, fill='x')

folder_label = tk.Label(folder_frame, text="Folder to scan:")
folder_label.pack(side=tk.LEFT)

folder_entry = tk.Entry(folder_frame, textvariable=folder_var, width=50)
folder_entry.pack(side=tk.LEFT, padx=5)

browse_button = tk.Button(folder_frame, text="Browse...", command=browse_folder)
browse_button.pack(side=tk.LEFT)

# Button to scan
scan_button = tk.Button(root, text="Scan Folder", command=scan_and_display)
scan_button.pack(pady=5)

# ScrolledText box to display results
display_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
display_box.pack(pady=5, padx=10)

# Button to save
save_button = tk.Button(root, text="Save to TXT File", command=save_to_file)
save_button.pack(pady=5)

root.mainloop()
