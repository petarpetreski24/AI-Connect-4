import math
import random
import sys
import time

import numpy as np
import pygame

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
HUMAN_PIECE = 1
AI_PIECE = 2

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

# noinspection PyShadowingNames
def get_difficulty_input(screen):
    input_rect = pygame.Rect(150, 360, 400, 40)
    input_text = ""
    input_active = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

        screen.fill(WHITE)
        intro_text = FONT_TITLE.render("Choose your", True, DARK_GRAY)
        screen.blit(intro_text, (150, 100))
        intro_text = FONT_TITLE.render("difficulty:", True, DARK_GRAY)
        screen.blit(intro_text, (220, 180))
        intro_text = FONT_TITLE.render("easy, medium or hard!", True, DARK_GRAY)
        screen.blit(intro_text, (15, 260))

        pygame.draw.rect(screen, BLUE, input_rect, 2)
        text_surface = FONT_INPUT.render(input_text, True, BLUE)
        screen.blit(text_surface, (input_rect.x + 160, input_rect.y + 3))

        if not input_active:
            pygame.display.update()
            if input_text == "easy":
                return 1
            elif input_text == "medium":
                return 3
            elif input_text == "hard":
                return 5
            input_active = True
        pygame.display.update()


def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))


# noinspection PyShadowingNames
def is_valid_location(board, col):
    return board[0][col] == 0


# noinspection PyShadowingNames
def drop_circle(board, row, col, circle):
    board[row][col] = circle
    if circle == HUMAN_PIECE:
        pygame.draw.circle(SCREEN, RED,
                           (col * SQUARE_SIZE + SQUARE_SIZE / 2, row * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2),
                           RADIUS)
    else:
        pygame.draw.circle(SCREEN, GREEN,
                           (col * SQUARE_SIZE + SQUARE_SIZE / 2, row * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2),
                           RADIUS)
    pygame.display.update()


# noinspection PyShadowingNames
def drop_circle_abstract(board, row, col, circle):
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
    return check_possible_win(board, HUMAN_PIECE) or check_possible_win(board, AI_PIECE) or FREE_SPACES == 0


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
def check_possible_win(board, player):
    # Horizontal Connect Four Win
    for i in range(ROW_COUNT):
        for j in range(COLUMN_COUNT - 3):
            if board[i][j] == player and board[i][j + 1] == player and board[i][j + 2] == player and \
                    board[i][j + 3] == player:
                return True

    # Vertical Connect Four Win
    for i in range(ROW_COUNT - 3):
        for j in range(COLUMN_COUNT):
            if board[i][j] == player and board[i + 1][j] == player and board[i + 2][j] == player and \
                    board[i + 3][j] == player:
                return True

    # Negative Diagonal Connect Four Win
    for i in range(ROW_COUNT - 3):
        for j in range(COLUMN_COUNT - 3):
            if board[i][j] == player and board[i + 1][j + 1] == player and board[i + 2][j + 2] == player and \
                    board[i + 3][j + 3] == player:
                return True

    # Positive Diagonal Connect Four Win
    for i in range(3, ROW_COUNT):
        for j in range(COLUMN_COUNT - 3):
            if board[i][j] == player and board[i - 1][j + 1] == player and board[i - 2][j + 2] == player and \
                    board[i - 3][j + 3] == player:
                return True
    return False


# noinspection PyShadowingNames
def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

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


# region MiniMax Function

