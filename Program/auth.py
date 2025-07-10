import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class AuthWindow:
    def __init__(self, parent, initial_position):
        self.parent = parent

        self.window = tk.Toplevel(parent)
        self.window.title("Authentication")
        self.window.geometry(f"400x500+{initial_position[0]}+{initial_position[1]}")
        self.window.resizable(False, False)

        self.create_notebook()
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.grab_set()

    def create_notebook(self):
        # Create tab system
        self.tabs = tk.ttk.Notebook(self.window)
        self.tabs.pack(expand=True, fill='both')

        # Login tab
        login_frame = tk.Frame(self.tabs)
        self.create_login_form(login_frame)
        self.tabs.add(login_frame, text="Login")

        # Signup tab
        signup_frame = tk.Frame(self.tabs)
        self.create_signup_form(signup_frame)
        self.tabs.add(signup_frame, text="Sign Up")

    def create_login_form(self, frame):
        tk.Label(frame, text="Login", font=('Arial', 16)).pack(pady=20)

        tk.Label(frame, text="Username:").pack()
        self.login_user = tk.Entry(frame)
        self.login_user.pack(pady=5, padx=20, fill='x')

        tk.Label(frame, text="Password:").pack()
        self.login_pass = tk.Entry(frame, show="*")
        self.login_pass.pack(pady=5, padx=20, fill='x')

        tk.Button(frame, text="Login",
                  command=self.attempt_login,
                  width=15).pack(pady=20)

    def create_signup_form(self, frame):
        tk.Label(frame, text="Create Account", font=('Arial', 16)).pack(pady=20)

        tk.Label(frame, text="Username:").pack()
        self.signup_user = tk.Entry(frame)
        self.signup_user.pack(pady=5, padx=20, fill='x')

        tk.Label(frame, text="Password:").pack()
        self.signup_pass = tk.Entry(frame, show="*")
        self.signup_pass.pack(pady=5, padx=20, fill='x')

        tk.Label(frame, text="Confirm Password:").pack()
        self.signup_confirm = tk.Entry(frame, show="*")
        self.signup_confirm.pack(pady=5, padx=20, fill='x')

        tk.Button(frame, text="Sign Up",
                  command=self.attempt_signup,
                  width=15).pack(pady=20)

    def attempt_login(self):
        username = self.login_user.get()
        password = self.login_pass.get()

        if not (username and password):
            messagebox.showerror("Error", "All fields are required")
            return

        # Add real authentication here
        messagebox.showinfo("Success", f"Welcome {username}!")
        self.close()

    def attempt_signup(self):
        username = self.signup_user.get()
        password = self.signup_pass.get()
        confirm = self.signup_confirm.get()

        if not (username and password and confirm):
            messagebox.showerror("Error", "All fields are required")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords don't match")
            return

        # Add real registration here
        messagebox.showinfo("Success", "Account created successfully!")
        self.close()

    def close(self):
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    AuthWindow(root, (100, 100))
    root.mainloop()