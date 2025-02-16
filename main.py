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


# Function to move the ball
def move_ball():
    global ball_dx, ball_dy, left_score, right_score
    canvas.move(ball, ball_dx, ball_dy)
    ball_coords = canvas.coords(ball)

    # Ball collision with walls
    if ball_coords[1] <= 0 or ball_coords[3] >= HEIGHT:
        ball_dy = -ball_dy

    # Ball collision with paddles
    if ball_coords[0] <= canvas.coords(left_paddle)[2] and \
            canvas.coords(left_paddle)[1] < ball_coords[3] and \
            canvas.coords(left_paddle)[3] > ball_coords[1]:
        ball_dx = -ball_dx

    if ball_coords[2] >= canvas.coords(right_paddle)[0] and \
            canvas.coords(right_paddle)[1] < ball_coords[3] and \
            canvas.coords(right_paddle)[3] > ball_coords[1]:
        ball_dx = -ball_dx

    # Ball out of bounds
    if ball_coords[0] <= 0:
        right_score += 1
        reset_ball()
    elif ball_coords[2] >= WIDTH:
        left_score += 1
        reset_ball()

    # Update score
    canvas.itemconfig(score_display, text=f"{left_score} : {right_score}")


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


# Initialize game elements
def initialize_game(single_player):
    global left_paddle, right_paddle, ball, score_display, left_score, right_score, is_single_player, button_frame
    is_single_player = single_player
    left_score = 0
    right_score = 0

    # Destroy the button frame to remove buttons from the screen
    if 'button_frame' in globals() and button_frame:
        button_frame.destroy()

    canvas.delete("all")
    left_paddle = canvas.create_rectangle(20, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                                           20 + PADDLE_WIDTH, HEIGHT // 2 + PADDLE_HEIGHT // 2, fill="white")
    right_paddle = canvas.create_rectangle(WIDTH - 20 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                                            WIDTH - 20, HEIGHT // 2 + PADDLE_HEIGHT // 2, fill="white")
    ball = canvas.create_oval(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2,
                               WIDTH // 2 + BALL_SIZE // 2, HEIGHT // 2 + BALL_SIZE // 2, fill="white")
    score_display = canvas.create_text(WIDTH // 2, 20, text="0 : 0", fill="white", font=SCORE_FONT)
    bind_keys()  # Ensure paddle movement keys are bound
    game_loop()

# Main game loop
def game_loop():
    move_paddles()
    move_ball()
    check_game_over()
    if left_score < 3 and right_score < 3:
        root.after(16, game_loop)


# Bind keys
root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)

# Start the game
start_screen()
root.mainloop()
