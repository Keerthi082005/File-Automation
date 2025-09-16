
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from organizer import Organizer
from pathlib import Path

class OrganizerGUI:
    def __init__(self, root):
        self.root = root
        root.title("File Organizer")
        root.geometry("580x360")
        root.resizable(False, False)

        self.folder_path = tk.StringVar()

        frame = ttk.Frame(root, padding=12)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Select folder to organize:").grid(row=0, column=0, sticky='w')
        entry = ttk.Entry(frame, textvariable=self.folder_path, width=55)
        entry.grid(row=1, column=0, sticky='w', pady=6)
        ttk.Button(frame, text="Browse", command=self.browse).grid(row=1, column=1, padx=6)

        self.organize_btn = ttk.Button(frame, text="Organize Now", command=self.start_organize)
        self.organize_btn.grid(row=2, column=0, pady=8, sticky='w')
        ttk.Button(frame, text="Undo Last", command=self.undo_last).grid(row=2, column=1, pady=8, sticky='w')

        self.progress = ttk.Progressbar(frame, length=520, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, pady=8)

        self.status = tk.StringVar(value="Ready")
        ttk.Label(frame, textvariable=self.status).grid(row=4, column=0, columnspan=2, sticky='w')

        # Summary treeview
        self.tree = ttk.Treeview(frame, columns=('count',), show='headings', height=8)
        self.tree.heading('count', text='Count')
        self.tree.grid(row=5, column=0, columnspan=2, pady=8, sticky='nsew')
        self.tree.column('count', width=80, anchor='center')

    def browse(self):
        p = filedialog.askdirectory()
        if p:
            self.folder_path.set(p)

    def start_organize(self):
        folder = self.folder_path.get().strip()
        if not folder:
            messagebox.showwarning("No folder", "Please select a folder to organize.")
            return
        try:
            self.organizer = Organizer(folder)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        # Run in thread to keep UI responsive
        t = threading.Thread(target=self._run_organize, daemon=True)
        t.start()

    def _run_organize(self):
        self._set_ui_running(True)
        self.progress['value'] = 0
        self.status.set("Scanning files...")
        moved = []
        def progress_cb(text):
            # simple textual progress; update status and increment progress bar slightly
            self.status.set(text)
            self.progress.step(5)
        try:
            moved = self.organizer.organize(show_progress=progress_cb)
            self.status.set(f"Done. Moved {len(moved)} files.")
            self._update_summary(moved)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self._set_ui_running(False)
            self.progress['value'] = 100

    def _set_ui_running(self, running):
        if running:
            self.organize_btn.config(state='disabled')
        else:
            self.organize_btn.config(state='normal')

    def _update_summary(self, moved):
        # Clear
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Aggregate by folder name of destination
        counts = {}
        for entry in moved:
            dest = Path(entry['dest'])
            category = dest.parent.name
            counts[category] = counts.get(category, 0) + 1
        for cat, cnt in counts.items():
            self.tree.insert('', 'end', values=(f"{cat}: {cnt}",))
        if not counts:
            self.tree.insert('', 'end', values=("No files moved",))

    def undo_last(self):
        folder = self.folder_path.get().strip()
        if not folder:
            messagebox.showwarning("No folder", "Please select the same folder used for organizing.")
            return
        try:
            organizer = Organizer(folder)
            res = organizer.undo_last()
            messagebox.showinfo("Undo Result", f"Restored {res.get('restored',0)} files. Errors: {len(res.get('errors',[]))}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == '__main__':
    root = tk.Tk()
    app = OrganizerGUI(root)
    root.mainloop()
