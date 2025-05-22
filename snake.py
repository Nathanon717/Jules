import tkinter as tk
import random

# Game Constants
WIDTH = 500
HEIGHT = 500
SEGMENT_SIZE = 20  # Size of each snake segment and food
GAME_SPEED = 150   # Milliseconds between game updates (lower is faster)

# Colors
BACKGROUND_COLOR = "black"
SNAKE_COLOR = "green"
FOOD_COLOR = "red"
GAME_OVER_TEXT_COLOR = "white"

class SnakeGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Simple Snake Game - Score: 0")
        self.master.resizable(False, False) # Prevent window resizing

        self.canvas = tk.Canvas(self.master, width=WIDTH, height=HEIGHT, bg=BACKGROUND_COLOR)
        self.canvas.pack()

        # Center window
        self.center_window()

        # Game state variables
        self.snake_segments = []
        self.food_coords = (0, 0)
        self.direction = "Right" # Initial direction
        self.new_direction = "Right" # To handle rapid key presses
        self.score = 0
        self.game_over_flag = False

        # Bind keyboard controls
        self.master.bind("<KeyPress-w>", lambda event: self.change_direction("Up"))
        self.master.bind("<KeyPress-a>", lambda event: self.change_direction("Left"))
        self.master.bind("<KeyPress-s>", lambda event: self.change_direction("Down"))
        self.master.bind("<KeyPress-d>", lambda event: self.change_direction("Right"))
        # Allow arrow keys too for convenience
        self.master.bind("<Up>", lambda event: self.change_direction("Up"))
        self.master.bind("<Left>", lambda event: self.change_direction("Left"))
        self.master.bind("<Down>", lambda event: self.change_direction("Down"))
        self.master.bind("<Right>", lambda event: self.change_direction("Right"))


        self.start_game()

    def center_window(self):
        """Centers the game window on the screen."""
        self.master.update_idletasks() # Ensure dimensions are calculated
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (WIDTH / 2))
        y_coordinate = int((screen_height / 2) - (HEIGHT / 2))
        self.master.geometry(f"{WIDTH}x{HEIGHT}+{x_coordinate}+{y_coordinate}")


    def start_game(self):
        self.game_over_flag = False
        self.score = 0
        self.master.title(f"Simple Snake Game - Score: {self.score}")
        self.direction = "Right"
        self.new_direction = "Right"

        # Initial snake (3 segments in the middle)
        self.snake_segments = [
            (WIDTH // 2 - 2 * SEGMENT_SIZE, HEIGHT // 2),
            (WIDTH // 2 - SEGMENT_SIZE, HEIGHT // 2),
            (WIDTH // 2, HEIGHT // 2)
        ]
        self.create_food()
        self.game_loop()

    def create_food(self):
        """Places food randomly on the canvas, not on the snake."""
        while True:
            x = random.randrange(0, WIDTH // SEGMENT_SIZE) * SEGMENT_SIZE
            y = random.randrange(0, HEIGHT // SEGMENT_SIZE) * SEGMENT_SIZE
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

        self.snake_segments.append(new_head)

        # Check if snake ate food
        if new_head == self.food_coords:
            self.score += 1
            self.master.title(f"Simple Snake Game - Score: {self.score}")
            self.create_food()
        else:
            self.snake_segments.pop(0) # Remove tail if no food eaten

    def check_collisions(self):
        head_x, head_y = self.snake_segments[-1]

        # Wall collision
        if not (0 <= head_x < WIDTH and 0 <= head_y < HEIGHT):
            return True # Collision occurred

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
        self.canvas.create_text(
            WIDTH / 2, HEIGHT / 2 - 20,
            text=f"GAME OVER!",
            fill=GAME_OVER_TEXT_COLOR, font=("Arial", 24, "bold"), anchor="center"
        )
        self.canvas.create_text(
            WIDTH / 2, HEIGHT / 2 + 20,
            text=f"Final Score: {self.score}",
            fill=GAME_OVER_TEXT_COLOR, font=("Arial", 16), anchor="center"
        )
        self.canvas.create_text(
            WIDTH / 2, HEIGHT - 30,
            text="Close window to exit or press R to Restart",
            fill=GAME_OVER_TEXT_COLOR, font=("Arial", 10), anchor="center"
        )
        self.master.bind("<KeyPress-r>", lambda event: self.restart_game_handler())
        self.master.bind("<KeyPress-R>", lambda event: self.restart_game_handler())


    def restart_game_handler(self):
        if self.game_over_flag: # Only allow restart if game is over
            self.master.unbind("<KeyPress-r>") # Unbind to prevent multiple restarts
            self.master.unbind("<KeyPress-R>")
            self.start_game()

    def game_loop(self):
        if self.game_over_flag:
            self.display_game_over()
            return

        self.move_snake()

        if self.check_collisions():
            self.game_over_flag = True
            # Call game_loop one last time to display game over message
            self.master.after(GAME_SPEED, self.game_loop)
            return

        self.draw_game()
        self.master.after(GAME_SPEED, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()