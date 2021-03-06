import random


class EngineInterface():
    """This class is intended to be the interface for this module."""
    def __init__(self, difficulty_level):
        """difficulty_level can be 1, 2 or 3."""
        self.game_state = GameState()
        self.difficulty_level = difficulty_level
        reset_transposition_table()

    def new_game(self):
        self.game_state = GameState()
        reset_transposition_table()

    def board_value(self, column, row):
        """Return "0" for an empty position, "1" for a first player disk and
        "2" for a second player disk.
        """
        return self.game_state.get_value(column, row)

    def legal(self, column):
        """Return true iff the move is legal"""
        return self.game_state.column_height[column] < 6

    def make_move(self, column):
        self.game_state.make_move(column)

    def draw(self):
        return self.game_state.number_of_moves == 42

    def four_in_a_row(self):
        """Return true if and only the last move made four in a row."""
        return self.game_state.four_in_a_row()

    def four_in_a_row_positions(self):
        """Return all positions on the board that have disks included in a four in a row.
        Positions are given as a set of (column, row)-pairs.
        """
        def disk_type(column, row):
            return self.game_state.board[10 + column + row * 9]

        def disks_are_of_same_type(col_row_pair_set):
            type_ = None
            all_equal = True
            for (column, row) in col_row_pair_set:
                if type_ == None:
                    type_ = disk_type(column, row)
                if type_ == "0":
                    return False
                if disk_type(column, row) != type_:
                    all_equal = False
            return all_equal

        possible_four_in_a_rows = []

        # Columns.
        for col in range(7):
            for row in range(3):
                col_row_pair_set = {(col, row), (col, row + 1),
                                    (col, row + 2), (col, row + 3)}
                possible_four_in_a_rows.append(col_row_pair_set)

        # Rows.
        for col in range(4):
            for row in range(6):
                col_row_pair_set = {(col, row), (col + 1, row),
                                    (col + 2, row), (col + 3, row)}
                possible_four_in_a_rows.append(col_row_pair_set)

        # Diagonals.
        for col in range(4):
            for row in range(3):
                col_row_pair_set = {(col, row), (col + 1, row + 1),
                                    (col + 2, row + 2), (col + 3, row + 3)}
                possible_four_in_a_rows.append(col_row_pair_set)

                col_row_pair_set = {(col, row + 3), (col + 1, row + 2),
                                    (col + 2, row + 1), (col + 3, row)}
                possible_four_in_a_rows.append(col_row_pair_set)

        four_in_a_rows = set()
        for col_row_pair_set in possible_four_in_a_rows:
            if disks_are_of_same_type(col_row_pair_set):
                four_in_a_rows |= col_row_pair_set

        return four_in_a_rows

    def engine_move(self):
        """Return an integer from 0 to 6 that represents a move made
        by the engine."""
        if self.difficulty_level == 1:
            return computer_move_level_1(self.game_state)
        if self.difficulty_level == 2:
            return computer_move_level_2(self.game_state)
        if self.difficulty_level == 3:
            return computer_move_level_3(self.game_state)


class GameState:
    """Instances of this object stores game states. A board configuration is stored as
    a list of lengths 72. Empty positions are stored as "0". The players are called "1" and "2",
    where "1" always make the first move.

    Some of the entries in the list is always 0. They represent the positions outside of the
    board, as in the following diagram.

    000000000
    0xxxxxxx0
    0xxxxxxx0
    0xxxxxxx0
    0xxxxxxx0
    0xxxxxxx0
    0xxxxxxx0
    000000000

    The positions with x are the positions on the board. The position in the lower left
    corner have index 10, the next index 11 etc.

    Many times in this program, rows and columns are refered to. Rows are counted from
    below and numbered 0, 1, ..., 5. Columns are counted from the left and are numbered
    0, 1, ..., 6. Moves are represented by the corresponding columns the moves are made to.
    """
    def __init__(self):
        self.number_of_moves = 0
        self.column_height = [0,0,0,0,0,0,0]
        self.move_history = [None]*42
        self.board = ["0"]*72

    def print_board(self):
        """Print the game state."""
        for row in range(6):
            row_string = ""
            for col in range(7):
                row_string += self.get_value(col, 5-row)
            print(row_string)
        print()

    def get_value(self, column, row):
        return self.board[10 + column + row * 9]

    def make_move(self, column):
        position = 10 + column + self.column_height[column] * 9
        self.board[position] = ("1", "2")[self.number_of_moves % 2]
        self.move_history[self.number_of_moves] = position
        self.column_height[column] += 1
        self.number_of_moves += 1

    def undo_last_move(self):
        self.number_of_moves -= 1
        position = self.move_history[self.number_of_moves]
        self.column_height[position % 9 - 1] -= 1
        self.board[position] = "0"

    def make_null_move(self):
       self.number_of_moves += 1

    def undo_null_move(self):
       self.number_of_moves -= 1

    def key(self):
        """Return a unique key for the position that can be used in a dictionary."""
        return "".join(self.board)

    def can_win_this_move(self):
        """Return true iff a the player in turn can make a move a move that gives
           a four in a row."""
        for move in range(7):
            if self.column_height[move] < 6:
                self.make_move(move)
                if self.four_in_a_row():
                    self.undo_last_move()
                    return True
                self.undo_last_move()
        return False

    def four_in_a_row(self):
        """True iff there is a four in a row that goes through the last made move."""
        position = self.move_history[self.number_of_moves - 1]
        player = self.board[position]

        # Columns
        if position // 9 >= 4:
            if self.board[position - 9] == player:
                if self.board[position - 18] == player:
                    if self.board[position - 27] == player:
                        return True

        # Rows
        in_row = 1
        if self.board[position - 1] == player:
            in_row += 1
            if self.board[position - 2] == player:
                in_row += 1
                if self.board[position - 3] == player:
                    in_row += 1
        if self.board[position + 1] == player:
            in_row += 1
            if self.board[position + 2] == player:
                in_row += 1
                if self.board[position + 3] == player:
                    in_row += 1
        if in_row >= 4:
            return True

        # Diagonals
        in_row = 1
        if self.board[position - 10] == player:
            in_row += 1
            if self.board[position - 20] == player:
                in_row += 1
                if self.board[position - 30] == player:
                    in_row += 1
        if self.board[position + 10] == player:
            in_row += 1
            if self.board[position + 20] == player:
                in_row += 1
                if self.board[position + 30] == player:
                    in_row += 1
        if in_row >= 4:
            return True

        in_row = 1
        if self.board[position - 8] == player:
            in_row += 1
            if self.board[position - 16] == player:
                in_row += 1
                if self.board[position - 24] == player:
                    in_row += 1
        if self.board[position + 8] == player:
            in_row += 1
            if self.board[position + 16] == player:
                in_row += 1
                if self.board[position + 24] == player:
                    in_row += 1
        if in_row >= 4:
            return True

        return False

