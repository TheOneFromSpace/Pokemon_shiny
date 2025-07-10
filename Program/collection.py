import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthWindow


class CollectionPage:
    def __init__(self, parent, on_close, initial_position, logged_in=False, current_user=None):
        self.parent = parent
        self.on_close = on_close
        self.logged_in = logged_in
        self.current_user = current_user

        self.window = tk.Toplevel(parent)
        self.window.title("Collection Page")
        self.window.geometry(f"800x600+{initial_position[0]}+{initial_position[1]}")
        self.window.resizable(False, False)

        self.create_navbar()
        self.create_content()

        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.focus_set()

    def create_navbar(self):
        """Create navigation bar with dynamic buttons"""
        self.navbar = tk.Frame(self.window, bg="#505050", height=50, pady=5)
        self.navbar.pack(fill='x', side='top')

        # Left items (always visible)
        left_frame = tk.Frame(self.navbar, bg="#505050")
        left_frame.pack(side='left', padx=15)
        tk.Button(left_frame, text="← Main Menu",
                  command=self.close,
                  bg="#505050", fg="white",
                  relief='flat', font=('Arial', 10, 'bold')).pack(side='left')

        # Right items (dynamic based on login)
        self.right_nav = tk.Frame(self.navbar, bg="#505050")
        self.right_nav.pack(side='right', padx=15)
        self.update_auth_buttons()

    def update_auth_buttons(self):
        """Update the auth buttons based on login state"""
        # Clear existing buttons
        for widget in self.right_nav.winfo_children():
            widget.destroy()

        if self.logged_in:
            # Show account and logout buttons
            tk.Button(self.right_nav, text=f"👤 {self.current_user}",
                      bg="#505050", fg="white",
                      relief='flat', font=('Arial', 10)).pack(side='left', padx=8)

            tk.Button(self.right_nav, text="Logout",
                      command=self.logout,
                      bg="#505050", fg="white",
                      relief='flat', activebackground="#606060",
                      font=('Arial', 10)).pack(side='left')
        else:
            # Show login/signup button
            tk.Button(self.right_nav, text="🔑 Login/Signup",
                      command=self.show_auth,
                      bg="#505050", fg="white",
                      relief='flat', font=('Arial', 10)).pack(side='left')

    def create_content(self):
        """Main content area"""
        self.content = tk.Frame(self.window)
        self.content.pack(expand=True, fill='both', padx=20, pady=20)
        self.update_content()

    def update_content(self):
        """Update content based on login state"""
        # Clear existing content
        for widget in self.content.winfo_children():
            widget.destroy()

        if self.logged_in:
            # Show collection content for logged-in users
            tk.Label(self.content, text="Your Pokémon Collection",
                     font=('Arial', 24)).pack(pady=20)
            tk.Label(self.content, text=f"Welcome back, {self.current_user}!",
                     font=('Arial', 14)).pack(pady=10)

            # Add your actual collection items here
            # Example:
            # self.show_pokemon_collection()

        else:
            # Show login prompt for guests
            tk.Label(self.content, text="Pokémon Collection",
                     font=('Arial', 24)).pack(pady=50)
            tk.Label(self.content, text="Please login to view your shiny collection",
                     font=('Arial', 14)).pack(pady=10)

    def show_auth(self):
        """Show authentication window"""
        auth = AuthWindow(
            parent=self.window,
            initial_position=(
                self.window.winfo_x() + 100,
                self.window.winfo_y() + 100
            )
        )
        # Wait for auth window to close
        self.window.wait_window(auth.window)

        # Update our state if login was successful
        if hasattr(auth, 'logged_in') and auth.logged_in:
            self.logged_in = True
            self.current_user = auth.current_user
            self.update_auth_buttons()
            self.update_content()

    def logout(self):
        """Handle logout"""
        self.logged_in = False
        self.current_user = None
        self.update_auth_buttons()
        self.update_content()
        messagebox.showinfo("Logged Out", "You have been logged out")

    def close(self):
        """Close the window and return state to main menu"""
        pos = (self.window.winfo_x(), self.window.winfo_y())
        self.window.destroy()
        # Pass back our current login state
        self.on_close(pos, self.logged_in, self.current_user)

    # Optional: Add your collection display methods here
    # def show_pokemon_collection(self):
    #     """Display the user's Pokémon collection"""
    #     pass