import tkinter as tk
from auth import AuthWindow


class CollectionPage:
    def __init__(self, parent, on_close, initial_position):
        self.parent = parent
        self.on_close = on_close
        self.auth_window = None

        self.window = tk.Toplevel(parent)
        self.window.title("Collection Page")
        self.window.geometry(f"800x600+{initial_position[0]}+{initial_position[1]}")
        self.window.resizable(False, False)

        self.create_navbar()
        self.create_content()

        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.focus_set()

    def create_navbar(self):
        navbar = tk.Frame(self.window, bg="#505050", height=50, pady=5)
        navbar.pack(fill='x', side='top')

        # Left items
        left_frame = tk.Frame(navbar, bg="#505050")
        left_frame.pack(side='left', padx=15)
        tk.Button(left_frame, text="← Main Menu",
                  command=self.close,
                  bg="#505050", fg="white",
                  relief='flat', font=('Arial', 10, 'bold')).pack(side='left')

        # Right items
        right_frame = tk.Frame(navbar, bg="#505050")
        right_frame.pack(side='right', padx=15)
        tk.Button(right_frame, text="🔑 Login/Signup",
                  command=self.show_auth,
                  bg="#505050", fg="white",
                  relief='flat', font=('Arial', 10)).pack(side='left')

    def create_content(self):
        self.content = tk.Frame(self.window)
        self.content.pack(expand=True, fill='both', padx=20, pady=20)
        tk.Label(self.content, text="Collection Content",
                 font=('Arial', 24)).pack(pady=50)

    def show_auth(self):
        if not self.auth_window or not tk.Toplevel.winfo_exists(self.auth_window.window):
            x = self.window.winfo_x() + 100
            y = self.window.winfo_y() + 100
            self.auth_window = AuthWindow(
                parent=self.window,
                initial_position=(x, y))
        else:
            self.auth_window.window.lift()

    def close(self):
        pos = (self.window.winfo_x(), self.window.winfo_y())
        self.window.destroy()
        self.on_close(pos)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    CollectionPage(root, lambda pos: root.quit(), (100, 100))
    root.mainloop()