def heuristic_function_constant(game_state, move):
    return 0

def heuristic_function_1(game_state, move):
    """Give a heuristic evaluation in form of a number
    of how good it would be to make "move" to "game_state". The value is
    higher the better the move, regardless of the player to make it.

    This function give higher values to more central columns.
    """
    return -abs(3 - move)

def heuristic_function_3(game_state, move):
    """Give a heuristic evaluation in form of a number
    of how good it would be to make "move" to "game_state". The value is
    higher the better the move, regardless of the player to make it.

    This function give higher values to more central columns and rows.
    Tests shows that this function is stronger than the above heuristic functions.
    """
    row = game_state.column_height[move]
    return -abs(3 - move) - abs(2.5 - row)

def heuristic_function_4(game_state, move):
    """Give a heuristic evaluation in form of a number
    of how good it would be to make "move" to "game_state". The value is
    higher the better the move, regardless of the player to make it.

    This function give higher values to more central positions.
    At higher depth calculations this heuristic appear to be better than heuristic_function_3.
    """
    row = game_state.column_height[move]
    values = [[0, 0, 0, 0, 0, 0, 0],
              [0, 0, 1, 1, 1, 0, 0],
              [0, 1, 1, 1, 1, 1, 0],
              [0, 1, 1, 1, 1, 1, 0],
              [0, 0, 1, 1, 1, 0, 0],
              [0, 0, 0, 0, 0, 0, 0]]
    return values[row][move]

def heuristic_move(game_state, move_list, heuristic_function):
    """Return a move from move_list that is given the highest value by
    heuristic_function. It there are several such moves, then one of
    them are chosen randomly.
    """
    heuristic_values = [heuristic_function(game_state, move) for move in move_list]
    max_value = max(heuristic_values)
    best_moves = []
    for i in range(len(move_list)):
        if heuristic_values[i] == max_value:
            best_moves.append(move_list[i])
    return random.choice(best_moves)

def blocking_moves(game_state):
    """Return a list of moves that blocks an immediate four in a row for the opponent if
    such move exists.
    """
    move_list = []
    available_moves = [move for move in [3,2,4,1,5,0,6] if game_state.column_height[move] < 6]
    game_state.make_null_move()

    for col in available_moves:
        game_state.make_move(col)
        if game_state.four_in_a_row():
            move_list.append(col)
        game_state.undo_last_move()

    game_state.undo_null_move()
    return move_list

def computer_move_level_1(game_state):
    x = random.random()
    if x < 0.3:
        depth = min(game_state.number_of_moves + 2, 42)
    else:
        depth = min(game_state.number_of_moves + 3, 42)
    return computer_move(game_state, depth, heuristic_function_constant)

def computer_move_level_2(game_state):
    x = random.random()
    depth = min(game_state.number_of_moves + 4, 42)
    if x < 0.3:
        return computer_move(game_state, depth, heuristic_function_constant)
    else:
        return computer_move(game_state, depth, heuristic_function_4)

