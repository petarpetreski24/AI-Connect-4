import math
import random
import sys
import numpy as np
import time
import psutil


# Function to get current memory usage
def get_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss  # Get the Resident Set Size (RSS) in bytes


start_memory = get_memory_usage()
start_time = time.time()
# region Defining final variables

# Colors
BLUE = (0, 33, 66)
RED = (220, 20, 60)
GREEN = (155, 230, 25)
GRAY = (218, 211, 211)
WHITE = (255, 255, 255)
DARK_GRAY = (150, 150, 150)

# Players values (enums)
EMPTY = 0
AI1_PIECE = 1
AI2_PIECE = 2

# Board Specifications
ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARE_SIZE = 100
WIDTH = COLUMN_COUNT * SQUARE_SIZE
HEIGHT = (ROW_COUNT + 1) * SQUARE_SIZE
RADIUS = SQUARE_SIZE / 2 - 5
FREE_SPACES = ROW_COUNT * COLUMN_COUNT
WINDOW_LENGTH = 4


# endregion

# region Helping Functions


def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))


# noinspection PyShadowingNames
def is_valid_location(board, col):
    return board[0][col] == 0


# noinspection PyShadowingNames
def drop_circle(board, row, col, circle):
    board[row][col] = circle


# noinspection PyShadowingNames
def drop_circle_minimax(board, row, col, circle):
    board[row][col] = circle


# noinspection PyShadowingNames
def get_next_open_row(board, col):
    for i in range(ROW_COUNT - 1, -1, -1):
        if board[i][col] == 0:
            return i


# noinspection PyShadowingNames
def get_valid_locations(board):
    valid_locations = []
    for colum in range(COLUMN_COUNT):
        if is_valid_location(board, colum):
            valid_locations.append(colum)
    return valid_locations


# noinspection PyShadowingNames
def is_terminal_node(board):
    return check_possible_win(board, AI1_PIECE) or check_possible_win(board, AI2_PIECE) or FREE_SPACES == 0


def evaluate_window(window, piece):
    score = 0
    opp_piece = piece % 2 + 1

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


# noinspection PyShadowingNames
def check_possible_win(board, circle):
    # Horizontal Connect Four Win
    for i in range(ROW_COUNT):
        for j in range(COLUMN_COUNT - 3):
            if board[i][j] == circle and board[i][j + 1] == circle and board[i][j + 2] == circle and \
                    board[i][j + 3] == circle:
                return True

    # Vertical Connect Four Win
    for i in range(ROW_COUNT - 3):
        for j in range(COLUMN_COUNT):
            if board[i][j] == circle and board[i + 1][j] == circle and board[i + 2][j] == circle and \
                    board[i + 3][j] == circle:
                return True

    # Negative Diagonal Connect Four Win
    for i in range(ROW_COUNT - 3):
        for j in range(COLUMN_COUNT - 3):
            if board[i][j] == circle and board[i + 1][j + 1] == circle and board[i + 2][j + 2] == circle and \
                    board[i + 3][j + 3] == circle:
                return True

    # Positive Diagonal Connect Four Win
    for i in range(3, ROW_COUNT):
        for j in range(COLUMN_COUNT - 3):
            if board[i][j] == circle and board[i - 1][j + 1] == circle and board[i - 2][j + 2] == circle and \
                    board[i - 3][j + 3] == circle:
                return True
    return False


