import tkinter as tk
import random
import json

# Game Constants
# WIDTH = 500  # Removed
# HEIGHT = 500 # Removed
INITIAL_MAP_SIZE_N = 25 # Default number of segments for width and height
SEGMENT_SIZE = 20  # Size of each snake segment and food
GAME_SPEED = 150   # Milliseconds between game updates (lower is faster)

# Colors
BACKGROUND_COLOR = "black"
# SNAKE_COLOR = "green" # Obsolete, defined in palettes
# FOOD_COLOR = "red" # Obsolete, defined in palettes
GAME_OVER_TEXT_COLOR = "white"
HIGH_SCORE_FILE = "highscore.txt"
SETTINGS_FILE = "settings.json"

SNAKE_COLOR_PALETTES = {
    "Green": {"body": "#00FF00", "head": "#00AA00", "food": "#FF0000"},
    "Blue": {"body": "#0000FF", "head": "#0000AA", "food": "#FF0000"},
    "Purple": {"body": "#800080", "head": "#500050", "food": "#FF0000"},
    "Pink": {"body": "#FFC0CB", "head": "#FF80A0", "food": "#FF0000"},
    "Red": {"body": "#FF0000", "head": "#AA0000", "food": "#00FF00"},
}

MOVE_SPEEDS = {
    "Slow": 250,
    "Normal": GAME_SPEED, # Use the existing constant
    "Fast": 75,
}

