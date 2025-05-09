import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from pygments import lex
from pygments.lexers import get_lexer_by_name, TextLexer
import sys
import os

EXTENSION_MAP = {
    '.py': 'python',
    '.html': 'html',
    '.css': 'css',
    '.bat': 'batch',
    '.idk': None,   # treat as plain text (like .txt)
}

class ScriptPad:
    def __init__(self, root, file_to_load=None):
        self.root = root
        self.root.title("ScriptPad - Untitled")

        # Main text area
        self.text = ScrolledText(
            root,
            font=("Consolas", 12),
            undo=True,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#ffffff"
        )
        self.text.pack(fill='both', expand=True)

        # Status bar
        self.status = tk.Label(root, text="", anchor='w', bd=1, relief='sunken')
        self.status.pack(fill='x', side='bottom')

        self.file_path = None
        self.zoom = 100  # percent

        self.setup_menu()
        self.setup_tags()
        self.bind_events()

        if file_to_load:
            self.load_file(file_to_load)
        else:
            self.update_status()

    def setup_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        filemenu = tk.Menu(menu, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save As", command=self.save_file_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menu.add_cascade(label="File", menu=filemenu)

    def setup_tags(self):
        # dark-theme syntax colors
        self.text.tag_configure("Token.Keyword", foreground="#569cd6")
        self.text.tag_configure("Token.Name", foreground="#d4d4d4")
        self.text.tag_configure("Token.Comment", foreground="#6a9955")
        self.text.tag_configure("Token.String", foreground="#ce9178")
        self.text.tag_configure("Token.Number", foreground="#b5cea8")
        self.text.tag_configure("Token.Operator", foreground="#d4d4d4")

    def bind_events(self):
        # update status on edits and cursor moves
        self.text.bind('<<Modified>>', lambda e: self.on_modified())
        self.text.bind('<KeyRelease>', lambda e: self.update_status())
        self.text.bind('<ButtonRelease>', lambda e: self.update_status())

    def on_modified(self):
        # reset modified flag and update status
        self.text.edit_modified(False)
        self.update_status()

    def highlight(self, content, lexer_name):
        lexer = get_lexer_by_name(lexer_name) if lexer_name else TextLexer()
        # clear old tags
        for tag in self.text.tag_names():
            self.text.tag_remove(tag, "1.0", "end")
        # apply new
        index = "1.0"
        for token, value in lex(content, lexer):
            lines = value.split('\n')
            for i, line in enumerate(lines):
                if line:
                    end_index = f"{index}+{len(line)}c"
                    self.text.tag_add(str(token), index, end_index)
                if i < len(lines) - 1:
                    row, _ = map(int, index.split('.'))
                    index = f"{row+1}.0"
                else:
                    index = f"{index}+{len(line)}c"

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if path:
            self.load_file(path)

    def load_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text.delete("1.0", "end")
            self.text.insert("1.0", content)
            ext = os.path.splitext(path)[1]
            lexer_name = EXTENSION_MAP.get(ext, None)
            self.highlight(content, lexer_name)
            self.file_path = path
            self.root.title(f"ScriptPad - {self.file_path}")
            self.update_status()
        except Exception as e:
            tk.messagebox.showerror("Load Error", f"Could not open file:\n{e}")

    def save_file(self):
        if self.file_path:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", "end-1c"))
        else:
            self.save_file_as()

    def save_file_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            self.file_path = path
            self.save_file()
            self.root.title(f"ScriptPad - {self.file_path}")
            self.update_status()

    def update_status(self):
        # get line, column
        idx = self.text.index("insert").split('.')
        line, col = idx[0], str(int(idx[1]) + 1)
        # char count
        chars = len(self.text.get("1.0", "end-1c"))
        # line endings & encoding
        eol = "Windows (CRLF)"
        enc = "UTF-8"
        status_text = (
            f"Ln {line}, Col {col}   |   {chars} chars   |   "
            f"{self.zoom}%   |   {eol}   |   {enc}"
        )
        self.status.config(text=status_text)

if __name__ == "__main__":
    file_to_open = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    app = ScriptPad(root, file_to_open)
    root.mainloop()