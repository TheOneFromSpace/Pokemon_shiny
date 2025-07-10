import tkinter as tk
from collection import CollectionPage


class MainApp:
    def __init__(self, root):
        self.root = root
        self.logged_in = False  # Track login state
        self.current_user = None  # Track current user
        self.setup_main_window()

    def setup_main_window(self):
        """Initialize main window widgets and settings"""
        self.root.title("Sun Shiny Hunting Tool")
        self.root.geometry("800x600+100+100")
        self.root.resizable(False, False)

        # Main UI Elements
        tk.Label(self.root, text="Sun Shiny Hunting Tool",
                 font=('Arial', 24)).pack(expand=True, pady=20)

        # Dynamic button based on login state
        self.collection_button = tk.Button(
            self.root,
            text="Open Collection Page",
            command=self.open_collection
        )
        self.collection_button.pack(pady=20)

        # self.update_ui_state()

    # def update_ui_state(self):
    #     """Update UI based on login state"""
    #     if self.logged_in:
    #         self.collection_button.config(text=f"Continue as {self.current_user}")
    #     else:
    #         self.collection_button.config(text="Open Collection Page")

    def open_collection(self):
        """Open collection window with current login state"""
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.root.withdraw()

        # Pass current login state to CollectionPage
        collection = CollectionPage(
            parent=self.root,
            on_close=self.on_collection_close,
            initial_position=(x, y),
            logged_in=self.logged_in,
            current_user=self.current_user
        )

        # Update our state when collection window closes
        self.window = collection.window
        self.root.wait_window(self.window)

    def on_collection_close(self, position, logged_in, current_user):
        """Handle collection window closing"""
        self.logged_in = logged_in
        self.current_user = current_user
        self.root.geometry(f"800x600+{position[0]}+{position[1]}")
        self.root.deiconify()
        #self.update_ui_state()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()