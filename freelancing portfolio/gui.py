#!/usr/bin/env python3
"""
Invoice OCR Extractor — Tkinter GUI
Drag-and-drop or browse to add invoice PDFs/images, then click Extract.
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from extractor import process_file, save_to_excel


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Invoice OCR Extractor')
        self.geometry('780x560')
        self.resizable(True, True)
        self.configure(bg='#1e1e2e')

        self.files = []
        self._build_ui()

    # ------------------------------------------------------------------ UI --
    def _build_ui(self):
        # Title bar
        tk.Label(self, text='🧾 Invoice OCR Extractor',
                 font=('Helvetica', 18, 'bold'),
                 bg='#1e1e2e', fg='#cdd6f4').pack(pady=(18, 4))
        tk.Label(self, text='Add PDF or image invoices → extract data → save to Excel',
                 font=('Helvetica', 10), bg='#1e1e2e', fg='#a6adc8').pack()

        # Drop zone / file list frame
        list_frame = tk.Frame(self, bg='#181825', bd=2, relief='groove')
        list_frame.pack(fill='both', expand=True, padx=20, pady=12)

        tk.Label(list_frame, text='Files to process',
                 font=('Helvetica', 10, 'bold'),
                 bg='#181825', fg='#89b4fa').pack(anchor='w', padx=8, pady=(6, 0))

        self.listbox = tk.Listbox(list_frame, bg='#181825', fg='#cdd6f4',
                                  selectbackground='#313244',
                                  font=('Courier', 10), bd=0,
                                  highlightthickness=0)
        self.listbox.pack(fill='both', expand=True, padx=8, pady=6)

        # Buttons row
        btn_frame = tk.Frame(self, bg='#1e1e2e')
        btn_frame.pack(fill='x', padx=20)

        self._btn(btn_frame, '+ Add Files', self._add_files).pack(side='left', padx=(0, 6))
        self._btn(btn_frame, '+ Add Folder', self._add_folder).pack(side='left', padx=(0, 6))
        self._btn(btn_frame, '✕ Remove Selected', self._remove_selected, danger=True).pack(side='left')
        self._btn(btn_frame, '⬇ Extract → Excel', self._start_extract,
                  accent=True).pack(side='right')

        # Output path row
        out_frame = tk.Frame(self, bg='#1e1e2e')
        out_frame.pack(fill='x', padx=20, pady=(10, 4))
        tk.Label(out_frame, text='Output file:', bg='#1e1e2e',
                 fg='#a6adc8', font=('Helvetica', 10)).pack(side='left')
        self.out_var = tk.StringVar(value='output/extracted.xlsx')
        tk.Entry(out_frame, textvariable=self.out_var, bg='#313244', fg='#cdd6f4',
                 insertbackground='white', font=('Courier', 10),
                 relief='flat', bd=4, width=40).pack(side='left', padx=6)
        self._btn(out_frame, 'Browse', self._browse_out).pack(side='left')

        # Status / log
        self.status = tk.StringVar(value='Ready.')
        tk.Label(self, textvariable=self.status, bg='#1e1e2e',
                 fg='#a6e3a1', font=('Helvetica', 10)).pack(pady=(4, 0))

        self.progress = ttk.Progressbar(self, mode='indeterminate', length=300)
        self.progress.pack(pady=(4, 14))

    def _btn(self, parent, text, cmd, accent=False, danger=False):
        bg = '#89b4fa' if accent else ('#f38ba8' if danger else '#313244')
        fg = '#1e1e2e' if accent else '#cdd6f4'
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=fg, activebackground=bg,
                         font=('Helvetica', 10, 'bold' if accent else 'normal'),
                         relief='flat', padx=10, pady=5, cursor='hand2')

    # --------------------------------------------------------------- Actions --
    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title='Select invoice files',
            filetypes=[('Invoices', '*.pdf *.png *.jpg *.jpeg *.tiff *.bmp'),
                       ('All files', '*.*')])
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.listbox.insert('end', p)

    def _add_folder(self):
        folder = filedialog.askdirectory(title='Select folder of invoices')
        if not folder:
            return
        supported = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
        for f in sorted(os.listdir(folder)):
            if os.path.splitext(f)[1].lower() in supported:
                full = os.path.join(folder, f)
                if full not in self.files:
                    self.files.append(full)
                    self.listbox.insert('end', full)

    def _remove_selected(self):
        for idx in reversed(self.listbox.curselection()):
            self.listbox.delete(idx)
            self.files.pop(idx)

    def _browse_out(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel file', '*.xlsx')])
        if path:
            self.out_var.set(path)

    def _start_extract(self):
        if not self.files:
            messagebox.showwarning('No files', 'Please add at least one invoice file.')
            return
        self.progress.start(10)
        self.status.set('Extracting…')
        threading.Thread(target=self._extract_thread, daemon=True).start()

    def _extract_thread(self):
        data_list = []
        for idx, f in enumerate(self.files):
            self.status.set(f'Processing {idx+1}/{len(self.files)}: {os.path.basename(f)}')
            try:
                data_list.append(process_file(f))
            except Exception as e:
                print(f'[WARN] {f}: {e}')

        out = self.out_var.get()
        if data_list:
            save_to_excel(data_list, out=out)
            self.status.set(f'✓ Done! Saved {len(data_list)} invoice(s) → {out}')
            messagebox.showinfo('Done', f'Extracted {len(data_list)} invoice(s).\nSaved to:\n{out}')
        else:
            self.status.set('No data extracted. Check console for errors.')

        self.progress.stop()


if __name__ == '__main__':
    app = App()
    app.mainloop()