# noinspection PyShadowingNames
def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 2

    # Score Horizontal
    for row in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[row, :])]
        for column in range(COLUMN_COUNT - 3):
            window = row_array[column:column + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for column in range(COLUMN_COUNT):
        column_array = [int(i) for i in list(board[:, column])]
        for row in range(ROW_COUNT - 3):
            window = column_array[row:row + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score positive sloped diagonal
    for row in range(ROW_COUNT - 3):
        for column in range(COLUMN_COUNT - 3):
            window = [board[row + i][column + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for row in range(ROW_COUNT - 3):
        for column in range(COLUMN_COUNT - 3):
            window = [board[row + 3 - i][column + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


# endregion


# region ExpectiMax Function

# noinspection PyShadowingNames
def minimax_expectimax_AI1(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)

    if depth == 0 or is_terminal_node(board):  # Terminal conditions
        if is_terminal_node(board):
            if check_possible_win(board, AI1_PIECE):
                return None, sys.maxsize - 1
            elif check_possible_win(board, AI2_PIECE):
                return None, -sys.maxsize - 1
            else:  # Game is over
                return None, 0
        else:  # Depth is zero
            return None, score_position(board, AI1_PIECE)

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_minimax(b_copy, row, col, AI1_PIECE)
            new_score = minimax_expectimax_AI1(b_copy, depth - 1, alpha, beta, False)[1]

            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)

            if alpha >= beta:
                break

        return column, value
    else:  # Chance node (Expectimax)
        expected_value = 0
        num_possible_moves = 0

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_minimax(b_copy, row, col, AI2_PIECE)
            new_score = minimax_expectimax_AI1(b_copy, depth - 1, alpha, beta, True)[1]

            expected_value += new_score
            num_possible_moves += 1

        return None, expected_value / num_possible_moves


# noinspection PyShadowingNames
def minimax_expectimax_AI2(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)

    if depth == 0 or is_terminal_node(board):  # Terminal conditions
        if is_terminal_node(board):
            if check_possible_win(board, AI2_PIECE):
                return None, sys.maxsize - 1
            elif check_possible_win(board, AI1_PIECE):
                return None, -sys.maxsize - 1
            else:  # Game is over
                return None, 0
        else:  # Depth is zero
            return None, score_position(board, AI2_PIECE)

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_minimax(b_copy, row, col, AI2_PIECE)
            new_score = minimax_expectimax_AI2(b_copy, depth - 1, alpha, beta, False)[1]

            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)

            if alpha >= beta:
                break

        return column, value
    else:  # Chance node (Expectimax)
        expected_value = 0
        num_possible_moves = 0

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_minimax(b_copy, row, col, AI1_PIECE)
            new_score = minimax_expectimax_AI2(b_copy, depth - 1, alpha, beta, True)[1]

            expected_value += new_score
            num_possible_moves += 1

        return None, expected_value / num_possible_moves
# endregion

# region Starting the game


board = create_board()
game_over = False
sprints = 5
tries = 100
AI1Wins = 0
AI2Wins = 0
Draw = 0

AI_1_DEPTH = 2
AI_2_DEPTH = 3

turn = random.randint(AI1_PIECE, AI2_PIECE)
first_turn = None
sprint_starts = True
turn_starts = True

turns_1 = 0
turns_2 = 0

while sprints > 0:
    if sprint_starts:
        sprint_starts = False
        first_turn = turn

    if turn_starts:
        turn_starts=False
        if turn == AI1_PIECE:
            turns_1 += 1
        else:
            turns_2 += 1
    if turn == AI1_PIECE and not game_over:

        turn = AI2_PIECE
        col, minimax_score = minimax_expectimax_AI1(board, AI_1_DEPTH, -math.inf, math.inf, True)

        if col is not None and is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_circle(board, row, col, AI1_PIECE)
            FREE_SPACES -= 1

            if check_possible_win(board, AI1_PIECE):
                AI1Wins += 1
                game_over = True

    elif turn == AI2_PIECE and not game_over:

        turn = AI1_PIECE
        col, minimax_score = minimax_expectimax_AI2(board, AI_2_DEPTH, -math.inf, math.inf, True)

        if col is not None and is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_circle(board, row, col, AI2_PIECE)
            FREE_SPACES -= 1

            if check_possible_win(board, AI2_PIECE):
                AI2Wins += 1
                game_over = True

    if FREE_SPACES == 0 and not game_over:
        Draw += 1
        game_over = True

    if game_over:
        tries -= 1
        FREE_SPACES = ROW_COUNT * COLUMN_COUNT
        board = create_board()
        game_over = False
        turn = random.randint(AI1_PIECE, AI2_PIECE)
        turn_starts=True

    if tries == 0:
        print('#################################')
        print(f'Stats for sprint {11 - sprints}')
        print(f'Turn: {first_turn}')
        print(f'Number of AI1 turns: {turns_1}')
        print(f'Number of AI2 turns: {turns_2}')
        print(f'AI1: {AI1Wins}, AI2: {AI2Wins}, Draw: {Draw}')

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time: {elapsed_time:.2f} seconds")

        end_memory = get_memory_usage()
        memory_used = end_memory - start_memory
        memory_used_mb = memory_used / (1024 * 1024)
        print(f"Memory used: {memory_used_mb:.2f} MB")
        print('#################################')
        print('\n')

        start_time = time.time()

        sprints -= 1
        tries = 100
        AI1Wins = 0
        AI2Wins = 0
        Draw = 0
        turns_1 = 0
        turns_2 = 0
        sprint_starts = True

# endregion
