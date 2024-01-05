# -*- coding: utf-8 -*-
from subprocess import call
from time import sleep
import sys
from game import Game
from test_helpers import heuristic_gen, get_successors
from node import Node
import heuristics
import zobrist
import time
import json
import os


# open JSON file to read cached oves
with open("./moves_cache.json", "r") as f:
    try:
        cache_moves = json.load(f)
        # if the file is empty the ValueError will be thrown
    except ValueError:
        cache_moves = {"even": {}, "odd": {}}

even_moves = cache_moves["even"]
odd_moves = cache_moves["odd"]

# Magenta = '\033[95m'
# Blue = '\033[94m'
# Green = '\033[92m'
# Yellow = '\033[93m'
# Red = '\033[91m'
# Clear = '\033[0m'
# Bold = '\033[1m'
# Underline = '\033[4m'


class Game_Engine:
    def __init__(self, board_state):
        self.game = Game(board_state)
        self.computer = AI(self.game)

    def prompt_user(self):
        print(
            "\033[94m\033[1m==================================================================="
        )
        print(
            "\033[93m               ______________                     \n"
            "               __  ____/__  /_____________________\n"
            "               _  /    __  __ \  _ \_  ___/_  ___/\n"
            "               / /___  _  / / /  __/(__  )_(__  ) \n"
            "               \____/  /_/ /_/\___//____/ /____/  \n"
            "                                                  "
        )
        print(
            "\033[94m===================================================================\033[0m\033[22m"
        )
        load_input = input("Want to continue a previous game? y/n")

        save = ""
        while load_input.lower() != "n":
            if load_input != "y":
                load_input = input("Please insert either y or n")
            else:
                save = self.getSave()
                self.game.set_fen(save)
                break
        print(
            "\nWelcome! To play, enter a command, e.g. '\033[95me2e4\033[0m'. To quit, type '\033[91mff\033[0m'. To save the game type '\033[91msave\033[0m'"
        )
        self.computer.print_board(str(self.game))
        try:
            while self.game.status < 2:
                user_move = input("\nMake a move: \033[95m")
                print("\033[0m")
                while (
                    user_move not in self.game.get_moves()
                    and user_move != "ff"
                    and user_move != "save"
                ):
                    user_move = input("Please enter a valid move: ")
                if user_move == "ff":
                    print("You surrendered.")
                    break
                elif user_move == "save":
                    while True:
                        # Get user input for file name
                        file_name = input(
                            "Enter the name of the file (or type 'cancel' to cancel): "
                        )

                        # Check if the user wants to cancel
                        if file_name.lower() == "cancel":
                            print("Operation canceled. Continue with the game.")
                            break

                        # Check if the file name is empty or contains special characters
                        if not file_name or any(
                            char in file_name for char in '/\:*?"<>|'
                        ):
                            print(
                                "Invalid file name. Please enter a valid name without special characters."
                            )
                            continue

                        # Get user input for game state
                        game_state = str(self.game)

                        # Save the game state to the file
                        self.save_game_state(file_name, game_state)
                        break
                    break

                self.game.apply_move(user_move)
                captured = self.captured_pieces(str(self.game))
                start_time = time.time()
                self.computer.print_board(str(self.game), captured)
                print("\nCalculating...\n")
                if self.game.status < 2:
                    current_state = str(self.game)
                    computer_move = self.computer.greedy_make_move(current_state)
                    PIECE_NAME = {
                        "p": "pawn",
                        "b": "bishop",
                        "n": "knight",
                        "r": "rook",
                        "q": "queen",
                        "k": "king",
                    }
                    start = computer_move[:2]
                    end = computer_move[2:4]
                    piece = PIECE_NAME[
                        self.game.board.get_piece(self.game.xy2i(computer_move[:2]))
                    ]
                    captured_piece = self.game.board.get_piece(
                        self.game.xy2i(computer_move[2:4])
                    )
                    if captured_piece != " ":
                        captured_piece = PIECE_NAME[captured_piece.lower()]
                        print("---------------------------------")
                        print(
                            "Computer's \033[92m{piece}\033[0m at \033[92m{start}\033[0m captured \033[91m{captured_piece}\033[0m at \033[91m{end}\033[0m.".format(
                                piece=piece,
                                start=start,
                                captured_piece=captured_piece,
                                end=end,
                            )
                        )
                        print("---------------------------------")
                    else:
                        print("---------------------------------")
                        print(
                            "Computer moved \033[92m{piece}\033[0m at \033[92m{start}\033[0m to \033[92m{end}\033[0m.".format(
                                piece=piece, start=start, end=end
                            )
                        )
                        print("---------------------------------")
                    print(
                        "\033[1mNodes visited:\033[0m        \033[93m{}\033[0m".format(
                            self.computer.node_count
                        )
                    )
                    print(
                        "\033[1mNodes cached:\033[0m         \033[93m{}\033[0m".format(
                            len(self.computer.cache)
                        )
                    )
                    print(
                        "\033[1mNodes found in cache:\033[0m \033[93m{}\033[0m".format(
                            self.computer.found_in_cache
                        )
                    )
                    print(
                        "\033[1mUpdates to cache:\033[0m \033[93m{}\033[0m".format(
                            self.computer.updates
                        )
                    )
                    print(
                        "\033[1mElapsed time in sec:\033[0m  \033[93m{time}\033[0m".format(
                            time=time.time() - start_time
                        )
                    )
                    self.game.apply_move(computer_move)
                captured = self.captured_pieces(str(self.game))
                self.computer.print_board(str(self.game), captured)
            user_move = input("Game over. Play again? y/n: ")
            if user_move.lower() == "y":
                self.game = Game()
                self.computer.game = self.game
                self.prompt_user()
            # cache moves into JSON file
            with open("./moves_cache.json", "w") as f:
                if self.computer.max_depth % 2 == 0:
                    for key in self.computer.cache:
                        cache_moves["even"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
                else:
                    for key in self.computer.cache:
                        cache_moves["odd"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
        except KeyboardInterrupt:
            with open("./moves_cache.json", "w") as f:
                if self.computer.max_depth % 2 == 0:
                    for key in self.computer.cache:
                        cache_moves["even"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
                else:
                    for key in self.computer.cache:
                        cache_moves["odd"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
            print("\nYou quitter!")

    # def write_to_cache(self):

    def captured_pieces(self, board_state):
        piece_tracker = {
            "P": 8,
            "B": 2,
            "N": 2,
            "R": 2,
            "Q": 1,
            "K": 1,
            "p": 8,
            "b": 2,
            "n": 2,
            "r": 2,
            "q": 1,
            "k": 1,
        }
        captured = {"w": [], "b": []}
        for char in board_state.split()[0]:
            if char in piece_tracker:
                piece_tracker[char] -= 1
        for piece in piece_tracker:
            if piece_tracker[piece] > 0:
                if piece.isupper():
                    captured["w"] += piece_tracker[piece] * piece
                else:
                    captured["b"] += piece_tracker[piece] * piece
            piece_tracker[piece] = 0
        return captured

    def save_game_state(self, file_name, game_state):
        # Create a folder named "saves" if it doesn't exist
        save_folder = "saves"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        # Construct the file path
        file_path = os.path.join(save_folder, file_name + ".txt")
        for move in self.game.move_history:
            game_state += "\n" + move
        # Save the game state to the file
        with open(file_path, "w") as file:
            file.write(game_state)

        print(f"Game state saved to {file_path}")

    def getSave(self, directory="saves"):
        # List all txt files in the given directory
        txt_files = [file for file in os.listdir(directory) if file.endswith(".txt")]

        if not txt_files:
            print("No txt files found in the directory.")
            return

        print("Available txt files:")
        for txt_file in txt_files:
            print(txt_file[: txt_file.find(".")])

        while True:
            # Get input from the user
            file_name = input(
                "Enter the name of the txt file you want to open (without extension): "
            )

            # Check if the file exists in the directory
            if file_name + ".txt" not in txt_files:
                print(
                    f"The file '{file_name}.txt' does not exist in the directory. Please enter a valid file name."
                )
            else:
                # Try to open the file
                try:
                    with open(os.path.join(directory, file_name + ".txt"), "r") as file:
                        file_content = file.read()
                        notations = file_content.split("\n")
                        self.game.move_history = notations[1:]
                        return notations[0]
                except Exception as e:
                    print(f"Error opening the file: {e}")
                    return


class AI:
    def __init__(self, game, max_depth=7, leaf_nodes=[], node_count=0):
        self.max_depth = max_depth
        self.leaf_nodes = heuristic_gen(leaf_nodes)
        self.game = game
        self.moveset_size = 8
        self.node_count = node_count
        self.updates = 0
        self.time_limit = 140

        if self.max_depth % 2 == 0:
            self.cache = cache_moves["even"]
        else:
            self.cache = cache_moves["odd"]
        self.found_in_cache = 0

    def print_board(self, board_state, captured={"w": [], "b": []}):
        PIECE_SYMBOLS = {
            "P": "\033[93mP\033[0m",
            "B": "\033[93mB\033[0m",
            "N": "\033[93mN\033[0m",
            "R": "\033[93mR\033[0m",
            "Q": "\033[93mQ\033[0m",
            "K": "\033[93mK\033[0m",
            "p": "\033[94mp\033[0m",
            "b": "\033[94mb\033[0m",
            "n": "\033[94mn\033[0m",
            "r": "\033[94mr\033[0m",
            "q": "\033[94mq\033[0m",
            "k": "\033[94mk\033[0m",
        }
        board_state = board_state.split()[0].split("/")
        board_state_str = "\n"
        white_captured = " ".join(PIECE_SYMBOLS[piece] for piece in captured["w"])
        black_captured = " ".join(PIECE_SYMBOLS[piece] for piece in captured["b"])
        for i, row in enumerate(board_state):
            board_state_str += str(8 - i)
            for char in row:
                if char.isdigit():
                    board_state_str += " 0" * int(char)
                else:
                    board_state_str += " " + PIECE_SYMBOLS[char]
            if i == 0:
                board_state_str += "   Captured:" if len(white_captured) > 0 else ""
            if i == 1:
                board_state_str += "   " + white_captured
            if i == 6:
                board_state_str += "   Captured:" if len(black_captured) > 0 else ""
            if i == 7:
                board_state_str += "   " + black_captured
            board_state_str += "\n"
        board_state_str += "  A B C D E F G H"
        self.found_in_cache = 0
        self.node_count = 0
        print(board_state_str)

    def get_moves(self, board_state=None):
        if board_state == None:
            board_state = str(self.game)
        possible_moves = []
        for move in Game(board_state).get_moves():
            if len(move) < 5 or move[4] == "q":
                clone = Game(board_state)
                clone.apply_move(move)
                node = Node(str(clone))
                node.algebraic_move = move
                possible_moves.append(node)
        return possible_moves

    def get_heuristic(self, board_state=None):
        if board_state == None:
            board_state = str(self.game)
        clone = Game(board_state)
        total_points = 0
        # total piece count
        total_points += heuristics.material(board_state, 100)
        total_points += heuristics.piece_moves(clone, 50)
        total_points += heuristics.in_check(clone, 1)
        total_points += heuristics.structure(board_state, 0.1)

        return total_points

    def ab_make_move(self, board_state):
        possible_moves = self.get_moves(board_state)
        alpha = float("-inf")
        beta = float("inf")
        best_move = possible_moves[0]
        print()
        for move in possible_moves:
            board_value = self.ab_minimax(move, alpha, beta, 1)
            if alpha < board_value:
                alpha = board_value
                best_move = move
                best_move.value = alpha
            self.print_best(best_move, alpha)
        # best_move at this point stores the move with the highest heuristic
        # updates heuristic if it is mistaken
        cache_parse = zobrist.hash(
            board_state.split(" ")[0] + " " + board_state.split(" ")[1]
        )
        if cache_parse in self.cache:
            if self.cache[cache_parse] < alpha:
                self.cache[cache_parse] = alpha
                self.updates += 1
        else:
            self.cache[cache_parse] = alpha
        return best_move.algebraic_move

    def ab_minimax(self, node, alpha, beta, current_depth=0):
        current_depth += 1
        board_state = node.board_state
        cache_parse = zobrist.hash(
            board_state.split(" ")[0] + " " + board_state.split(" ")[1]
        )

        if current_depth == self.max_depth:
            if cache_parse in self.cache:
                self.found_in_cache += 1
                return self.cache[cache_parse]
            else:
                board_value = self.get_heuristic(node.board_state)
                self.cache[cache_parse] = board_value
                if current_depth % 2 == 0:
                    # pick largest number, where root is black and even depth
                    if alpha < board_value:
                        alpha = board_value
                    self.node_count += 1
                    return alpha
                else:
                    # pick smallest number, where root is black and odd depth
                    if beta > board_value:
                        beta = board_value
                    self.node_count += 1
                    return beta
        if current_depth % 2 == 0:
            # min player's turn
            for child_node in self.get_moves(node.board_state):
                if alpha < beta:
                    board_value = self.ab_minimax(
                        child_node, alpha, beta, current_depth
                    )
                    if beta > board_value:
                        beta = board_value
            return beta
        else:
            # max player's turn
            for child_node in self.get_moves(node.board_state):
                if alpha < beta:
                    board_value = self.ab_minimax(
                        child_node, alpha, beta, current_depth
                    )
                    if alpha < board_value:
                        alpha = board_value
            return alpha

    def print_best(self, move, value):
        score_tab = ""
        alg = move.algebraic_move
        score_tab += f"Best move: {alg} {value}"

        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        print(score_tab)

    def greedy_make_move(self, board_state):
        possible_moves = self.get_moves(board_state)
        alpha = float("-inf")
        beta = float("inf")
        start_time = time.time()
        current_depth = 1
        small_moveset = self.preorder_moves(possible_moves, current_depth, start_time)
        best_move = small_moveset[0]
        for move in small_moveset:
            board_value = self.greedy_minimax(
                move, alpha, beta, start_time, current_depth
            )
            if alpha < board_value:
                alpha = board_value
                best_move = move
                best_move.value = alpha
            self.print_best(best_move, alpha)

        # best_move at this point stores the move with the highest heuristic
        # updates heuristic if it is mistaken
        cache_parse = zobrist.hash(
            board_state.split(" ")[0] + " " + board_state.split(" ")[1]
        )
        if cache_parse in self.cache:
            if self.cache[cache_parse] < alpha:
                self.cache[cache_parse] = alpha
                self.updates += 1
        else:
            self.cache[cache_parse] = alpha
        return best_move.algebraic_move

    def greedy_minimax(self, node, alpha, beta, start_time, current_depth=0):
        current_depth += 1
        board_state = node.board_state
        cache_parse = zobrist.hash(
            board_state.split(" ")[0] + " " + board_state.split(" ")[1]
        )

        if current_depth >= self.max_depth:
            if cache_parse in self.cache:
                self.found_in_cache += 1
                return self.cache[cache_parse]
            else:
                board_value = self.get_heuristic(node.board_state)
                self.cache[cache_parse] = board_value
                self.node_count += 1
                if current_depth % 2 == 0:
                    # pick largest number, where root is black and even depth
                    if alpha < board_value:
                        alpha = board_value
                    return alpha
                else:
                    # pick smallest number, where root is black and odd depth
                    if beta > board_value:
                        beta = board_value
                    return beta
        possible_moves = self.get_moves(node.board_state)
        small_moveset = self.preorder_moves(possible_moves, current_depth, start_time)
        if time.time() - start_time > self.time_limit:
            return small_moveset[0].value

        if current_depth % 2 == 0:
            # min player's turn
            for child_node in small_moveset:
                if alpha < beta:
                    board_value = self.greedy_minimax(
                        child_node, alpha, beta, start_time, current_depth
                    )
                    if beta > board_value:
                        beta = board_value
                if time.time() - start_time > self.time_limit:
                    return max((small_moveset[0].value, beta))
            return beta
        else:
            # max player's turn
            for child_node in small_moveset:
                if alpha < beta:
                    board_value = self.greedy_minimax(
                        child_node, alpha, beta, start_time, current_depth
                    )
                    if alpha < board_value:
                        alpha = board_value
                if time.time() - start_time > self.time_limit:
                    return max((small_moveset[0].value, alpha))
            return alpha

    def preorder_moves(self, possible_moves, current_depth, start_time):
        small_moveset = []
        for move in possible_moves:
            board_value = 0
            board_state = move.board_state
            cache_parse = zobrist.hash(
                board_state.split(" ")[0] + " " + board_state.split(" ")[1]
            )
            if cache_parse in self.cache:
                self.found_in_cache += 1
                board_value = self.cache[cache_parse]
            else:
                board_value = self.get_heuristic(move.board_state)
                self.node_count += 1
                self.cache[cache_parse] = board_value
            move.value = board_value

            # Find the correct position for the value
            small_moveset = self.insert_into_sorted_list(
                small_moveset, move, current_depth % 2 == 0
            )
            if time.time() - start_time > self.time_limit:
                break
        return small_moveset

    def insert_into_sorted_list(self, sorted_list, move, prioritize_min=True):
        """
        Inserts the given value into the sorted list at its correct position, considering priorities and maximum size.

        Parameters:
        - sorted_list (list): The sorted list.
        - move: The move to be inserted into the list.
        - max_size (int): The maximum size the list can have.
        - prioritize_min (bool): If True, prioritize the minimum value; if False, prioritize the maximum value.

        Returns:
        - list: The updated sorted list.
        """

        # If the list is empty, just add the value
        if not sorted_list:
            sorted_list.append(move)
            return sorted_list
        # Determine the comparison operator based on the prioritization
        comparison_operator = (
            (lambda x, y: x < y) if prioritize_min else (lambda x, y: x > y)
        )
        # Insert the value at the correct position
        index = 0
        while index < len(sorted_list) and comparison_operator(
            sorted_list[index].value, move.value
        ):
            index += 1
        sorted_list.insert(index, move)

        # Check if the list exceeds the maximum size
        if len(sorted_list) > self.moveset_size:
            # Remove the least desirable value
            sorted_list.pop()

        return sorted_list


if __name__ == "__main__":
    new_test = Game_Engine("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    new_test.prompt_user()
