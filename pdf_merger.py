# MIT License
# Copyright (c) 2025 Grant Getzfrid

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from pypdf import PdfWriter
import os

# --- Constants for Styling ---
BG_COLOR = "#FFFFFF"
BORDER_COLOR = "#D1D5DA"
TEXT_COLOR = "#24292E"
TEXT_SECONDARY_COLOR = "#586069"
LINK_COLOR = "#0366D6"
BUTTON_BG_COLOR = "#F6F8FA"
BUTTON_BORDER_COLOR = "#D1D5DA"
BUTTON_HOVER_COLOR = "#F3F4F6"
COMPILE_BUTTON_BG = "#002060"
COMPILE_BUTTON_HOVER = "#003399"
COMPILE_BUTTON_TEXT = "#FFFFFF"

FONT_NORMAL = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_LARGE_BOLD = ("Segoe UI", 14, "bold")


class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Book Compiler")
        self.root.geometry("550x600")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.pdf_files = []
        self._create_widgets()
        self._update_ui_state()

    def _create_widgets(self):
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.list_container = tk.Frame(
            main_frame,
            bg=BG_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
        )
        self.list_container.pack(fill=tk.BOTH, expand=True)
        self.list_container.drop_target_register(DND_FILES)
        self.list_container.dnd_bind("<<Drop>>", self._handle_drop)

        self.file_listbox = tk.Listbox(
            self.list_container,
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=FONT_NORMAL,
            selectbackground=LINK_COLOR,
            selectforeground=BG_COLOR,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.drop_zone_frame = self._create_drop_zone(self.list_container)
        self.drop_zone_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.button_frame = tk.Frame(main_frame, bg=BG_COLOR)
        self.button_frame.pack(fill=tk.X, pady=(15, 10))

        self.btn_up = self._create_styled_button(
            self.button_frame, "Move Up", self._move_up
        )
        self.btn_up.pack(side=tk.LEFT, expand=True, padx=(0, 5))
        self.btn_down = self._create_styled_button(
            self.button_frame, "Move Down", self._move_down
        )
        self.btn_down.pack(side=tk.LEFT, expand=True, padx=5)
        self.btn_remove = self._create_styled_button(
            self.button_frame, "Remove", self._remove_selected
        )
        self.btn_remove.pack(side=tk.LEFT, expand=True, padx=5)
        self.btn_clear = self._create_styled_button(
            self.button_frame, "Clear All", self._clear_all
        )
        self.btn_clear.pack(side=tk.LEFT, expand=True, padx=(5, 0))

        self.compile_button = tk.Button(
            main_frame,
            text="Compile Book",
            font=FONT_BOLD,
            bg=COMPILE_BUTTON_BG,
            fg=COMPILE_BUTTON_TEXT,
            activebackground=COMPILE_BUTTON_HOVER,
            activeforeground=COMPILE_BUTTON_TEXT,
            command=self._compile_pdfs,
            relief="flat",
            borderwidth=0,
            pady=8,
        )
        self.compile_button.pack(fill=tk.X)

    def _create_drop_zone(self, parent):
        frame = tk.Frame(parent, bg=BG_COLOR)
        frame.drop_target_register(DND_FILES)
        frame.dnd_bind("<<Drop>>", self._handle_drop)

        # THE EMOJI ICON THAT WAS HERE IS NOW GONE.

        main_text = tk.Label(
            frame,
            text="Drag PDFs here to compile them",
            font=FONT_LARGE_BOLD,
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        # Add padding to keep it centered vertically
        main_text.pack(pady=(120, 0))

        sub_text_frame = tk.Frame(frame, bg=BG_COLOR)
        sub_text_frame.pack(pady=5)
        tk.Label(
            sub_text_frame, text="Or", font=FONT_NORMAL, bg=BG_COLOR, fg=TEXT_SECONDARY_COLOR
        ).pack(side=tk.LEFT)
        choose_link = tk.Label(
            sub_text_frame,
            text="choose your files",
            font=FONT_NORMAL,
            bg=BG_COLOR,
            fg=LINK_COLOR,
            cursor="hand2",
        )
        choose_link.pack(side=tk.LEFT, padx=4)
        choose_link.bind("<Button-1>", self._browse_files)

        for widget in (main_text, choose_link):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._handle_drop)
        return frame

    def _create_styled_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=FONT_BOLD,
            bg=BUTTON_BG_COLOR,
            fg=TEXT_COLOR,
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=TEXT_COLOR,
            relief="solid",
            borderwidth=1,
            highlightbackground=BUTTON_BORDER_COLOR,
        )
        btn.config(highlightthickness=1, highlightbackground=BUTTON_BORDER_COLOR)
        return btn

    def _handle_drop(self, event):
        self._add_files(self.root.tk.splitlist(event.data))

    def _browse_files(self, event=None):
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF Documents", "*.pdf")],
        )
        if files:
            self._add_files(files)

    def _add_files(self, file_paths):
        added = False
        for file_path in file_paths:
            if file_path.lower().endswith(".pdf") and file_path not in self.pdf_files:
                self.pdf_files.append(file_path)
                added = True
        if added:
            self._update_ui_state()

    def _update_ui_state(self):
        self.file_listbox.delete(0, tk.END)
        if not self.pdf_files:
            self.drop_zone_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.compile_button.config(state=tk.DISABLED)
            for btn in (self.btn_up, self.btn_down, self.btn_remove, self.btn_clear):
                btn.config(state=tk.DISABLED)
        else:
            self.drop_zone_frame.place_forget()
            for file_path in self.pdf_files:
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
            self.compile_button.config(state=tk.NORMAL)
            for btn in (self.btn_up, self.btn_down, self.btn_remove, self.btn_clear):
                btn.config(state=tk.NORMAL)

    def _move_up(self):
        selected_indices = self.file_listbox.curselection()
        if not selected_indices: return
        idx = selected_indices[0]
        if idx > 0:
            self.pdf_files[idx], self.pdf_files[idx - 1] = self.pdf_files[idx - 1], self.pdf_files[idx]
            self._update_ui_state()
            self.file_listbox.selection_set(idx - 1)

    def _move_down(self):
        selected_indices = self.file_listbox.curselection()
        if not selected_indices: return
        idx = selected_indices[0]
        if idx < len(self.pdf_files) - 1:
            self.pdf_files[idx], self.pdf_files[idx + 1] = self.pdf_files[idx + 1], self.pdf_files[idx]
            self._update_ui_state()
            self.file_listbox.selection_set(idx + 1)

    def _remove_selected(self):
        selected_indices = self.file_listbox.curselection()
        if not selected_indices: return
        for idx in sorted(selected_indices, reverse=True):
            del self.pdf_files[idx]
        self._update_ui_state()

    def _clear_all(self):
        self.pdf_files.clear()
        self._update_ui_state()

    def _compile_pdfs(self):
        if not self.pdf_files:
            messagebox.showwarning("No Files", "Please add PDF files to compile.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            title="Save Compiled Book As...",
            initialfile="Compiled Book.pdf",
        )
        if not output_path: return

        merger = PdfWriter()
        try:
            for pdf_path in self.pdf_files:
                merger.append(pdf_path)
            merger.write(output_path)
            merger.close()
            messagebox.showinfo("Success", f"Successfully compiled book to:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during compilation:\n{e}")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFMergerApp(root)
    root.mainloop()