import os
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import messagebox
import threading

class FileCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Combiner")
        self.root.geometry("800x700")  # Increased height from 600 to 700
        self.root.minsize(600, 650)    # Set minimum window size
        
        # Variables
        self.root_directory = ""
        self.selected_files = []
        self.output_file = ""
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Root directory selection
        root_frame = ttk.LabelFrame(self.main_frame, text="Step 1: Select Root Directory", padding="10")
        root_frame.pack(fill=tk.X, pady=5)
        
        self.root_dir_var = tk.StringVar()
        ttk.Entry(root_frame, textvariable=self.root_dir_var, width=70).pack(side=tk.LEFT, padx=5)
        ttk.Button(root_frame, text="Browse", command=self.select_root_directory).pack(side=tk.LEFT, padx=5)
        
        # File selection
        file_frame = ttk.LabelFrame(self.main_frame, text="Step 2: Select Files to Combine", padding="10")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_files).pack(side=tk.LEFT, padx=5)
        
        # File listbox with scrollbar
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=15)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Output file selection
        output_frame = ttk.LabelFrame(self.main_frame, text="Step 3: Specify Output File", padding="10")
        output_frame.pack(fill=tk.X, pady=5)
        
        self.output_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var, width=70).pack(side=tk.LEFT, padx=5)
        ttk.Button(output_frame, text="Browse", command=self.select_output_file).pack(side=tk.LEFT, padx=5)
        
        # Combine button
        combine_frame = ttk.LabelFrame(self.main_frame, text="Step 4: Combine Files", padding="10")
        combine_frame.pack(fill=tk.X, pady=5)
        
        self.progress = ttk.Progressbar(combine_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=10)
        
        # Create the combine button with explicit text and standard button instead of ttk
        self.combine_button = tk.Button(combine_frame, text="Combine Files", 
                                       command=self.combine_files,
                                       font=('Arial', 10),
                                       bg='#e1e1e1',
                                       height=1,
                                       width=15)
        self.combine_button.pack(pady=5)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(self.main_frame, textvariable=self.status_var, font=('Arial', 10)).pack(anchor=tk.W, pady=5)
        
        # Create custom style for the main button
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 11, 'bold'))
    
    def select_root_directory(self):
        directory = filedialog.askdirectory(title="Select Root Directory")
        if directory:
            self.root_directory = directory
            self.root_dir_var.set(directory)
            self.status_var.set(f"Root directory set to: {directory}")
    
    def add_files(self):
        if not self.root_directory:
            messagebox.showwarning("Warning", "Please select a root directory first.")
            return
            
        files = filedialog.askopenfilenames(title="Select Files to Combine", 
                                          initialdir=self.root_directory)
        if files:
            for file in files:
                try:
                    # Improved check for files within root directory or any of its subdirectories
                    # This uses os.path.abspath to handle path differences more reliably
                    file_abs = os.path.abspath(file)
                    root_abs = os.path.abspath(self.root_directory)
                    
                    # Check if file path starts with root path (including subfolders)
                    if file_abs.startswith(root_abs):
                        # Get path relative to root directory
                        rel_path = os.path.relpath(file, self.root_directory)
                        item_text = f"{rel_path}"
                        
                        # Check if file is already in the list
                        if item_text not in [self.file_listbox.get(i) for i in range(self.file_listbox.size())]:
                            self.selected_files.append(file)
                            self.file_listbox.insert(tk.END, item_text)
                    else:
                        messagebox.showwarning("Warning", 
                                             f"File '{os.path.basename(file)}' is not within the root directory.")
                except ValueError:
                    # This handles the case where commonpath might fail
                    messagebox.showwarning("Warning", 
                                         f"File '{os.path.basename(file)}' cannot be compared with the root directory.")
            
            self.status_var.set(f"{len(self.selected_files)} files selected")
    
    def remove_selected(self):
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            return
            
        # Remove items in reverse order to avoid index shifting
        for i in sorted(selected_indices, reverse=True):
            self.file_listbox.delete(i)
            self.selected_files.pop(i)
            
        self.status_var.set(f"{len(self.selected_files)} files selected")
    
    def clear_files(self):
        self.file_listbox.delete(0, tk.END)
        self.selected_files = []
        self.status_var.set("File list cleared")
    
    def select_output_file(self):
        output_file = filedialog.asksaveasfilename(
            title="Save Combined File As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if output_file:
            self.output_file = output_file
            self.output_var.set(output_file)
            self.status_var.set(f"Output file set to: {output_file}")
    
    def combine_files(self):
        if not self.root_directory:
            messagebox.showwarning("Warning", "Please select a root directory.")
            return
            
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select files to combine.")
            return
            
        if not self.output_file:
            messagebox.showwarning("Warning", "Please specify an output file.")
            return
        
        # Start the combination process in a separate thread to avoid freezing the GUI
        self.progress['value'] = 0
        combine_thread = threading.Thread(target=self._combine_files_task)
        combine_thread.daemon = True
        combine_thread.start()
    
    def _generate_tree_view(self, directory, prefix="", is_last=True, exclude_dirs=None):
        """Generate a tree view of the directory structure."""
        if exclude_dirs is None:
            exclude_dirs = ['.git', '__pycache__', 'node_modules', '.vscode', '.idea']
            
        lines = []
        
        # Get relative directory name for the current level
        rel_dir = os.path.relpath(directory, self.root_directory)
        if rel_dir == '.':
            dir_name = os.path.basename(self.root_directory)
        else:
            dir_name = os.path.basename(directory)
            
        # Add this directory to the tree
        if is_last:
            lines.append(f"{prefix}└── {dir_name}/")
            next_prefix = prefix + "    "
        else:
            lines.append(f"{prefix}├── {dir_name}/")
            next_prefix = prefix + "│   "
            
        # Get all items in the directory
        try:
            items = sorted(os.listdir(directory))
            # First process directories, then files
            dirs = [item for item in items if os.path.isdir(os.path.join(directory, item)) and item not in exclude_dirs]
            files = [item for item in items if os.path.isfile(os.path.join(directory, item))]
            
            # Process directories
            for i, item in enumerate(dirs):
                item_path = os.path.join(directory, item)
                is_last_dir = (i == len(dirs) - 1 and len(files) == 0)
                lines.extend(self._generate_tree_view(item_path, next_prefix, is_last_dir, exclude_dirs))
                
            # Process files
            for i, item in enumerate(files):
                if i == len(files) - 1:  # Last item
                    lines.append(f"{next_prefix}└── {item}")
                else:
                    lines.append(f"{next_prefix}├── {item}")
        except PermissionError:
            lines.append(f"{next_prefix}[Permission denied]")
        except Exception as e:
            lines.append(f"{next_prefix}[Error: {str(e)}]")
            
        return lines
        
    def _combine_files_task(self):
        try:
            self.status_var.set("Combining files...")
            total_files = len(self.selected_files)
            
            with open(self.output_file, 'w', encoding='utf-8') as outfile:
                # Add file header with metadata
                import datetime
                current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                outfile.write("=" * 80 + "\n")
                outfile.write("COMBINED FILE INDEX\n")
                outfile.write("=" * 80 + "\n")
                outfile.write(f"Created: {current_date}\n")
                outfile.write(f"Root Directory: {self.root_directory}\n")
                outfile.write(f"Number of Files: {total_files}\n\n")
                
                # Add tree view of the directory structure
                outfile.write("DIRECTORY STRUCTURE\n")
                outfile.write("-" * 80 + "\n")
                
                # Generate the tree view starting from the root directory
                tree_lines = self._generate_tree_view(self.root_directory)
                for line in tree_lines[1:]:  # Skip the first line (root dir with prefix)
                    outfile.write(line + "\n")
                outfile.write("\n")
                
                # Add table of contents with all selected files
                outfile.write("TABLE OF CONTENTS\n")
                outfile.write("-" * 80 + "\n")
                for i, file_path in enumerate(self.selected_files):
                    rel_path = os.path.relpath(file_path, self.root_directory)
                    outfile.write(f"{i+1}. {rel_path}\n")
                
                # Add separator between header and content
                outfile.write("\n" + "=" * 80 + "\n")
                outfile.write("FILE CONTENTS\n")
                outfile.write("=" * 80 + "\n\n")
                
                # Process each file
                for i, file_path in enumerate(self.selected_files):
                    # Update progress bar
                    progress_value = int((i / total_files) * 100)
                    self.root.after(0, lambda v=progress_value: self.progress.configure(value=v))
                    
                    # Get relative path
                    rel_path = os.path.relpath(file_path, self.root_directory)
                    
                    # Write file header with the specified format
                    outfile.write(f"((({rel_path})))\n\n")
                    
                    # Write file contents
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                    except UnicodeDecodeError:
                        # Try with a different encoding if UTF-8 fails
                        try:
                            with open(file_path, 'r', encoding='latin-1') as infile:
                                content = infile.read()
                                outfile.write(content)
                        except Exception as e:
                            outfile.write(f"[Error reading file: {str(e)}]")
                    
                    # Add separator between files
                    outfile.write("\n\n")
            
            # Set progress to 100% when done
            self.root.after(0, lambda: self.progress.configure(value=100))
            self.root.after(0, lambda: self.status_var.set(f"Successfully combined {total_files} files to {self.output_file}"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Successfully combined {total_files} files to {self.output_file}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCombinerApp(root)
    root.mainloop()