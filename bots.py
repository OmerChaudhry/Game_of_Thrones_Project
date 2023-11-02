#!/usr/bin/python
import math
import numpy as np
from GoT_problem import *
from GoT_types import CellType
import random
import getch
# import msvcrt


# Throughout this file, ASP means adversarial search problem.
class StudentBot:
    """ Write your student bot here """

    def decide(self, asp):
        """
        Input: asp, a GoTProblem
        Output: A direction in {'U','D','L','R'}
        To get started, you can get the current
        state by calling asp.get_start_state()
        """
        return "U"

    def cleanup(self):
        """
        Input: None
        Output: None
        This function will be called in between
        games during grading. You can use it
        to reset any variables your bot uses during the game
        (for example, you could use this function to reset a
        turns_elapsed counter to zero). If you don't need it,
        feel free to leave it as "pass"
        """
        pass


class RandBot:
    """Moves in a random (safe) direction"""

    def decide(self, asp):
        """
        Input: asp, a GoTProblem
        Output: A direction in {'U','D','L','R'}
        """
        state = asp.get_start_state()
        locs = state.player_locs
        board = state.board
        ptm = state.ptm
        loc = locs[ptm]
        possibilities = list(GoTProblem.get_safe_actions(board, loc, ptm))
        if possibilities:
            return random.choice(possibilities)
        return "U"

    def cleanup(self):
        pass


class ManualBot:
    """Bot which can be manually controlled using W, A, S, D"""

    def decide(self, asp: GoTProblem):
        # maps keyboard input to {U, D, L, R}
        dir_map = {'A': 'L', 'W': 'U', 
                   'a': 'L', 'w': 'U', 
                   'S': 'D', 'D': 'R', 
                   's': 'D', 'd': 'R'}
        # Command for mac/unix:
        direction = getch.getch()
        # Command for Windows:
        # direction = msvcrt.getch().decode('ASCII')
        return dir_map[direction]

    def cleanup(self):
        pass

class AttackBot:
    """Aggressive bot which attacks opposing player when possible"""

    def __init__(self):
        self.prev_cell_type = None
        self.last_move = None
        self.ptm = None
        self.perm_cell = None
        self.temp_cell = None
        self.opp_temp_cell = None

    def cleanup(self):
        self.prev_cell_type = None
        self.last_move = None
        self.ptm = None
        self.perm_cell = None
        self.temp_cell = None
        self.opp_temp_cell = None

    def dist_from_opp(self, opp_loc, ptm_loc):
        dist = 0
        for i in range(len(opp_loc)):
            dist += abs(opp_loc[i] - ptm_loc[i])
        return dist

    def min_dist_to_temp(self, board, ptm_loc):
        locs = self.temp_barrier_locs_from_board(board)
        min_dist = math.inf
        for loc in locs:
            this_dist = self.dist_from_opp(loc, ptm_loc)
            if this_dist < min_dist:
                min_dist = this_dist
        return min_dist

    def temp_barrier_locs_from_board(self, board):
        if self.opp_temp_cell is None:
            return []
        loc_dict = {}
        num_temp = 0
        for r in range(len(board)):
            for c in range(len(board[r])):
                char = board[r][c]
                if char == self.opp_temp_cell:
                    loc_dict[num_temp] = (r, c)
                    num_temp += 1
        loc_list = []
        for index in range(num_temp):
            loc_list.append(loc_dict[index])
        return loc_list

    def decide(self, asp):
        """
        Input: asp, a GoTProblem
        Output: A direction in {'U','D','L','R'}
        """
        state = asp.get_start_state()
        locs = state.player_locs
        board = state.board
        ptm = state.ptm
        loc = locs[ptm]
        possibilities = list(GoTProblem.get_safe_actions(board, loc, ptm))
        opp_loc = locs[(ptm + 1) % 2]
        if self.ptm is None:
            self.ptm = ptm
            self.perm_cell = CellType.TWO_PERM
            self.temp_cell = CellType.TWO_TEMP
            self.opp_temp_cell = CellType.ONE_TEMP
            if ptm == 0:
                self.perm_cell = CellType.ONE_PERM
                self.temp_cell = CellType.ONE_TEMP
                self.opp_temp_cell = CellType.TWO_TEMP

        if not possibilities:
            return "U"

        if self.prev_cell_type is None:
            "Attack bot starting"
            self.prev_cell_type = self.temp_cell
            this_move = possibilities[0]
            self.last_move = this_move
            return this_move

        # if player needs to return to perm area
        must_return_to_perm = False
        if self.prev_cell_type == self.temp_cell:
            this_move = None
            if self.last_move == "U":
                this_move = "D"
            elif self.last_move == "D":
                this_move = "U"
            elif self.last_move == "R":
                this_move = "L"
            elif self.last_move == "L":
                this_move = "R"
            else:
                raise Exception

            self.prev_cell_type = self.perm_cell
            self.last_move = this_move
            must_return_to_perm = True

        # else, player is (potentially) leaving perm area
        min_dist = math.inf
        min_dist_to_temp = math.inf
        go_for_temp = False
        decision = possibilities[0]
        min_next_loc = [None] * 2
        for move in possibilities:
            next_loc = GoTProblem.move(loc, move)
            dist_from_opponent = self.dist_from_opp(next_loc, opp_loc)
            this_dist_to_temp = self.min_dist_to_temp(board, next_loc)
            if this_dist_to_temp == 0:
                return move

            if not must_return_to_perm:
                # If we are close to temp barrier
                if this_dist_to_temp <= 5 or go_for_temp:
                    go_for_temp = True
                    if this_dist_to_temp < min_dist_to_temp:
                        min_dist_to_temp = this_dist_to_temp
                        decision = move
                        min_next_loc = next_loc

                elif dist_from_opponent < min_dist:
                    min_dist = dist_from_opponent
                    decision = move
                    min_next_loc = next_loc
                    min_dist_to_temp = this_dist_to_temp

                elif dist_from_opponent == min_dist:
                    if this_dist_to_temp < min_dist_to_temp:
                        min_dist_to_temp = this_dist_to_temp
                        decision = move
                        min_next_loc = next_loc

        if not must_return_to_perm:
            if board[min_next_loc[0]][min_next_loc[1]] == self.perm_cell:
                self.prev_cell_type = self.perm_cell
            else:
                self.prev_cell_type = self.temp_cell
            self.last_move = decision
        return self.last_move