def computer_move_level_3(game_state):
    available_moves = [move for move in [3,2,4,1,5,0,6] if game_state.column_height[move] < 6]

    # Depth for the minimax algorithm is chosen based
    # on the number of filled columns.
    columns = len(available_moves)
    if columns < 4:
        depth = 20
        depth = min(game_state.number_of_moves + 20, 42)
    elif columns == 4:
        depth = 14
        depth = min(game_state.number_of_moves + 14, 42)
    elif columns == 5:
            depth = 12
            depth = min(game_state.number_of_moves + 12, 42)
    else:
        if game_state.number_of_moves == 0:
            return 3
        if game_state.number_of_moves < 8:
            depth = 6
            depth = min(game_state.number_of_moves + 6, 42)
        elif game_state.number_of_moves < 12:
            depth = 6
            depth = min(game_state.number_of_moves + 6, 42)
        else:
            depth = 6
            depth = min(game_state.number_of_moves + 6, 42)

    depth = min(depth + 1, 42)

#    if game_state.number_of_moves > 25:
#        depth = 42

    # Some opening moves.
    if game_state.number_of_moves == 0:
        return 3
    if game_state.number_of_moves == 1:
        return 3
    if game_state.number_of_moves == 2:
        return 3

    move = computer_move(game_state, depth, heuristic_function_4)
    return move

def negamax(game_state, depth, alpha, beta):
    """Compute a value of game_state. Return a positive integer for a winning game_state for
       the player in turn, 0 for a draw or unknown outcome and a negative integer for a loss.
       A win at move 42 give the score 1, a win at move 41 give a the score 2 etc,
       and vice versa for losses.
       Depth is counted as the move number at which the search is stopped. For example,
       depth=42 give a maximum depth search. This function can only be used on if the game state
       have no four in a row."""
    original_alpha = alpha;

    # If terminal node.
    if game_state.can_win_this_move():
        return 42 - game_state.number_of_moves

    # If not terminal node, but full depth.
    if game_state.number_of_moves == depth - 1:
        return 0

    global transposition_table

    moves = [3,2,4,1,5,0,6]

    # Check the transposition table.
    use_transposition_table = depth > 0
    if use_transposition_table:
        key = game_state.key()
        tt_data = transposition_table.get(key)
        if tt_data != None:
            (tt_depth, tt_type, tt_value) = tt_data

            if tt_type == 2:
                return tt_value

            if tt_value != 0 or tt_depth >= depth:
                if tt_value >= beta:
                    return beta

    # Else, return a value based on child node values.
    for move in moves:
        if game_state.column_height[move] < 6:
            game_state.make_move(move)
            value = -negamax(game_state, depth, -beta, -alpha)
            game_state.undo_last_move()
            if value >= beta: # Fail hard beta-cutoff.
                if use_transposition_table:
                    transposition_table.update({key:(depth, 1, beta)})
                return beta
            if value > alpha:
                alpha = value

    if use_transposition_table:
        if alpha > original_alpha: # Exact values.
            if alpha != 0:
                transposition_table.update({key:(depth, 2, alpha)})
    return alpha

def root_negamax(game_state, move_order, depth, alpha, beta):
    for move in move_order:
        game_state.make_move(move)
        new_value = -negamax(game_state, depth, -beta, -alpha)
        game_state.undo_last_move()
        if new_value > alpha:
            best_move = move
            alpha = new_value
    return best_move

def computer_move(game_state, depth, heuristic_function):
    """Return a move computed by using the minimax algorithm
    and heuristic evaluations.
    """
    def best_moves(move_list, value_list):
        best_value = max(value_list)
        return [move_list[i] for i in range(len(move_list))
                if value_list[i] == best_value]

    available_moves = [move for move in [3,2,4,1,5,0,6] if game_state.column_height[move] < 6]

    # Moves are shuffled before they are sorted in order to make the move order
    # more varied. Shuffling take longer time, maybe because of less optimal usage of
    # the transposition table, but it anyway appear to give a stronger engine, even if
    # the depth level is lowered.
    random.shuffle(available_moves)

    def search_key(move):
        return heuristic_function(game_state, move)

    # The available moves are sorted based on the heuristic function.
    available_moves.sort(key=search_key, reverse=True)

    # Look for a move that makes a four in a row.
    for move in available_moves:
        if game_state.column_height[move] < 6:
            game_state.make_move(move)
            if game_state.four_in_a_row():
                game_state.undo_last_move()
                return move
            game_state.undo_last_move()

    # Look for blocking moves.
    if game_state.number_of_moves <= 40:
        move_list = blocking_moves(game_state)
        if move_list:
            return heuristic_move(game_state, move_list, heuristic_function)

    alpha = -10000
    beta = 10000

#    # Iterative deepening.
#    if depth == 42:
#        available_moves = [move for move in [3,2,4,1,5,0,6] if game_state.column_height[move] < 6]
#        for d in range(game_state.number_of_moves + 2, depth):
#            best_move = root_negamax(game_state, available_moves, d, alpha, beta)
#            available_moves = [best_move] + [move for move in [3,2,4,1,5,0,6]
#                              if game_state.column_height[move] < 6 and move != best_move]

    return root_negamax(game_state, available_moves, depth, alpha, beta)

def reset_transposition_table():
    global transposition_table
    transposition_table = dict()
