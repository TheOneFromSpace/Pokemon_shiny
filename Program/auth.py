import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
import pyodbc
from db import dbconnection as dbc


class AuthWindow:
    def __init__(self, parent, initial_position):
        self.logged_in = False  # Add this
        self.current_user = None  # Add this
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Authentication")
        self.window.geometry(f"400x500+{initial_position[0]}+{initial_position[1]}")
        self.window.resizable(False, False)
        self.conn = None

        self.create_notebook()
        self.window.protocol("WM_DELETE_WINDOW", self.cleanup)
        self.window.grab_set()

    def create_notebook(self):
        """Create tabbed interface"""
        self.tabs = ttk.Notebook(self.window)
        self.tabs.pack(expand=True, fill='both')

        # Login Tab
        login_frame = tk.Frame(self.tabs)
        self.create_login_form(login_frame)
        self.tabs.add(login_frame, text="Login")

        # Signup Tab
        signup_frame = tk.Frame(self.tabs)
        self.create_signup_form(signup_frame)
        self.tabs.add(signup_frame, text="Sign Up")

    def create_login_form(self, frame):
        """Login form widgets"""
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
        """Signup form widgets"""
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

    def hash_password(self, password: str) -> bytes:
        """Hash a password with bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def verify_password(self, password: str, hashed: bytes) -> bool:
        """Verify password against stored hash"""
        try:
            # Handle both string and bytes input from database
            if isinstance(hashed, str):
                # Convert hex string back to bytes if needed
                if hashed.startswith('\\x'):
                    hashed = bytes.fromhex(hashed[2:])
                else:
                    hashed = hashed.encode('latin1')
            return bcrypt.checkpw(password.encode('utf-8'), hashed)
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

    def get_connection(self):
        """Get database connection with error handling"""
        if not self.conn:
            try:
                self.conn = dbc.get_db_connection()
            except pyodbc.Error as e:
                messagebox.showerror("Database Error",
                                     f"Connection failed:\n{str(e)}")
                raise
        return self.conn

    def attempt_login(self):
        """Handle login attempt with hashed password verification"""
        username = self.login_user.get().strip()
        password = self.login_pass.get()

        if not username or not password:
            messagebox.showerror("Error", "Both fields are required")
            return

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT password FROM account WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()

            if not result:
                messagebox.showerror("Error", "Invalid credentials")
                return

            stored_hash = result[0]
            print(f"Debug: Stored hash type={type(stored_hash)}, value={stored_hash}")

            if self.verify_password(password, stored_hash):
                messagebox.showinfo("Success", f"Welcome {username}!")
                self.logged_in = True  # Add this
                self.current_user = username  # Add this
                self.cleanup()
            else:
                messagebox.showerror("Error", "Invalid credentials")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def attempt_signup(self):
        """Handle account creation with password hashing"""
        username = self.signup_user.get().strip()
        password = self.signup_pass.get()
        confirm = self.signup_confirm.get()

        if not (username and password and confirm):
            messagebox.showerror("Error", "All fields are required")
            return

        if len(username) < 4:
            messagebox.showerror("Error", "Username must be at least 4 characters")
            return

        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Check if username exists
            cursor.execute(
                "SELECT username FROM account WHERE username = ?",
                (username,)
            )
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                return

            # Hash password and store
            hashed_pw = self.hash_password(password)
            print(f"Debug: New hash to store: {hashed_pw}")

            cursor.execute(
                "INSERT INTO account (username, password) VALUES (?, ?)",
                (username, hashed_pw)
            )
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            self.cleanup()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            if conn:
                conn.rollback()

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except:
                pass
        self.window.destroy()

    def close(self):
        """Alias for cleanup"""
        self.cleanup()