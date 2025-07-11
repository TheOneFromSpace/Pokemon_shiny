import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
from auth import AuthWindow
from addshiny import AddShinyWindow
from db import dbconnection as dbc


class CollectionPage:
    def __init__(self, parent, on_close, initial_position, logged_in=False, current_user=None):
        self.parent = parent
        self.on_close = on_close
        self.logged_in = logged_in
        self.current_user = current_user
        self.pokemon_images = {}  # Cache for pokemon images

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
        for widget in self.right_nav.winfo_children():
            widget.destroy()

        if self.logged_in:
            tk.Button(self.right_nav, text=f"👤 {self.current_user}",
                      bg="#505050", fg="white",
                      relief='flat', font=('Arial', 10)).pack(side='left', padx=8)

            tk.Button(self.right_nav, text="✨ Add Shiny",
                      command=self.open_add_shiny,
                      bg="#505050", fg="white",
                      relief='flat', activebackground="#606060",
                      font=('Arial', 10)).pack(side='left', padx=8)

            tk.Button(self.right_nav, text="Logout",
                      command=self.logout,
                      bg="#505050", fg="white",
                      relief='flat', activebackground="#606060",
                      font=('Arial', 10)).pack(side='left')
        else:
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
        for widget in self.content.winfo_children():
            widget.destroy()

        if self.logged_in:
            tk.Label(self.content, text="Your Pokémon Collection",
                     font=('Arial', 24)).pack(pady=20)
            tk.Label(self.content, text=f"Welcome back, {self.current_user}!",
                     font=('Arial', 14)).pack(pady=10)
            self.show_collection_items()
        else:
            tk.Label(self.content, text="Pokémon Collection",
                     font=('Arial', 24)).pack(pady=50)
            tk.Label(self.content, text="Please login to view your shiny collection",
                     font=('Arial', 14)).pack(pady=10)

    def get_pokemon_image(self, pokemon_name):
        """Load and cache pokemon images"""
        if pokemon_name in self.pokemon_images:
            return self.pokemon_images[pokemon_name]

        try:
            # Try to load from images folder (adjust path as needed)
            image_path = os.path.join("images", "pokemon", f"{pokemon_name.lower()}.png")
            img = Image.open(image_path)
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.pokemon_images[pokemon_name] = photo
            return photo
        except:
            # Fallback if image not found
            fallback_img = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
            draw = ImageDraw.Draw(fallback_img)
            draw.text((10, 40), pokemon_name, fill="black")
            photo = ImageTk.PhotoImage(fallback_img)
            self.pokemon_images[pokemon_name] = photo
            return photo

    def show_collection_items(self):
        """Display the user's collection as image buttons"""
        try:
            conn = dbc.get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    cs.shinyid,
                    pb.pokemonname,
                    cs.gender,
                    cs.nickname,
                    pball.ballname,
                    cs.username,
                    cs.otname,
                    g.gamename,
                    hm.methodname,
                    cs.date_caught,
                    cs.time_caught,
                    cs.encounters,
                    cs.video_link,
                    cs.notes
                FROM caughtshiny cs
                JOIN pokedex pb ON cs.pokemon = pb.dexnr
                JOIN pokeball pball ON cs.pokeball = pball.ballnr
                JOIN game g ON cs.game_caught = g.gameid
                JOIN huntingmethod hm ON cs.method = hm.methodId
                WHERE cs.username = ?
                ORDER BY cs.date_caught DESC, cs.time_caught DESC
            """, (self.current_user,))

            # Create a scrollable canvas
            container = tk.Frame(self.content)
            container.pack(fill='both', expand=True)

            canvas = tk.Canvas(container)
            scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Display pokemon as image buttons in a grid
            row, col = 0, 0
            max_cols = 5  # Number of columns in the grid

            for shiny in cursor.fetchall():
                shinyid, pokemon, gender, nickname, ballname, username, otname, gamename, methodname, \
                    date_caught, time_caught, encounters, video_link, notes = shiny

                # Get pokemon image
                img = self.get_pokemon_image(pokemon)

                # Create button with image and name
                btn_frame = tk.Frame(scrollable_frame, padx=5, pady=5)
                btn_frame.grid(row=row, column=col, padx=5, pady=5)

                btn = tk.Button(
                    btn_frame,
                    image=img,
                    compound='top',
                    text=nickname if nickname else pokemon,
                    command=lambda s=shiny: self.show_shiny_details(s),
                    width=100,
                    height=120,
                    font=('Arial', 10)
                )
                btn.image = img  # Keep reference to prevent garbage collection
                btn.pack()

                # Add shiny star indicator
                tk.Label(btn_frame, text="⭐", font=('Arial', 10)).pack()

                # Update grid position
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load collection:\n{str(e)}")

    def show_shiny_details(self, shiny):
        """Show a detailed popup for the selected shiny"""
        shinyid, pokemon, gender, nickname, ballname, username, otname, gamename, methodname, \
            date_caught, time_caught, encounters, video_link, notes = shiny

        details_window = tk.Toplevel(self.window)
        details_window.title(f"Shiny {pokemon} Details")
        details_window.geometry(f"500x700+{self.window.winfo_x() + 50}+{self.window.winfo_y() + 50}")

        # Main frame
        main_frame = tk.Frame(details_window, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        # Header with pokemon image and name
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill='x', pady=10)

        try:
            img_path = os.path.join("recources", "PNG", "sprites","pokedb","scarlet-violet","normal",f"{pokemon.lower()}.png")
            img = Image.open(img_path)
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(header_frame, image=photo)
            img_label.image = photo
            img_label.pack(side='left', padx=10)
        except:
            pass

        name_frame = tk.Frame(header_frame)
        name_frame.pack(side='left', fill='y', padx=10)

        display_name = nickname if nickname else pokemon
        tk.Label(name_frame, text=f"✨ {display_name} ✨",
                 font=('Arial', 18, 'bold')).pack(anchor='w')
        tk.Label(name_frame, text=f"OT: {otname}",
                 font=('Arial', 12)).pack(anchor='w')
        tk.Label(name_frame, text=f"Caught in: {gamename}",
                 font=('Arial', 12)).pack(anchor='w')

        # Details frame
        details_frame = tk.Frame(main_frame)
        details_frame.pack(fill='x', pady=10)

        # Left column
        left_col = tk.Frame(details_frame)
        left_col.pack(side='left', fill='both', expand=True)

        tk.Label(left_col, text=f"Gender: {gender}",
                 font=('Arial', 12), anchor='w').pack(fill='x')
        tk.Label(left_col, text=f"Poké Ball: {ballname}",
                 font=('Arial', 12), anchor='w').pack(fill='x')
        tk.Label(left_col, text=f"Method: {methodname}",
                 font=('Arial', 12), anchor='w').pack(fill='x')

        # Right column
        right_col = tk.Frame(details_frame)
        right_col.pack(side='right', fill='both', expand=True)

        tk.Label(right_col, text=f"Date: {date_caught}",
                 font=('Arial', 12), anchor='w').pack(fill='x')
        tk.Label(right_col, text=f"Time: {time_caught}",
                 font=('Arial', 12), anchor='w').pack(fill='x')
        tk.Label(right_col, text=f"Encounters: {encounters}",
                 font=('Arial', 12), anchor='w').pack(fill='x')

        # Notes section
        notes_frame = tk.LabelFrame(main_frame, text="Notes", padx=10, pady=10)
        notes_frame.pack(fill='both', expand=True, pady=10)

        notes_text = tk.Text(notes_frame, height=5, wrap='word', font=('Arial', 11))
        notes_text.pack(fill='both', expand=True)
        notes_text.insert('1.0', notes if notes else "No notes available")
        notes_text.config(state='disabled')

        # Video link if available
        if video_link:
            video_frame = tk.Frame(main_frame)
            video_frame.pack(fill='x', pady=10)

            tk.Label(video_frame, text="Video Proof:",
                     font=('Arial', 12, 'bold')).pack(anchor='w')
            link = tk.Label(video_frame, text=video_link,
                            font=('Arial', 11), fg='blue', cursor='hand2')
            link.pack(anchor='w')
            link.bind("<Button-1>", lambda e: self.open_link(video_link))

        # Close button
        tk.Button(main_frame, text="Close", command=details_window.destroy,
                  font=('Arial', 12), width=15).pack(pady=10)

    def open_link(self, url):
        """Helper function to open URLs"""
        import webbrowser
        webbrowser.open_new(url)

    def open_add_shiny(self):
        """Open the Add Shiny window with database connection"""
        if not self.logged_in:
            messagebox.showerror("Error", "You must be logged in to add shinies")
            return

        try:
            conn = dbc.get_db_connection()
            AddShinyWindow(
                parent=self.window,
                initial_position=(
                    self.window.winfo_x() + 50,
                    self.window.winfo_y() + 50
                ),
                db_connection=conn,
                username=self.current_user,
                on_success=self.update_content  # Refresh after adding
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to database:\n{str(e)}")

    def show_auth(self):
        """Show authentication window"""
        auth = AuthWindow(
            parent=self.window,
            initial_position=(
                self.window.winfo_x() + 100,
                self.window.winfo_y() + 100
            )
        )
        self.window.wait_window(auth.window)

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
        self.on_close(pos, self.logged_in, self.current_user)