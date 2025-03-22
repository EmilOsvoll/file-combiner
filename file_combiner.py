import os
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import messagebox
import threading

class FileCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Combiner")
        self.root.geometry("1000x700")  # Wider for dual-panel layout
        self.root.minsize(800, 650)    # Set minimum window size
        
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
        
        # File selection with dual panel layout
        file_frame = ttk.LabelFrame(self.main_frame, text="Step 2: Select Files to Combine", padding="10")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create a paned window for the split view
        paned = ttk.PanedWindow(file_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left panel - File browser tree
        left_panel = ttk.Frame(paned)
        paned.add(left_panel, weight=1)
        
        # Buttons for tree view
        tree_btn_frame = ttk.Frame(left_panel)
        tree_btn_frame.pack(fill=tk.X)
        
        ttk.Button(tree_btn_frame, text="Refresh", command=self.refresh_tree).pack(side=tk.LEFT, padx=5)
        ttk.Button(tree_btn_frame, text="Expand All", command=lambda: self.expand_all_items(True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(tree_btn_frame, text="Collapse All", command=lambda: self.expand_all_items(False)).pack(side=tk.LEFT, padx=5)
        
        # Tree view with scrollbars
        tree_container = ttk.Frame(left_panel)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Add vertical scrollbar
        vsb_tree = ttk.Scrollbar(tree_container, orient="vertical")
        vsb_tree.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add horizontal scrollbar
        hsb_tree = ttk.Scrollbar(tree_container, orient="horizontal")
        hsb_tree.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create the tree view
        self.tree = ttk.Treeview(tree_container)
        self.tree.heading('#0', text='Files and Folders', anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Connect scrollbars to treeview
        self.tree.configure(yscrollcommand=vsb_tree.set, xscrollcommand=hsb_tree.set)
        vsb_tree.configure(command=self.tree.yview)
        hsb_tree.configure(command=self.tree.xview)
        
        # Bind events for tree
        self.tree.bind("<Double-1>", self.toggle_item)
        
        # Center panel - Transfer buttons
        center_panel = ttk.Frame(paned, width=50)  # Fixed width for button panel
        paned.add(center_panel, weight=0)
        
        # Add padding around buttons
        button_frame = ttk.Frame(center_panel, padding="10")
        button_frame.pack(expand=True)
        
        # Add buttons for transferring items
        ttk.Button(button_frame, text=">", command=self.add_selected, width=3).pack(pady=10)
        ttk.Button(button_frame, text="<", command=self.remove_selected, width=3).pack(pady=10)
        
        # Right panel - Selected files list
        right_panel = ttk.Frame(paned)
        paned.add(right_panel, weight=1)
        
        # Button for clearing selection
        ttk.Button(right_panel, text="Clear All", command=self.clear_selection).pack(anchor=tk.W, padx=5, pady=5)
        
        # Listbox with scrollbar for selected files
        list_container = ttk.Frame(right_panel)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        vsb_list = ttk.Scrollbar(list_container, orient="vertical")
        vsb_list.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.selected_listbox = tk.Listbox(list_container, selectmode=tk.EXTENDED)
        self.selected_listbox.pack(fill=tk.BOTH, expand=True)
        self.selected_listbox.configure(yscrollcommand=vsb_list.set)
        vsb_list.configure(command=self.selected_listbox.yview)
        
        # Set initial pane sizes (use the correct method names)
        # ttk.PanedWindow doesn't support paneconfig, so we'll set the weights when adding them
        # No need to call any additional methods here
        
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
    
    def select_root_directory(self):
        directory = filedialog.askdirectory(title="Select Root Directory")
        if directory:
            self.root_directory = directory
            self.root_dir_var.set(directory)
            self.status_var.set(f"Root directory set to: {directory}")
            
            # Clear previous list and refresh tree
            self.selected_files = []
            self.selected_listbox.delete(0, tk.END)
            self.refresh_tree()
    
    def refresh_tree(self):
        if not self.root_directory:
            messagebox.showwarning("Warning", "Please select a root directory first.")
            return
            
        # Clear existing tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Root node
        root_node = self.tree.insert('', 'end', text=os.path.basename(self.root_directory), 
                               open=True, values=[self.root_directory, "directory"])
        
        # Populate the tree
        self.populate_tree(root_node, self.root_directory)
        
        # Expand the root node
        self.tree.item(root_node, open=True)
        
    def populate_tree(self, parent, path, depth=1):
        try:
            # Skip certain directories to avoid clutter
            skip_dirs = ['.git', '__pycache__', 'node_modules', '.vscode', '.idea']
            
            # List all items in the directory
            items = sorted(os.listdir(path))
            
            # First add directories
            for item in items:
                item_path = os.path.join(path, item)
                
                # If it's a directory
                if os.path.isdir(item_path) and item not in skip_dirs:
                    # Insert the directory into the tree
                    node = self.tree.insert(parent, 'end', text=item, 
                                     values=[item_path, "directory"])
                    
                    # Only recurse if the depth is not too great (to avoid slowdown)
                    if depth < 8:  # Limit recursion depth
                        self.populate_tree(node, item_path, depth + 1)
                    elif len(os.listdir(item_path)) > 0:
                        # Add a placeholder if there are items but depth limit is reached
                        self.tree.insert(node, 'end', text="...", values=["", "placeholder"])
            
            # Then add files
            for item in items:
                item_path = os.path.join(path, item)
                
                # If it's a file
                if os.path.isfile(item_path):
                    # Insert the file into the tree
                    self.tree.insert(parent, 'end', text=item, 
                                     values=[item_path, "file"])
                    
        except PermissionError:
            # Add an error node if permission is denied
            self.tree.insert(parent, 'end', text="Permission denied", values=["", "error"])
        except Exception as e:
            # Add an error node for any other exception
            self.tree.insert(parent, 'end', text=f"Error: {str(e)}", values=["", "error"])
    
    def toggle_item(self, event):
        """Toggle expand/collapse on double-click"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            # Get type of item
            values = self.tree.item(item, "values")
            if len(values) >= 2:
                item_type = values[1]
                
                # Only toggle directories
                if item_type == "directory":
                    if self.tree.item(item, "open"):
                        self.tree.item(item, open=False)
                    else:
                        self.tree.item(item, open=True)
                        
                        # If this item has a placeholder, remove it and add actual items
                        children = self.tree.get_children(item)
                        if len(children) == 1 and self.tree.item(children[0], "values")[1] == "placeholder":
                            self.tree.delete(children[0])
                            item_path = self.tree.item(item, "values")[0]
                            self.populate_tree(item, item_path)
    
    def add_selected(self):
        """Add selected tree items to the right panel"""
        selected_items = self.tree.selection()
        
        if not selected_items:
            messagebox.showinfo("Information", "Please select files or folders in the left panel first.")
            return
            
        # Process all selected items
        for item in selected_items:
            item_values = self.tree.item(item, "values")
            item_path = item_values[0]
            item_type = item_values[1]
            
            if item_type == "directory":
                # If it's a directory, add all files in it recursively
                self.add_directory_files(item_path)
            elif item_type == "file":
                # If it's a file, add it if not already in the list
                if item_path not in self.selected_files:
                    self.selected_files.append(item_path)
                    rel_path = os.path.relpath(item_path, self.root_directory)
                    self.selected_listbox.insert(tk.END, rel_path)
        
        # Update status
        self.status_var.set(f"{len(self.selected_files)} files selected")
    
    def add_directory_files(self, directory):
        """Add all files in a directory and its subdirectories"""
        try:
            for root, dirs, files in os.walk(directory):
                # Skip certain directories to avoid clutter
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.vscode', '.idea']]
                
                # Add each file
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in self.selected_files:
                        self.selected_files.append(file_path)
                        rel_path = os.path.relpath(file_path, self.root_directory)
                        self.selected_listbox.insert(tk.END, rel_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error adding directory files: {str(e)}")
    
    def remove_selected(self):
        """Remove selected items from the right panel"""
        selected_indices = self.selected_listbox.curselection()
        
        if not selected_indices:
            messagebox.showinfo("Information", "Please select files to remove in the right panel first.")
            return
            
        # Remove items in reverse order to avoid index shifting
        for i in sorted(selected_indices, reverse=True):
            rel_path = self.selected_listbox.get(i)
            full_path = os.path.join(self.root_directory, rel_path)
            
            # Remove from selected files list
            if full_path in self.selected_files:
                self.selected_files.remove(full_path)
            
            # Remove from listbox
            self.selected_listbox.delete(i)
        
        # Update status
        self.status_var.set(f"{len(self.selected_files)} files selected")
    
    def clear_selection(self):
        """Clear all selected files"""
        self.selected_files = []
        self.selected_listbox.delete(0, tk.END)
        self.status_var.set("Selection cleared")
    
    def expand_all_items(self, expand=True):
        """Expand or collapse all items in the tree"""
        def _expand_all(node):
            for child in self.tree.get_children(node):
                # Check if this is a directory
                item_values = self.tree.item(child, "values")
                if len(item_values) >= 2 and item_values[1] == "directory":
                    self.tree.item(child, open=expand)
                    
                    # If expanding and this item has a placeholder, replace it
                    if expand:
                        children = self.tree.get_children(child)
                        if len(children) == 1 and self.tree.item(children[0], "values")[1] == "placeholder":
                            self.tree.delete(children[0])
                            item_path = self.tree.item(child, "values")[0]
                            self.populate_tree(child, item_path)
                    
                    # Recurse
                    _expand_all(child)
        
        # Start recursion from the root
        for child in self.tree.get_children():
            self.tree.item(child, open=expand)
            _expand_all(child)
    
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