# noinspection PyShadowingNames
def miniMaxWithABP(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    if depth == 0 or is_terminal_node(board):  # Terminal conditions
        if is_terminal_node(board):
            if check_possible_win(board, AI_PIECE):
                return None, sys.maxsize - 1
            elif check_possible_win(board, HUMAN_PIECE):
                return None, -sys.maxsize - 1
            else:  # Game is over
                return None, 0
        else:  # depth is zero
            return None, score_position(board, AI_PIECE)
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_abstract(b_copy, row, col, AI_PIECE)
            new_score = miniMaxWithABP(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_abstract(b_copy, row, col, HUMAN_PIECE)
            new_score = miniMaxWithABP(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def miniMax(board, depth, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    if depth == 0 or is_terminal_node(board):  # Terminal conditions
        if is_terminal_node(board):
            if check_possible_win(board, AI_PIECE):
                return None, sys.maxsize - 1
            elif check_possible_win(board, HUMAN_PIECE):
                return None, -sys.maxsize - 1
            else:  # Game is over
                return None, 0
        else:  # depth is zero
            return None, score_position(board, AI_PIECE)
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_abstract(b_copy, row, col, AI_PIECE)
            new_score = miniMax(b_copy, depth - 1, False)[1]
            if new_score > value:
                value = new_score
                column = col
        return column, value
    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_abstract(b_copy, row, col, HUMAN_PIECE)
            new_score = miniMax(b_copy, depth - 1, True)[1]
            if new_score < value:
                value = new_score
                column = col
        return column, value


# noinspection PyShadowingNames
def expectiMaxWithABP(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)

    if depth == 0 or is_terminal_node(board):  # Terminal conditions
        if is_terminal_node(board):
            if check_possible_win(board, AI_PIECE):
                return None, sys.maxsize - 1
            elif check_possible_win(board, HUMAN_PIECE):
                return None, -sys.maxsize - 1
            else:  # Game is over
                return None, 0
        else:  # Depth is zero
            return None, score_position(board, AI_PIECE)

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_abstract(b_copy, row, col, AI_PIECE)
            new_score = expectiMaxWithABP(b_copy, depth - 1, alpha, beta, False)[1]

            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)

            if alpha >= beta:
                break

        return column, value
    else:
        expected_value = 0
        num_possible_moves = 0

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_abstract(b_copy, row, col, HUMAN_PIECE)
            new_score = expectiMaxWithABP(b_copy, depth - 1, alpha, beta, True)[1]

            expected_value += new_score
            num_possible_moves += 1

        return None, expected_value / num_possible_moves

def expectimax(board, depth, maximizingPlayer):
    valid_locations = get_valid_locations(board)

    if depth == 0 or is_terminal_node(board):  # Terminal conditions
        if is_terminal_node(board):
            if check_possible_win(board, AI_PIECE):
                return None, sys.maxsize - 1
            elif check_possible_win(board, HUMAN_PIECE):
                return None, -sys.maxsize - 1
            else:  # Game is over
                return None, 0
        else:  # Depth is zero
            return None, score_position(board, AI_PIECE)

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_abstract(b_copy, row, col, AI_PIECE)
            new_score = expectimax(b_copy, depth - 1, False)[1]

            if new_score > value:
                value = new_score
                column = col

        return column, value
    else:
        expected_value = 0
        num_possible_moves = 0

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_circle_abstract(b_copy, row, col, HUMAN_PIECE)
            new_score = expectimax(b_copy, depth - 1, True)[1]

            expected_value += new_score
            num_possible_moves += 1

        return None, expected_value / num_possible_moves


# endregion

# region Board Initialization

# noinspection PyShadowingNames
def draw_board():
    for i in range(COLUMN_COUNT):
        for j in range(ROW_COUNT):
            pygame.draw.rect(SCREEN, BLUE,
                             (i * SQUARE_SIZE, j * SQUARE_SIZE + SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(SCREEN, GRAY,
                               (i * SQUARE_SIZE + SQUARE_SIZE / 2, j * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2),
                               RADIUS)
            pygame.display.update()


# endregion

# region Starting the game


board = create_board()
game_over = False

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
FONT = pygame.font.SysFont("comicsansms", 75)
FONT_INPUT = pygame.font.SysFont("verdana", 26)
FONT_TITLE = pygame.font.SysFont("verdana", 60)
DIFFICULTY = get_difficulty_input(SCREEN)

pygame.display.set_caption("AI Connect Four")

draw_board()
pygame.draw.rect(SCREEN, GRAY, (0, 0, WIDTH, SQUARE_SIZE))
pygame.display.update()

turn = random.randint(HUMAN_PIECE, AI_PIECE)

if turn == AI_PIECE and DIFFICULTY != 6:
    pygame.time.wait(1000)

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(SCREEN, GRAY, (0, 0, WIDTH, SQUARE_SIZE))
            if turn == HUMAN_PIECE:
                pygame.draw.circle(SCREEN, RED,
                                   (event.pos[0], SQUARE_SIZE / 2),
                                   RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(SCREEN, GRAY, (0, 0, WIDTH, SQUARE_SIZE))
            col = int(math.floor(event.pos[0] / SQUARE_SIZE))

            if COLUMN_COUNT <= col < 0 or 0 != board[0][col]:
                error_column_text = FONT_TITLE.render("Click on a free column!", True, DARK_GRAY)
                SCREEN.blit(error_column_text, (10, 5))
                continue

            # Player 1
            if turn == HUMAN_PIECE:
                turn = AI_PIECE
                pos_x = event.pos[0]
                col = int(math.floor(pos_x / SQUARE_SIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_circle(board, row, col, HUMAN_PIECE)
                    FREE_SPACES -= 1

                    if check_possible_win(board, HUMAN_PIECE):
                        pygame.draw.rect(SCREEN, GRAY, (0, 0, WIDTH, SQUARE_SIZE))
                        SCREEN.blit(FONT.render("You won!!!", 1, RED), (185, 0))
                        pygame.display.update()
                        game_over = True

                    if FREE_SPACES == 0:
                        game_over = True
                        SCREEN.blit(FONT.render("Draw!", 1, BLUE), (230, 5))
                        pygame.display.update()

    if turn == AI_PIECE and not game_over:

        turn = HUMAN_PIECE
        start_time = time.time()
        col, minimax_score = expectimax(board, 7, True)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time: {elapsed_time:.6f} seconds")

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_circle(board, row, col, AI_PIECE)
            FREE_SPACES -= 1

            if check_possible_win(board, AI_PIECE):
                pygame.draw.rect(SCREEN, GRAY, (0, 0, WIDTH, SQUARE_SIZE))
                SCREEN.blit(FONT.render("AI won!", 1, GREEN), (245, 5))
                pygame.display.update()
                game_over = True

    if FREE_SPACES == 0:
        game_over = True
        SCREEN.blit(FONT.render("Draw!", 1, BLUE), (245, 5))
        pygame.display.update()

pygame.time.wait(4000)
# endregion