class SnakeGame:
    def __init__(self, master, map_size_n=INITIAL_MAP_SIZE_N): # map_size_n will be set by menu
        self.master = master
        
        # Initialize default settings values FIRST
        self.map_size_n = INITIAL_MAP_SIZE_N # Default map size
        self.current_snake_color_name = "Green"
        self.current_speed_name = "Normal"
        self.screen_wrapping_enabled = True
        self.grid_brightness = 0

        # Load settings from file, potentially overwriting defaults
        self.load_settings()

        # Initialize dynamic properties based on potentially loaded settings
        self.width = self.map_size_n * SEGMENT_SIZE
        self.height = self.map_size_n * SEGMENT_SIZE
        
        # Initialize color hex values based on current_snake_color_name
        palette = SNAKE_COLOR_PALETTES.get(self.current_snake_color_name, SNAKE_COLOR_PALETTES["Green"])
        self.current_snake_color_hex = palette["body"]
        self.current_food_color_hex = palette["food"]

        # Initialize speed ms based on current_speed_name
        self.current_speed_ms = MOVE_SPEEDS.get(self.current_speed_name, MOVE_SPEEDS["Normal"])

        self.master.title("Simple Snake Game") 
        self.master.resizable(False, False)

        self.canvas = None # Will be created by show_menu / start_game_from_menu
        
        # Game state variables (not part of saved settings)
        self.snake_segments = []
        self.food_coords = (0, 0)
        self.direction = "Right"
        self.new_direction = "Right"
        self.score = 0
        self.game_over_flag = False
        
        # Tkinter variables for menu - initialized AFTER settings are loaded/defaulted
        self.selected_color_var = tk.StringVar(master)
        self.selected_speed_var = tk.StringVar(master)
        self.wrapping_var = tk.BooleanVar(master)
        self.grid_brightness_scale_var = tk.IntVar(master)

        # These .set() calls for Tkinter variables will be done in show_menu()
        # using the now-finalized instance variables.
        
        self.menu_active = True
        self.high_score = self.load_high_score()
        
        # Menu widgets (references initialized to None)
        self.map_size_entry = None
        self.color_label = None # For "Snake Color:"
        self.color_option_menu = None # For color selection
        self.speed_label = None # For "Game Speed:"
        self.speed_option_menu = None # For speed selection
        self.wrapping_checkbutton = None # For Screen Wrapping
        self.grid_brightness_label = None # For "Grid Brightness:"
        self.grid_brightness_slider = None # For grid brightness Scale
        self.start_button = None
        self.exit_button = None
        self.map_label = None
        self.title_text_id = None
        self.highscore_text_id = None
        self.map_label_window_id = None
        self.map_entry_window_id = None
        self.color_label_window_id = None # Canvas ID for color label
        self.color_option_menu_window_id = None # Canvas ID for color option menu
        self.speed_label_window_id = None # Canvas ID for speed label
        self.speed_option_menu_window_id = None # Canvas ID for speed option menu
        self.wrapping_checkbutton_window_id = None # Canvas ID for wrapping Checkbutton
        self.grid_brightness_label_window_id = None # Canvas ID for grid label
        self.grid_brightness_slider_window_id = None # Canvas ID for grid slider
        self.start_button_window_id = None
        self.exit_button_window_id = None

        # Key bindings are context-dependent (menu vs game)
        # Initial call to show menu
        self.show_menu() # __init__ ends by showing the menu

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)

            # Validate and apply settings, falling back to defaults if necessary
            # Map Size
            map_size = settings.get("map_size_n", self.map_size_n)
            if isinstance(map_size, int) and 10 <= map_size <= 50:
                self.map_size_n = map_size
            else:
                print(f"Warning: Invalid map_size_n '{map_size}' in settings. Using default {self.map_size_n}.")


            # Snake Color
            color_name = settings.get("snake_color_name", self.current_snake_color_name)
            if color_name in SNAKE_COLOR_PALETTES:
                self.current_snake_color_name = color_name
            else:
                print(f"Warning: Invalid snake_color_name '{color_name}' in settings. Using default {self.current_snake_color_name}.")
                # Ensure default is set if loaded one was bad
                self.current_snake_color_name = "Green"


            # Game Speed
            speed_name = settings.get("speed_name", self.current_speed_name)
            if speed_name in MOVE_SPEEDS:
                self.current_speed_name = speed_name
            else:
                print(f"Warning: Invalid speed_name '{speed_name}' in settings. Using default {self.current_speed_name}.")
                # Ensure default is set
                self.current_speed_name = "Normal"


            # Screen Wrapping
            wrapping_enabled = settings.get("screen_wrapping_enabled", self.screen_wrapping_enabled)
            if isinstance(wrapping_enabled, bool):
                self.screen_wrapping_enabled = wrapping_enabled
            else:
                print(f"Warning: Invalid screen_wrapping_enabled '{wrapping_enabled}' in settings. Using default {self.screen_wrapping_enabled}.")
                self.screen_wrapping_enabled = True # Default

            # Grid Brightness
            grid_brightness = settings.get("grid_brightness", self.grid_brightness)
            if isinstance(grid_brightness, int) and 0 <= grid_brightness <= 100:
                self.grid_brightness = grid_brightness
            else:
                print(f"Warning: Invalid grid_brightness '{grid_brightness}' in settings. Using default {self.grid_brightness}.")
                self.grid_brightness = 0 # Default


        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            print(f"Info: Settings file '{SETTINGS_FILE}' not found or invalid. Using default settings. ({e})")
            # Defaults are already set in __init__ before this method is called.
            # We just need to ensure dependent variables are correctly initialized based on these defaults.
        
        # Update dependent variables after loading/defaulting primary ones
        palette = SNAKE_COLOR_PALETTES.get(self.current_snake_color_name, SNAKE_COLOR_PALETTES["Green"])
        self.current_snake_color_hex = palette["body"]
        self.current_food_color_hex = palette["food"]
        self.current_speed_ms = MOVE_SPEEDS.get(self.current_speed_name, MOVE_SPEEDS["Normal"])


    def save_settings(self):
        settings_to_save = {
            "map_size_n": self.map_size_n,
            "snake_color_name": self.current_snake_color_name,
            "speed_name": self.current_speed_name,
            "screen_wrapping_enabled": self.screen_wrapping_enabled,
            "grid_brightness": self.grid_brightness,
        }
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings_to_save, f, indent=4)
        except IOError:
            print(f"Warning: Could not save settings to {SETTINGS_FILE}")


    def load_high_score(self):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                score = int(f.read())
                return score
        except (FileNotFoundError, ValueError):
            return 0
            
    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open(HIGH_SCORE_FILE, "w") as f:
                    f.write(str(self.high_score))
            except IOError:
                # Silently ignore if saving fails, or log to console
                print(f"Warning: Could not save high score to {HIGH_SCORE_FILE}")

    def center_window(self):
        """Centers the game window on the screen."""
        self.master.update_idletasks() # Ensure dimensions are calculated
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (self.width / 2))
        y_coordinate = int((screen_height / 2) - (self.height / 2))
        self.master.geometry(f"{self.width}x{self.height}+{x_coordinate}+{y_coordinate}")

    def show_menu(self):
        self.menu_active = True
        self.game_over_flag = False # Reset game over state when showing menu

        # Initial map size for menu display (can be different from game map size)
        menu_map_n = INITIAL_MAP_SIZE_N 
        self.width = menu_map_n * SEGMENT_SIZE
        self.height = menu_map_n * SEGMENT_SIZE

        if not self.canvas:
            self.canvas = tk.Canvas(self.master, width=self.width, height=self.height, bg=BACKGROUND_COLOR)
            self.canvas.pack()
        else:
            self.canvas.config(width=self.width, height=self.height, bg=BACKGROUND_COLOR)
        
        self.center_window() # Center based on menu dimensions
        self.canvas.delete(tk.ALL) # Clear previous drawings (game or menu)
        self.master.title("Snake Game - Menu")

        # Unbind any game-specific keys, or keys from game over screen
        self.unbind_game_keys()
        self.master.unbind("<KeyPress-r>") 
        self.master.unbind("<KeyPress-R>")

        # Menu Title
        self.title_text_id = self.canvas.create_text(
            self.width / 2, self.height / 2 - 150, # Adjusted Y
            text="Snake Game",
            fill=GAME_OVER_TEXT_COLOR, font=("Arial", 30, "bold"), anchor="center"
        )
        # High Score
        self.highscore_text_id = self.canvas.create_text(
            self.width / 2, self.height / 2 - 100, # Adjusted Y
            text=f"High Score: {self.high_score}",
            fill=GAME_OVER_TEXT_COLOR, font=("Arial", 16), anchor="center"
        )

        # Map Size Entry
        self.map_label = tk.Label(self.master, text="Map Size (10-50):", bg=BACKGROUND_COLOR, fg="white", font=("Arial", 10))
        self.map_size_entry = tk.Entry(self.master, font=("Arial", 10), width=5)
        self.map_size_entry.insert(0, str(self.map_size_n)) # Use current map_size_n
        
        self.map_label_window_id = self.canvas.create_window(self.width / 2 - 70, self.height / 2 - 50, anchor="e", window=self.map_label) # Adjusted Y and X
        self.map_entry_window_id = self.canvas.create_window(self.width / 2 - 60, self.height / 2 - 50, anchor="w", window=self.map_size_entry) # Adjusted Y and X

        # Snake Color Selection
        self.color_label = tk.Label(self.master, text="Snake Color:", bg=BACKGROUND_COLOR, fg="white", font=("Arial", 10))
        self.selected_color_var.set(self.current_snake_color_name) # Initialize OptionMenu with current color
        color_options = list(SNAKE_COLOR_PALETTES.keys())
        self.color_option_menu = tk.OptionMenu(self.master, self.selected_color_var, *color_options)
        self.color_option_menu.config(font=("Arial", 8), width=7)

        self.color_label_window_id = self.canvas.create_window(self.width / 2 - 70, self.height / 2 - 10, anchor="e", window=self.color_label) # Adjusted Y
        self.color_option_menu_window_id = self.canvas.create_window(self.width / 2 - 60, self.height / 2 - 10, anchor="w", window=self.color_option_menu) # Adjusted Y

        # Game Speed Selection
        self.speed_label = tk.Label(self.master, text="Game Speed:", bg=BACKGROUND_COLOR, fg="white", font=("Arial", 10))
        self.selected_speed_var.set(self.current_speed_name) # Initialize OptionMenu
        speed_options = list(MOVE_SPEEDS.keys())
        self.speed_option_menu = tk.OptionMenu(self.master, self.selected_speed_var, *speed_options)
        self.speed_option_menu.config(font=("Arial", 8), width=7)

        self.speed_label_window_id = self.canvas.create_window(self.width / 2 - 70, self.height / 2 + 30, anchor="e", window=self.speed_label) # New Y
        self.speed_option_menu_window_id = self.canvas.create_window(self.width / 2 - 60, self.height / 2 + 30, anchor="w", window=self.speed_option_menu) # New Y

        # Screen Wrapping Checkbutton
        self.wrapping_var.set(self.screen_wrapping_enabled) # Initialize Checkbutton state
        self.wrapping_checkbutton = tk.Checkbutton(self.master, text="Screen Wrapping", variable=self.wrapping_var,
                                                   bg=BACKGROUND_COLOR, fg="white", font=("Arial", 10),
                                                   selectcolor=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR,
                                                   activeforeground="white", highlightthickness=0, borderwidth=0)
        self.wrapping_checkbutton_window_id = self.canvas.create_window(self.width / 2, self.height / 2 + 70, anchor="center", window=self.wrapping_checkbutton) # New Y

        # Grid Brightness Slider
        self.grid_brightness_label = tk.Label(self.master, text="Grid Brightness:", bg=BACKGROUND_COLOR, fg="white", font=("Arial", 10))
        self.grid_brightness_scale_var.set(self.grid_brightness) # Initialize Slider
        self.grid_brightness_slider = tk.Scale(self.master, from_=0, to=100, orient=tk.HORIZONTAL,
                                               variable=self.grid_brightness_scale_var,
                                               bg=BACKGROUND_COLOR, fg="white", troughcolor="grey",
                                               highlightthickness=0, length=100, font=("Arial", 8))
        self.grid_brightness_label_window_id = self.canvas.create_window(self.width / 2 - 55, self.height / 2 + 110, anchor="e", window=self.grid_brightness_label) # New Y
        self.grid_brightness_slider_window_id = self.canvas.create_window(self.width / 2 - 50, self.height / 2 + 110, anchor="w", window=self.grid_brightness_slider) # New Y

        # Start Game Button
        self.start_button = tk.Button(self.master, text="Start Game", command=self.start_game_from_menu, font=("Arial", 14), bg="grey", fg="white")
        self.start_button_window_id = self.canvas.create_window(self.width / 2, self.height / 2 + 160, anchor="center", window=self.start_button) # Adjusted Y for more spacing

        # Exit Button
        self.exit_button = tk.Button(self.master, text="Exit", command=self.master.destroy, font=("Arial", 14), bg="grey", fg="white")
        self.exit_button_window_id = self.canvas.create_window(self.width / 2, self.height / 2 + 210, anchor="center", window=self.exit_button) # Adjusted Y for more spacing
        
        self.canvas.focus_set() # For any potential menu key bindings, though not used yet

    def clear_menu_widgets(self):
        # Destroy Tkinter widgets
        if self.map_label: self.map_label.destroy()
        if self.map_size_entry: self.map_size_entry.destroy()
        if self.color_label: self.color_label.destroy()
        if self.color_option_menu: self.color_option_menu.destroy()
        if self.speed_label: self.speed_label.destroy()
        if self.speed_option_menu: self.speed_option_menu.destroy()
        if self.wrapping_checkbutton: self.wrapping_checkbutton.destroy()
        if self.grid_brightness_label: self.grid_brightness_label.destroy()
        if self.grid_brightness_slider: self.grid_brightness_slider.destroy()
        if self.start_button: self.start_button.destroy()
        if self.exit_button: self.exit_button.destroy()
        
        # Nullify references
        self.map_label = self.map_size_entry = self.start_button = self.exit_button = None
        self.color_label = self.color_option_menu = None
        self.speed_label = self.speed_option_menu = None
        self.wrapping_checkbutton = None
        self.grid_brightness_label = self.grid_brightness_slider = None
        
        # Canvas items created with create_text, create_window are cleared by canvas.delete(ALL)
        # but if we stored their IDs, we could delete them individually too.
        # For now, relying on canvas.delete(ALL) before drawing game or new menu.

    def start_game_from_menu(self):
        # Get and validate map size
        try:
            n = int(self.map_size_entry.get())
            if not (10 <= n <= 50):
                print(f"Invalid map size: {n}. Must be between 10 and 50. Using default {self.map_size_n}.")
                n = self.map_size_n # Revert to current if invalid, or default if first time
            else:
                self.map_size_n = n # Update if valid
        except ValueError:
            print(f"Invalid map size input. Using current map size {self.map_size_n}.")
            n = self.map_size_n # Revert to current if invalid input

        self.width = self.map_size_n * SEGMENT_SIZE
        self.height = self.map_size_n * SEGMENT_SIZE

        # Get selected color and update game settings
        selected_color = self.selected_color_var.get()
        self.current_snake_color_name = selected_color
        palette = SNAKE_COLOR_PALETTES[selected_color]
        self.current_snake_color_hex = palette["body"]
        self.current_food_color_hex = palette["food"]

        # Get selected speed and update game settings
        selected_speed = self.selected_speed_var.get()
        self.current_speed_name = selected_speed
        self.current_speed_ms = MOVE_SPEEDS[selected_speed]

        # Get screen wrapping setting
        self.screen_wrapping_enabled = self.wrapping_var.get()

        # Get grid brightness setting
        self.grid_brightness = self.grid_brightness_scale_var.get()

        # Save all settings
        self.save_settings()
        
        self.clear_menu_widgets() # Remove menu widgets
        
        self.canvas.config(width=self.width, height=self.height)
        self.center_window() # Recenter for new game dimensions
        
        self.menu_active = False
        self.bind_game_keys() # Bind keys for game
        self.start_game() # Proceed to game setup

    def start_game(self): # Modified to be called from menu
        self.canvas.delete(tk.ALL) # Clear menu elements or previous game
        self.game_over_flag = False
        self.score = 0
        self.master.title(f"Simple Snake Game - Score: {self.score}")
        self.direction = "Right"
        self.new_direction = "Right"

        mid_x_segment = self.width // (2 * SEGMENT_SIZE)
        mid_y_segment = self.height // (2 * SEGMENT_SIZE)
        start_x_head = mid_x_segment * SEGMENT_SIZE
        start_y_head = mid_y_segment * SEGMENT_SIZE

        self.snake_segments = [
            (start_x_head - 2 * SEGMENT_SIZE, start_y_head),
            (start_x_head - SEGMENT_SIZE, start_y_head),
            (start_x_head, start_y_head)
        ]
        self.create_food()
        self.game_loop() # Start the game's update cycle

    def create_food(self):
        """Places food randomly on the canvas, not on the snake."""
        while True:
            x = random.randrange(0, self.width // SEGMENT_SIZE) * SEGMENT_SIZE
            y = random.randrange(0, self.height // SEGMENT_SIZE) * SEGMENT_SIZE
            self.food_coords = (x, y)
            if self.food_coords not in self.snake_segments:
                break

    def draw_grid(self):
        if self.grid_brightness > 0:
            rgb_val = int(255 * (self.grid_brightness / 100.0))
            grid_color_hex = f"#{rgb_val:02x}{rgb_val:02x}{rgb_val:02x}"

            # Draw vertical lines
            for x in range(0, self.width, SEGMENT_SIZE):
                self.canvas.create_line(x, 0, x, self.height, fill=grid_color_hex, width=1, tags="grid_line")
            
            # Draw horizontal lines
            for y in range(0, self.height, SEGMENT_SIZE):
                self.canvas.create_line(0, y, self.width, y, fill=grid_color_hex, width=1, tags="grid_line")

    def draw_game(self):
        self.canvas.delete(tk.ALL) # Clear previous frame
        self.draw_grid() # Draw grid first

        # Draw food
        self.canvas.create_rectangle(
            self.food_coords[0], self.food_coords[1],
            self.food_coords[0] + SEGMENT_SIZE, self.food_coords[1] + SEGMENT_SIZE,
            fill=self.current_food_color_hex, outline=self.current_food_color_hex, tags="food"
        )

        # Draw snake
        border_color_hex = "#000000" # Black for the border
        
        current_palette = SNAKE_COLOR_PALETTES[self.current_snake_color_name]
        head_color_hex = current_palette["head"]
        body_color_hex = self.current_snake_color_hex # This is already set to current_palette["body"]

        for i, (x, y) in enumerate(self.snake_segments):
            is_head = (i == len(self.snake_segments) - 1)
            fill_color = head_color_hex if is_head else body_color_hex

            # Draw border rectangle (1 pixel larger on all sides)
            self.canvas.create_rectangle(
                x, y, x + SEGMENT_SIZE, y + SEGMENT_SIZE,
                fill=border_color_hex, outline=border_color_hex, tags="snake_border"
            )
            # Draw main segment rectangle (inset by 1 pixel for border effect)
            self.canvas.create_rectangle(
                x + 1, y + 1, x + SEGMENT_SIZE - 1, y + SEGMENT_SIZE - 1,
                fill=fill_color, outline=fill_color, tags="snake_segment"
            )

    def move_snake(self):
        # Update direction based on last valid key press
        self.direction = self.new_direction
        
        head_x, head_y = self.snake_segments[-1]

        if self.direction == "Up":
            new_head = (head_x, head_y - SEGMENT_SIZE)
        elif self.direction == "Down":
            new_head = (head_x, head_y + SEGMENT_SIZE)
        elif self.direction == "Left":
            new_head = (head_x - SEGMENT_SIZE, head_y)
        elif self.direction == "Right":
            new_head = (head_x + SEGMENT_SIZE, head_y)
        else: # Should not happen
            return

        final_head_pos = new_head

        if self.screen_wrapping_enabled:
            # Screen Wrapping Logic
            current_head_x, current_head_y = new_head
            wrapped_head_x, wrapped_head_y = current_head_x, current_head_y

            if current_head_x >= self.width:
                wrapped_head_x = 0
            elif current_head_x < 0:
                wrapped_head_x = self.width - SEGMENT_SIZE
            
            if current_head_y >= self.height:
                wrapped_head_y = 0
            elif current_head_y < 0:
                wrapped_head_y = self.height - SEGMENT_SIZE
                
            final_head_pos = (wrapped_head_x, wrapped_head_y)
        else:
            # Boundary Collision Logic (No Wrapping)
            current_head_x, current_head_y = new_head
            if not (0 <= current_head_x < self.width and 0 <= current_head_y < self.height):
                self.game_over_flag = True
                # Game over due to wall collision, no need to add segment or check food
                # The game_loop will pick up game_over_flag and display the screen.
                return 

        self.snake_segments.append(final_head_pos)

        # Check if snake ate food
        if final_head_pos == self.food_coords:
            self.score += 1
            self.master.title(f"Simple Snake Game - Score: {self.score}")
            self.create_food()
        else:
            self.snake_segments.pop(0) # Remove tail if no food eaten

    def check_collisions(self):
        head_x, head_y = self.snake_segments[-1]

        # Wall collision logic is now handled in move_snake if wrapping is off.
        # This method primarily checks for self-collision.

        # Self-collision (check if head is in the rest of the body)
        if (head_x, head_y) in self.snake_segments[:-1]:
            return True # Collision occurred

        return False # No collision

    def change_direction(self, new_dir):
        # Prevent 180-degree turns
        if new_dir == "Up" and self.direction != "Down":
            self.new_direction = new_dir
        elif new_dir == "Down" and self.direction != "Up":
            self.new_direction = new_dir
        elif new_dir == "Left" and self.direction != "Right":
            self.new_direction = new_dir
        elif new_dir == "Right" and self.direction != "Left":
            self.new_direction = new_dir

    def display_game_over(self):
        self.save_high_score() # Save score before displaying
        self.unbind_game_keys() # Prevent movement after game over

        self.canvas.create_text(
            self.width / 2, self.height / 2 - 60, # Adjusted y for more elements
            text="GAME OVER!",
            fill=GAME_OVER_TEXT_COLOR, font=("Arial", 24, "bold"), anchor="center"
        )
        self.canvas.create_text(
            self.width / 2, self.height / 2 - 20, # Adjusted y
            text=f"Final Score: {self.score}",
            fill=GAME_OVER_TEXT_COLOR, font=("Arial", 16), anchor="center"
        )
        self.canvas.create_text(
            self.width / 2, self.height / 2 + 20, # Display high score
            text=f"High Score: {self.high_score}",
            fill=GAME_OVER_TEXT_COLOR, font=("Arial", 16), anchor="center"
        )
        self.canvas.create_text(
            self.width / 2, self.height - 50, # Adjusted y for new instruction
            text="Press R to Return to Menu",
            fill=GAME_OVER_TEXT_COLOR, font=("Arial", 12), anchor="center"
        )
        # Bind R/r to return to menu
        self.master.bind("<KeyPress-r>", lambda event: self.handle_game_over_key())
        self.master.bind("<KeyPress-R>", lambda event: self.handle_game_over_key())

    def handle_game_over_key(self):
        # This function is called when R/r is pressed on game over screen
        self.master.unbind("<KeyPress-r>")
        self.master.unbind("<KeyPress-R>")
        self.show_menu() # Go back to the menu

    def restart_game_handler(self): # This method is now effectively handle_game_over_key
        # Kept for compatibility if referenced elsewhere, but should be deprecated
        # in favor of direct show_menu or specific handler like handle_game_over_key
        self.show_menu()

    def game_loop(self):
        if self.menu_active: # Don't run game logic if menu is active
            return

        if self.game_over_flag:
            self.display_game_over() # Show game over screen
            return # Stop game loop here

        self.move_snake()

        if self.check_collisions():
            self.game_over_flag = True
            # Call game_loop one last time to display game over message
            self.master.after(self.current_speed_ms, self.game_loop)
            return

        self.draw_game()
        self.master.after(self.current_speed_ms, self.game_loop)


    def bind_game_keys(self):
        self.master.bind("<KeyPress-w>", lambda event: self.change_direction("Up"))
        self.master.bind("<KeyPress-a>", lambda event: self.change_direction("Left"))
        self.master.bind("<KeyPress-s>", lambda event: self.change_direction("Down"))
        self.master.bind("<KeyPress-d>", lambda event: self.change_direction("Right"))
        self.master.bind("<Up>", lambda event: self.change_direction("Up"))
        self.master.bind("<Left>", lambda event: self.change_direction("Left"))
        self.master.bind("<Down>", lambda event: self.change_direction("Down"))
        self.master.bind("<Right>", lambda event: self.change_direction("Right"))
        # Note: 'R' for restart during game is not implemented here, only from game over.

    def unbind_game_keys(self):
        self.master.unbind("<KeyPress-w>")
        self.master.unbind("<KeyPress-a>")
        self.master.unbind("<KeyPress-s>")
        self.master.unbind("<KeyPress-d>")
        self.master.unbind("<Up>")
        self.master.unbind("<Left>")
        self.master.unbind("<Down>")
        self.master.unbind("<Right>")
        # Also unbind R from game over screen if it was bound
        self.master.unbind("<KeyPress-r>")
        self.master.unbind("<KeyPress-R>")


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root) # This will call __init__ which calls show_menu()
    root.mainloop()