class SafeBot:
    """Bot that plays safe and takes area"""

    def __init__(self):
        self.prev_move = None
        self.to_empty = []
        self.algo_path = []
        self.path = []
        self.calc_empty = False
        self.order = {"U": ("L", "R"), 
                    "D": ("L", "R"), 
                    "L": ("U", "D"),
                    "R": ("U", "D")}

    def cleanup(self): 
        self.prev_move = None
        self.to_empty = []
        self.algo_path = []
        self.path = []
        self.calc_empty = False
        self.order = {"U": ("L", "R"), 
                    "D": ("L", "R"), 
                    "L": ("U", "D"),
                    "R": ("U", "D")}
    
    def get_safe_neighbors_wall(self, board, loc):
        neighbors = [
                ((loc[0] + 1, loc[1]), D),
                ((loc[0] - 1, loc[1]), U),
                ((loc[0], loc[1] + 1), R),
                ((loc[0], loc[1] - 1), L),
            ]
        return list(filter(lambda m: board[m[0][0]][m[0][1]] != CellType.WALL, neighbors))

    def get_safe_neighbors_no_wall(self, board, loc, wall):
        neighbors = [
                ((loc[0] + 1, loc[1]), D),
                ((loc[0] - 1, loc[1]), U),
                ((loc[0], loc[1] + 1), R),
                ((loc[0], loc[1] - 1), L),
            ]
        return list(filter(lambda m: board[m[0][0]][m[0][1]] != CellType.WALL and board[m[0][0]][m[0][1]] != wall, neighbors))

    def decide(self, asp: GoTProblem):
        state = asp.get_start_state()
        if not self.path:
            if self.calc_empty:
                self.gen_path_to_empty(state)
                self.path += self.to_empty
                self.to_empty = []
                self.calc_empty = False
            else:
                self.gen_space_grab(state)
                self.path += self.algo_path
                self.algo_path = []
                self.calc_empty = True
        move = self.path.pop(0)
        self.prev_move = move
        return move  
        
    def gen_space_grab(self, state : GoTState):
        board = state.board
        loc = state.player_locs[state.ptm]
        if state.ptm == 0:
            player_wall = CellType.ONE_PERM
        else:
            player_wall = CellType.TWO_PERM
        avail_actions = {U, D, L, R}
        prev = self.prev_move
        if prev:
            avail_actions.remove(prev)
        else:
            safe_actions = self.get_safe_neighbors_wall(board, loc)
            random.shuffle(safe_actions)
            loc, move = safe_actions[0]
            self.algo_path.append(move)
            avail_actions.remove(move)
            prev = move
        while avail_actions:
            safe_moves = self.get_safe_neighbors_no_wall(board, loc, player_wall)
            safe_moves_wall = self.get_safe_neighbors_wall(board,loc)
            if not safe_moves and not safe_moves_wall:
                self.algo_path.append(U)
                return
            random.shuffle(safe_moves)
            random.shuffle(safe_moves_wall)
            use_wall = True
            for loc, move in safe_moves:
                board_val = board[loc[0]][loc[1]]
                if move in self.order[prev] and move in avail_actions and board_val != player_wall:
                    self.algo_path.append(move)
                    avail_actions.remove(move)
                    prev = move
                    use_wall = False
                    break
            if use_wall:
               for loc, move in safe_moves_wall:
                    board_val = board[loc[0]][loc[1]]
                    if move in self.order[prev] and move in avail_actions:
                        self.algo_path.append(move)
                        avail_actions.remove(move)
                        prev = move
                        use_wall = False
                        break 
        return

    def gen_path_to_empty(self, state: GoTState):
        board = state.board
        player_loc = state.player_locs[state.ptm]
        to_check = [(player_loc, None)]
        checked = {(player_loc, None): None}
        while to_check:
            loc, m = to_check.pop(0)
            neighbors = [
                ((loc[0] + 1, loc[1]), D),
                ((loc[0] - 1, loc[1]), U),
                ((loc[0], loc[1] + 1), R),
                ((loc[0], loc[1] - 1), L),
            ]
            random.shuffle(neighbors)
            for move in neighbors:
                x, y = move[0][0], move[0][1]
                board_val = board[x][y]
                if move not in checked and board_val != CellType.WALL:
                    checked[move] = (loc, m)
                    if board_val == ' ':
                        path = []
                        while move[1] is not None:
                            path.append(move[1])
                            move = checked[move]
                        self.to_empty += path
                        return
                    else:
                        to_check.append(move)
        self.to_empty += [U]
        return
