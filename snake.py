import tkinter as tk
import random

# Game Constants
# WIDTH = 500  # Removed
# HEIGHT = 500 # Removed
INITIAL_MAP_SIZE_N = 25 # Default number of segments for width and height
SEGMENT_SIZE = 20  # Size of each snake segment and food
GAME_SPEED = 150   # Milliseconds between game updates (lower is faster)

# Colors
BACKGROUND_COLOR = "black"
SNAKE_COLOR = "green"
FOOD_COLOR = "red"
GAME_OVER_TEXT_COLOR = "white"
HIGH_SCORE_FILE = "highscore.txt"

class SnakeGame:
    def __init__(self, master, map_size_n=INITIAL_MAP_SIZE_N): # map_size_n will be set by menu
        self.master = master
        # self.map_size_n, self.width, self.height will be set before game starts
        self.map_size_n = map_size_n # Default for now, will be updated by menu
        self.width = self.map_size_n * SEGMENT_SIZE
        self.height = self.map_size_n * SEGMENT_SIZE
        
        self.master.title("Simple Snake Game") 
        self.master.resizable(False, False)

        self.canvas = None # Will be created by show_menu / start_game_from_menu
        
        # Game state variables
        self.snake_segments = []
        self.food_coords = (0, 0)
        self.direction = "Right"
        self.new_direction = "Right"
        self.score = 0
        self.game_over_flag = False
        
        self.menu_active = True
        self.high_score = self.load_high_score()
        
        # Menu widgets
        self.map_size_entry = None
        self.start_button = None
        self.exit_button = None
        self.map_label = None
        self.title_text_id = None
        self.highscore_text_id = None
        self.map_label_window_id = None
        self.map_entry_window_id = None
        self.start_button_window_id = None
        self.exit_button_window_id = None

        # Key bindings are context-dependent (menu vs game)
        # Initial call to show menu
        self.show_menu() # __init__ ends by showing the menu

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
            self.width / 2, self.height / 2 - 120,
            text="Snake Game",
            fill=GAME_OVER_TEXT_COLOR, font=("Arial", 30, "bold"), anchor="center"
        )
        # High Score
        self.highscore_text_id = self.canvas.create_text(
            self.width / 2, self.height / 2 - 70,
            text=f"High Score: {self.high_score}",
            fill=GAME_OVER_TEXT_COLOR, font=("Arial", 16), anchor="center"
        )

        # Map Size Entry
        self.map_label = tk.Label(self.master, text="Map Size (10-50):", bg=BACKGROUND_COLOR, fg="white", font=("Arial", 10))
        self.map_size_entry = tk.Entry(self.master, font=("Arial", 10), width=5)
        self.map_size_entry.insert(0, str(INITIAL_MAP_SIZE_N))
        
        self.map_label_window_id = self.canvas.create_window(self.width / 2 - 60, self.height / 2 - 20, anchor="e", window=self.map_label)
        self.map_entry_window_id = self.canvas.create_window(self.width / 2 - 50, self.height / 2 - 20, anchor="w", window=self.map_size_entry)

        # Start Game Button
        self.start_button = tk.Button(self.master, text="Start Game", command=self.start_game_from_menu, font=("Arial", 14), bg="grey", fg="white")
        self.start_button_window_id = self.canvas.create_window(self.width / 2, self.height / 2 + 30, anchor="center", window=self.start_button)

        # Exit Button
        self.exit_button = tk.Button(self.master, text="Exit", command=self.master.destroy, font=("Arial", 14), bg="grey", fg="white")
        self.exit_button_window_id = self.canvas.create_window(self.width / 2, self.height / 2 + 80, anchor="center", window=self.exit_button)
        
        self.canvas.focus_set() # For any potential menu key bindings, though not used yet

    def clear_menu_widgets(self):
        # Destroy Tkinter widgets
        if self.map_label: self.map_label.destroy()
        if self.map_size_entry: self.map_size_entry.destroy()
        if self.start_button: self.start_button.destroy()
        if self.exit_button: self.exit_button.destroy()
        
        # Nullify references
        self.map_label = self.map_size_entry = self.start_button = self.exit_button = None
        
        # Canvas items created with create_text, create_window are cleared by canvas.delete(ALL)
        # but if we stored their IDs, we could delete them individually too.
        # For now, relying on canvas.delete(ALL) before drawing game or new menu.

    def start_game_from_menu(self):
        try:
            n = int(self.map_size_entry.get())
            if not (10 <= n <= 50):
                print(f"Invalid map size: {n}. Must be between 10 and 50. Using default {INITIAL_MAP_SIZE_N}.")
                n = INITIAL_MAP_SIZE_N
        except ValueError:
            print(f"Invalid map size input. Using default {INITIAL_MAP_SIZE_N}.")
            n = INITIAL_MAP_SIZE_N
        
        self.map_size_n = n
        self.width = self.map_size_n * SEGMENT_SIZE
        self.height = self.map_size_n * SEGMENT_SIZE
        
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

    def draw_game(self):
        self.canvas.delete(tk.ALL) # Clear previous frame

        # Draw food
        self.canvas.create_rectangle(
            self.food_coords[0], self.food_coords[1],
            self.food_coords[0] + SEGMENT_SIZE, self.food_coords[1] + SEGMENT_SIZE,
            fill=FOOD_COLOR, outline=FOOD_COLOR, tags="food"
        )

        # Draw snake
        for x, y in self.snake_segments:
            self.canvas.create_rectangle(
                x, y, x + SEGMENT_SIZE, y + SEGMENT_SIZE,
                fill=SNAKE_COLOR, outline=SNAKE_COLOR, tags="snake"
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
            
        wrapped_new_head = (wrapped_head_x, wrapped_head_y)

        self.snake_segments.append(wrapped_new_head)

        # Check if snake ate food
        if wrapped_new_head == self.food_coords:
            self.score += 1
            self.master.title(f"Simple Snake Game - Score: {self.score}")
            self.create_food()
        else:
            self.snake_segments.pop(0) # Remove tail if no food eaten

    def check_collisions(self):
        head_x, head_y = self.snake_segments[-1]

        # Wall collision logic is removed for screen wrapping

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
            self.master.after(GAME_SPEED, self.game_loop)
            return

        self.draw_game()
        self.master.after(GAME_SPEED, self.game_loop)


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