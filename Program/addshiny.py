import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from db import dbconnection as dbc


class AddShinyWindow:
    def __init__(self, parent, initial_position, db_connection, username, on_success=None):
        self.parent = parent
        self.db_conn = db_connection
        self.username = username
        self.on_success = on_success
        self.pokemon_images = {}

        self.window = tk.Toplevel(parent)
        self.window.title("Add New Shiny Pokémon")
        self.window.geometry(f"600x800+{initial_position[0]}+{initial_position[1]}")
        self.window.resizable(False, False)

        self.create_widgets()
        self.load_pokemon_list()
        self.load_methods_list()
        self.load_games_list()
        self.load_balls_list()

        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.focus_set()

    def create_widgets(self):
        """Create all form widgets"""
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        # Header
        tk.Label(main_frame, text="Add New Shiny Pokémon",
                 font=('Arial', 18, 'bold')).pack(pady=10)

        # Form frame
        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill='x', pady=10)

        # Pokémon Selection
        tk.Label(form_frame, text="Pokémon:", font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.pokemon_var = tk.StringVar()
        self.pokemon_combobox = ttk.Combobox(form_frame, textvariable=self.pokemon_var, font=('Arial', 12))
        self.pokemon_combobox.grid(row=0, column=1, sticky='ew', pady=5)
        self.pokemon_combobox.bind('<<ComboboxSelected>>', self.update_pokemon_image)

        # Pokémon Image Preview
        self.pokemon_img_frame = tk.Frame(form_frame, height=150, width=150, bg='white')
        self.pokemon_img_frame.grid(row=1, column=0, columnspan=2, pady=10)
        self.pokemon_img_label = tk.Label(self.pokemon_img_frame)
        self.pokemon_img_label.pack()

        # Nickname
        tk.Label(form_frame, text="Nickname (optional):", font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=5)
        self.nickname_entry = tk.Entry(form_frame, font=('Arial', 12))
        self.nickname_entry.grid(row=2, column=1, sticky='ew', pady=5)

        # Gender
        tk.Label(form_frame, text="Gender:", font=('Arial', 12)).grid(row=3, column=0, sticky='w', pady=5)
        self.gender_var = tk.StringVar(value="Unknown")
        gender_frame = tk.Frame(form_frame)
        gender_frame.grid(row=3, column=1, sticky='w', pady=5)
        tk.Radiobutton(gender_frame, text="♂ Male", variable=self.gender_var, value="Male", font=('Arial', 11)).pack(
            side='left')
        tk.Radiobutton(gender_frame, text="♀ Female", variable=self.gender_var, value="Female",
                       font=('Arial', 11)).pack(side='left', padx=10)
        tk.Radiobutton(gender_frame, text="Unknown", variable=self.gender_var, value="Unknown",
                       font=('Arial', 11)).pack(side='left')

        # Game
        tk.Label(form_frame, text="Game:", font=('Arial', 12)).grid(row=4, column=0, sticky='w', pady=5)
        self.game_var = tk.StringVar()
        self.game_combobox = ttk.Combobox(form_frame, textvariable=self.game_var, font=('Arial', 12))
        self.game_combobox.grid(row=4, column=1, sticky='ew', pady=5)

        # Method
        tk.Label(form_frame, text="Method:", font=('Arial', 12)).grid(row=5, column=0, sticky='w', pady=5)
        self.method_var = tk.StringVar()
        self.method_combobox = ttk.Combobox(form_frame, textvariable=self.method_var, font=('Arial', 12))
        self.method_combobox.grid(row=5, column=1, sticky='ew', pady=5)

        # Poké Ball
        tk.Label(form_frame, text="Poké Ball:", font=('Arial', 12)).grid(row=6, column=0, sticky='w', pady=5)
        self.ball_var = tk.StringVar()
        self.ball_combobox = ttk.Combobox(form_frame, textvariable=self.ball_var, font=('Arial', 12))
        self.ball_combobox.grid(row=6, column=1, sticky='ew', pady=5)

        # OT Name
        tk.Label(form_frame, text="OT Name:", font=('Arial', 12)).grid(row=7, column=0, sticky='w', pady=5)
        self.otname_entry = tk.Entry(form_frame, font=('Arial', 12))
        self.otname_entry.grid(row=7, column=1, sticky='ew', pady=5)
        self.otname_entry.insert(0, self.username)  # Default to current username

        # Date Caught
        tk.Label(form_frame, text="Date Caught:", font=('Arial', 12)).grid(row=8, column=0, sticky='w', pady=5)
        self.date_entry = tk.Entry(form_frame, font=('Arial', 12))
        self.date_entry.grid(row=8, column=1, sticky='ew', pady=5)

        # Time Caught
        tk.Label(form_frame, text="Time Caught:", font=('Arial', 12)).grid(row=9, column=0, sticky='w', pady=5)
        self.time_entry = tk.Entry(form_frame, font=('Arial', 12))
        self.time_entry.grid(row=9, column=1, sticky='ew', pady=5)

        # Encounters
        tk.Label(form_frame, text="Encounters:", font=('Arial', 12)).grid(row=10, column=0, sticky='w', pady=5)
        self.encounters_entry = tk.Entry(form_frame, font=('Arial', 12))
        self.encounters_entry.grid(row=10, column=1, sticky='ew', pady=5)
        self.encounters_entry.insert(0, "0")  # Default to 0

        # Video Link
        tk.Label(form_frame, text="Video Link (optional):", font=('Arial', 12)).grid(row=11, column=0, sticky='w',
                                                                                     pady=5)
        self.video_entry = tk.Entry(form_frame, font=('Arial', 12))
        self.video_entry.grid(row=11, column=1, sticky='ew', pady=5)

        # Notes
        tk.Label(form_frame, text="Notes (optional):", font=('Arial', 12)).grid(row=12, column=0, sticky='nw', pady=5)
        self.notes_text = tk.Text(form_frame, height=5, width=30, font=('Arial', 11), wrap='word')
        self.notes_text.grid(row=12, column=1, sticky='ew', pady=5)

        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)

        tk.Button(button_frame, text="Cancel", command=self.close,
                  font=('Arial', 12), width=10).pack(side='right', padx=10)
        tk.Button(button_frame, text="Add Shiny", command=self.add_shiny,
                  font=('Arial', 12, 'bold'), width=15).pack(side='right')

        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)

    def load_pokemon_list(self):
        """Load all Pokémon from database into combobox"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT pokemonname FROM pokedex ORDER BY dexnr")
            pokemon_list = [row[0] for row in cursor.fetchall()]
            self.pokemon_combobox['values'] = pokemon_list
        except Exception as e:
            messagebox.showerror("Error", f"Could not load Pokémon list:\n{str(e)}")

    def load_methods_list(self):
        """Load all hunting methods from database into combobox"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT methodname FROM huntingmethod ORDER BY methodname")
            methods_list = [row[0] for row in cursor.fetchall()]
            self.method_combobox['values'] = methods_list
        except Exception as e:
            messagebox.showerror("Error", f"Could not load methods list:\n{str(e)}")

    def load_games_list(self):
        """Load all games from database into combobox"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT gamename FROM game ORDER BY gamename")
            games_list = [row[0] for row in cursor.fetchall()]
            self.game_combobox['values'] = games_list
        except Exception as e:
            messagebox.showerror("Error", f"Could not load games list:\n{str(e)}")

    def load_balls_list(self):
        """Load all Poké Balls from database into combobox"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT ballname FROM pokeball ORDER BY ballname")
            balls_list = [row[0] for row in cursor.fetchall()]
            self.ball_combobox['values'] = balls_list
        except Exception as e:
            messagebox.showerror("Error", f"Could not load Poké Balls list:\n{str(e)}")

    def update_pokemon_image(self, event=None):
        """Update the Pokémon image preview when selection changes"""
        pokemon_name = self.pokemon_var.get()
        if not pokemon_name:
            return

        if pokemon_name in self.pokemon_images:
            img = self.pokemon_images[pokemon_name]
        else:
            try:
                # Try to load from images folder
                image_path = os.path.join("images", "pokemon", f"{pokemon_name.lower()}.png")
                img = Image.open(image_path)
                img = img.resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.pokemon_images[pokemon_name] = photo
            except Exception as e:
                # Fallback if image not found
                fallback_img = Image.new('RGBA', (150, 150), (255, 255, 255, 0))
                draw = ImageDraw.Draw(fallback_img)
                draw.text((10, 65), pokemon_name, fill="black", font=ImageFont.load_default())
                photo = ImageTk.PhotoImage(fallback_img)
                self.pokemon_images[pokemon_name] = photo

        self.pokemon_img_label.config(image=photo)
        self.pokemon_img_label.image = photo  # Keep reference

    def add_shiny(self):
        """Add the new shiny Pokémon to the database"""
        # Validate required fields
        if not self.pokemon_var.get():
            messagebox.showerror("Error", "Please select a Pokémon")
            return
        if not self.game_var.get():
            messagebox.showerror("Error", "Please select a game")
            return
        if not self.method_var.get():
            messagebox.showerror("Error", "Please select a method")
            return
        if not self.ball_var.get():
            messagebox.showerror("Error", "Please select a Poké Ball")
            return
        if not self.date_entry.get():
            messagebox.showerror("Error", "Please enter a date")
            return

        try:
            cursor = self.db_conn.cursor()

            # Get IDs for foreign keys
            cursor.execute("SELECT dexnr FROM pokedex WHERE pokemonname = ?", (self.pokemon_var.get(),))
            pokemon_id = cursor.fetchone()[0]

            cursor.execute("SELECT gameld FROM game WHERE gamename = ?", (self.game_var.get(),))
            game_id = cursor.fetchone()[0]

            cursor.execute("SELECT methodId FROM huntingmethod WHERE methodname = ?", (self.method_var.get(),))
            method_id = cursor.fetchone()[0]

            cursor.execute("SELECT ballnr FROM pokeball WHERE ballname = ?", (self.ball_var.get(),))
            ball_id = cursor.fetchone()[0]

            # Insert the new shiny
            cursor.execute("""
                INSERT INTO caughtshiny (
                    pokemon, gender, nickname, pokeball, username, otname,
                    game_caught, method, date_caught, time_caught, encounters,
                    video_link, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pokemon_id,
                self.gender_var.get(),
                self.nickname_entry.get() or None,
                ball_id,
                self.username,
                self.otname_entry.get(),
                game_id,
                method_id,
                self.date_entry.get(),
                self.time_entry.get() or None,
                int(self.encounters_entry.get()),
                self.video_entry.get() or None,
                self.notes_text.get("1.0", "end-1c") or None
            ))

            self.db_conn.commit()
            messagebox.showinfo("Success", "Shiny Pokémon added successfully!")

            if self.on_success:
                self.on_success()  # Refresh the collection view

            self.close()

        except Exception as e:
            messagebox.showerror("Database Error", f"Could not add shiny Pokémon:\n{str(e)}")
            self.db_conn.rollback()

    def close(self):
        """Close the window"""
        self.window.destroy()