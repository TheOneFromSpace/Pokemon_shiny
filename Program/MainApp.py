import tkinter as tk
from collection import CollectionPage


class MainApp:
    def __init__(self, root):
        self.root = root
        self.setup_main_window()

    def setup_main_window(self):
        """Initialize main window widgets and settings"""
        self.root.title("Sun Shiny Hunting Tool")
        self.root.geometry("800x600+100+100")  # Default position
        self.root.resizable(False, False)

        # Main UI Elements
        tk.Label(self.root, text="Sun Shiny Hunting Tool",
                 font=('Arial', 24)).pack(expand=True, pady=20)

        tk.Button(self.root, text="Open Collection Page",
                  command=self.open_collection).pack(pady=20)

    def open_collection(self):
        """Open collection window in same position as main window"""
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.root.withdraw()  # Hide main window

        # Create collection window and pass position callback
        CollectionPage(
            parent=self.root,
            on_close=lambda pos: self.on_collection_close(pos),
            initial_position=(x, y)
        )

    def on_collection_close(self, position):
        """Show main window at new position"""
        self.root.geometry(f"800x600+{position[0]}+{position[1]}")
        self.root.deiconify()  # Show main window


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()