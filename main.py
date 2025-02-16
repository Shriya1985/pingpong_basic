import random
import tkinter as tk

# Initialize the main window
root = tk.Tk()
root.title("Pong Game with AI")

# Game dimensions
WIDTH = 800
HEIGHT = 400
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_SIZE = 20
SCORE_FONT = ("Helvetica", 20)

# Initialize canvas
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()

# Global variables for game elements
left_paddle = None
right_paddle = None
ball = None
score_display = None

# Game state
left_score = 0
right_score = 0
ball_dx = 4
ball_dy = 4
left_paddle_dy = 0
right_paddle_dy = 0
is_single_player = True  # Default mode

# AI speed
AI_SPEED = 6

power_up = None
power_up_active = False
power_up_effects = {
    "paddle_size": "Increase Paddle Size",
    "ball_slow": "Slow Ball",
    "score_boost": "Score Boost"
}
active_power_up = None  # Currently active power-up
power_up_timer = 0  # Timer for power-up duration
POWER_UP_DURATION = 5000  # Duration of power-up in milliseconds (5 seconds)


# Function to reset the ball
def reset_ball():
    global ball_dx, ball_dy
    canvas.coords(ball, WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2,
                  WIDTH // 2 + BALL_SIZE // 2, HEIGHT // 2 + BALL_SIZE // 2)
    ball_dx = -ball_dx  # Change direction


# Function to move paddles
def move_paddles():
    global left_paddle_dy, right_paddle_dy

    # Move left paddle
    canvas.move(left_paddle, 0, left_paddle_dy)
    left_coords = canvas.coords(left_paddle)
    if left_coords[1] < 0:
        canvas.move(left_paddle, 0, -left_coords[1])
    elif left_coords[3] > HEIGHT:
        canvas.move(left_paddle, 0, HEIGHT - left_coords[3])

    # Move right paddle
    if is_single_player:
        move_ai()
    else:
        canvas.move(right_paddle, 0, right_paddle_dy)
        right_coords = canvas.coords(right_paddle)
        if right_coords[1] < 0:
            canvas.move(right_paddle, 0, -right_coords[1])
        elif right_coords[3] > HEIGHT:
            canvas.move(right_paddle, 0, HEIGHT - right_coords[3])


# Function to control the AI paddle
def move_ai():
    ball_coords = canvas.coords(ball)
    paddle_coords = canvas.coords(right_paddle)
    paddle_center = (paddle_coords[1] + paddle_coords[3]) / 2

    if ball_coords[1] < paddle_center:
        canvas.move(right_paddle, 0, -AI_SPEED)
    elif ball_coords[3] > paddle_center:
        canvas.move(right_paddle, 0, AI_SPEED)


def spawn_power_up():
    global power_up
    if power_up is not None:  # If a power-up already exists, do nothing
        return

    power_up_type = random.choice(list(power_up_effects.keys()))  # Randomly select a power-up type
    x = random.randint(WIDTH // 4, (3 * WIDTH) // 4)  # Random x position
    y = random.randint(HEIGHT // 4, (3 * HEIGHT) // 4)  # Random y position

    power_up = canvas.create_oval(x, y, x + 20, y + 20, fill="yellow", tags=power_up_type)
    root.after(random.randint(10000, 20000), spawn_power_up)  # Spawn power-ups periodically


# Function to apply a power-up effect
def apply_power_up(power_up_type):
    global active_power_up, power_up_timer, ball_dx, ball_dy

    if power_up_type == "paddle_size":
        canvas.scale(left_paddle, 0, 0, 1, 1.5)  # Increase paddle height
        canvas.scale(right_paddle, 0, 0, 1, 1.5)
    elif power_up_type == "ball_slow":
        ball_dx /= 2
        ball_dy /= 2
    elif power_up_type == "score_boost":
        global left_score, right_score
        left_score += 1
        right_score += 1

    active_power_up = power_up_type
    power_up_timer = POWER_UP_DURATION
    canvas.delete(power_up)
    power_up = None


# Function to deactivate a power-up
def deactivate_power_up():
    global active_power_up, ball_dx, ball_dy
    if active_power_up == "paddle_size":
        canvas.scale(left_paddle, 0, 0, 1, 2 / 3)  # Reset paddle size
        canvas.scale(right_paddle, 0, 0, 1, 2 / 3)
    elif active_power_up == "ball_slow":
        ball_dx *= 2
        ball_dy *= 2

    active_power_up = None


# Update move_ball function to include power-up collision detection
def move_ball():
    global ball_dx, ball_dy, left_score, right_score, power_up_timer, active_power_up
    canvas.move(ball, ball_dx, ball_dy)
    ball_coords = canvas.coords(ball)

    # Ball collision with walls
    if ball_coords[1] <= 0 or ball_coords[3] >= HEIGHT:
        ball_dy = -ball_dy

    # Ball collision with paddles
    if ball_coords[0] <= canvas.coords(left_paddle)[2] and \
            canvas.coords(left_paddle)[1] < ball_coords[3] and \
            canvas.coords(left_paddle)[3] > ball_coords[1]:
        ball_dx = -ball_dx * 1.1
        ball_dy = ball_dy * 1.1
        limit_ball_speed()

    if ball_coords[2] >= canvas.coords(right_paddle)[0] and \
            canvas.coords(right_paddle)[1] < ball_coords[3] and \
            canvas.coords(right_paddle)[3] > ball_coords[1]:
        ball_dx = -ball_dx * 1.1
        ball_dy = ball_dy * 1.1
        limit_ball_speed()

    # Ball out of bounds
    if ball_coords[0] <= 0:
        right_score += 1
        reset_ball()
    elif ball_coords[2] >= WIDTH:
        left_score += 1
        reset_ball()

    # Check for collision with power-up
    if power_up and canvas.bbox(ball) and canvas.bbox(power_up):
        power_up_type = canvas.gettags(power_up)[0]
        apply_power_up(power_up_type)

    # Update power-up timer
    if active_power_up:
        power_up_timer -= 20  # Decrease timer
        if power_up_timer <= 0:
            deactivate_power_up()

    # Update score display
    canvas.itemconfig(score_display, text=f"{left_score} : {right_score}")


# Function to limit the ball's speed
def limit_ball_speed():
    global ball_dx, ball_dy
    max_speed = 10  # Define a maximum speed
    ball_dx = max(-max_speed, min(max_speed, ball_dx))  # Clamp ball_dx to [-max_speed, max_speed]
    ball_dy = max(-max_speed, min(max_speed, ball_dy))  # Clamp ball_dy to [-max_speed, max_speed]



# Function to handle key presses
def on_key_press(event):
    global left_paddle_dy, right_paddle_dy
    if event.keysym == "w":
        left_paddle_dy = -8
    elif event.keysym == "s":
        left_paddle_dy = 8
    elif not is_single_player:
        if event.keysym == "Up":
            right_paddle_dy = -8
        elif event.keysym == "Down":
            right_paddle_dy = 8


# Function to handle key releases
def on_key_release(event):
    global left_paddle_dy, right_paddle_dy
    if event.keysym in ("w", "s"):
        left_paddle_dy = 0
    elif event.keysym in ("Up", "Down"):
        right_paddle_dy = 0


# Updated function to check for game over
def check_game_over():
    if left_score >= 3:
        canvas.create_text(WIDTH // 2, HEIGHT // 2 - 30, text="Left Player Wins!", fill="white", font=SCORE_FONT)
        show_end_screen()
    elif right_score >= 3:
        canvas.create_text(WIDTH // 2, HEIGHT // 2 - 30, text="Right Player Wins!", fill="white", font=SCORE_FONT)
        show_end_screen()


# Function to display the end screen with Retry and Main Menu buttons
def show_end_screen():
    # Disable paddle and ball movements
    root.unbind("<KeyPress>")
    root.unbind("<KeyRelease>")

    # Create Retry button
    retry_button = tk.Button(root, text="Retry", font=("Helvetica", 14), bg="black", fg="white",
                             command=lambda: retry_game(retry_button, main_menu_button))
    retry_button.place(x=WIDTH // 2 - 120, y=HEIGHT // 2, width=100, height=40)

    # Create Main Menu button
    main_menu_button = tk.Button(root, text="Main Menu", font=("Helvetica", 14), bg="black", fg="white",
                                 command=lambda: go_to_start_screen(retry_button, main_menu_button))
    main_menu_button.place(x=WIDTH // 2 + 20, y=HEIGHT // 2, width=100, height=40)


# Function to restart the game and remove the Retry and Main Menu buttons
def retry_game(retry_button, main_menu_button):
    retry_button.destroy()  # Remove Retry button
    main_menu_button.destroy()  # Remove Main Menu button
    initialize_game(is_single_player)  # Restart the game in the current mode


# Function to go back to the start screen and remove the Retry and Main Menu buttons
def go_to_start_screen(retry_button, main_menu_button):
    retry_button.destroy()  # Remove Retry button
    main_menu_button.destroy()  # Remove Main Menu button
    start_screen()


def bind_keys():
    # Bind keys for paddle movement
    root.bind("<KeyPress>", on_key_press)
    root.bind("<KeyRelease>", on_key_release)


# Start screen with buttons
def start_screen():
    global button_frame  # To keep track of the frame and buttons for removal later

    canvas.delete("all")  # Clear any existing canvas content
    canvas.create_text(WIDTH // 2, HEIGHT // 4, text="Pong Game", fill="white", font=("Helvetica", 30))

    # Create a frame for the buttons
    button_frame = tk.Frame(root, bg="black")
    button_frame.place(relx=0.5, rely=0.6, anchor="center")  # Adjust the position of the buttons

    # Single Player Button
    single_player_button = tk.Button(
        button_frame,
        text="Single Player",
        font=SCORE_FONT,
        bg="white",
        fg="black",
        width=15,
        command=lambda: initialize_game(True)
    )
    single_player_button.pack(pady=10)

    # Multiplayer Button
    multiplayer_button = tk.Button(
        button_frame,
        text="Multiplayer",
        font=SCORE_FONT,
        bg="white",
        fg="black",
        width=15,
        command=lambda: initialize_game(False)
    )
    multiplayer_button.pack(pady=10)

    # Exit Button
    exit_button = tk.Button(
        button_frame,
        text="Exit",
        font=SCORE_FONT,
        bg="white",
        fg="black",
        width=15,
        command=root.quit  # Exit the application
    )
    exit_button.pack(pady=10)


# Modify the initialize_game function to start spawning power-ups
def initialize_game(single_player_mode):
    global left_score, right_score, ball_dx, ball_dy, is_single_player, power_up, active_power_up, power_up_timer

    is_single_player = single_player_mode
    left_score = 0
    right_score = 0
    ball_dx = 4
    ball_dy = 4
    power_up = None
    active_power_up = None
    power_up_timer = 0

    canvas.delete("all")  # Clear the canvas
    create_game_elements()  # Create paddles, ball, and score display
    bind_keys()  # Bind keys for movement
    spawn_power_up()  # Start spawning power-ups
    game_loop()


# Main game loop
def game_loop():
    move_paddles()
    move_ball()
    check_game_over()
    root.after(20, game_loop)


# Create paddles, ball, and score display
def create_game_elements():
    global left_paddle, right_paddle, ball, score_display
    left_paddle = canvas.create_rectangle(50, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                                          50 + PADDLE_WIDTH, HEIGHT // 2 + PADDLE_HEIGHT // 2, fill="white")
    right_paddle = canvas.create_rectangle(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                                           WIDTH - 50, HEIGHT // 2 + PADDLE_HEIGHT // 2, fill="white")
    ball = canvas.create_oval(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2,
                               WIDTH // 2 + BALL_SIZE // 2, HEIGHT // 2 + BALL_SIZE // 2, fill="white")
    score_display = canvas.create_text(WIDTH // 2, 30, text="0 : 0", fill="white", font=SCORE_FONT)



# Bind keys
root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)

# Start the game
start_screen()
root.mainloop()
