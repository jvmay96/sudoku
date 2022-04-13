import numpy
from tkinter import Tk, Frame, Button, Canvas
from collections import deque
from random import randint
from time import sleep


class SudokuGame:
    def __init__(self):
        self.height = 9
        self.width = 9
        self._board = numpy.zeros((self.width, self.height), dtype=int)
        self.frozen_tiles = set()  # frozen tiles can not have their values altered.

    def get_board(self):
        return numpy.array(self._board)

    def set_board(self, array):
        self._board = array

    board = property(get_board, set_board)

    def set_tile(self, row, col, value: int):
        self._board[row][col] = value

    def valid_move(self, row, col, value):
        # check row
        for i in range(self.width):
            if self._board[row][i] == value:
                return False
        for i in range(self.height):
            if self._board[i][col] == value:
                return False
        row_region = range(3*int(row/3), 3*int((row/3) + 1))
        col_region = range(3*int(col/3), 3*int((col/3) + 1))
        for i in row_region:
            for j in col_region:
                if self._board[i][j] == value:
                    return False
        return True

    def is_full(self):
        for row in self._board:
            for value in row:
                if value == 0:
                    return False
        return True

    def freeze_tile(self, row, col):
        self.frozen_tiles.add((row, col))

    def tile_is_frozen(self, row, col):
        return (row, col) in self.frozen_tiles

    def __str__(self):
        return str(self._board)

    def __iter__(self):
        return self._board.__iter__()

    def __getitem__(self, item):
        return self._board[item]


class SudokuFrame(Frame):
    def __init__(self, board_height=9, board_width=9):
        super().__init__()
        self.tile_width = 60
        self.board_height = board_height
        self.board_width = board_width
        self.height = self.board_height*self.tile_width
        self.width = self.board_width*self.tile_width
        self.board_canvas = Canvas(self, height=9*self.tile_width, width=9*self.tile_width)
        self.board_canvas.pack()
        x_partition = [i*self.tile_width for i in range(self.board_width + 1)]
        y_partition = [i * self.tile_width for i in range(self.board_height + 1)]

        # create tiles
        self.tiles = {}
        for i in range(self.board_height):
            for j in range(self.board_width):
                self.tiles[(i, j)] = self.board_canvas.create_rectangle(x_partition[j], y_partition[i],
                                                                        x_partition[j+1], y_partition[i+1],
                                                                        fill="white")
        # create text
        self.values = {}
        for i in range(self.board_height):
            for j in range(self.board_width):
                self.values[(i, j)] = Button(self.board_canvas, text="0", font=("Arial", 20), bg="white", width=2,
                                             relief="flat")
                self.values[(i, j)].place(x=j*self.tile_width + 10, y=i*self.tile_width + 3)

        # create lines
        for i in range(1, self.board_height-1):
            # horizontal
            if i % 3 == 0:
                self.board_canvas.create_line(0, i*self.tile_width, self.width, i*self.tile_width, width=3)

        for i in range(1, self.board_width - 1):
            # vertical
            if i % 3 == 0:
                self.board_canvas.create_line(i*self.tile_width, 0, i*self.tile_width, self.height, width=3)

    def set_value(self, row, col, value):
        self.values[(row, col)]["text"] = value
        self.update()

    def draw(self, game):
        for i in range(self.board_height):
            for j in range(self.board_width):
                self.values[(i, j)]["text"] = str(game[i][j])
                self.update()


class SudokuSolver:
    def __init__(self, sudoku_game):
        self.game = sudoku_game
        self.screens = []
        self.discovered = deque()
        self.visited = set()

    def add_screen(self, screen):
        self.screens.append(screen)

    def _find_empty_cell(self):
        for i, row in enumerate(self.game):
            for j, item in enumerate(row):
                if item == 0:
                    return i, j

    def solve(self, speed=100):
        max_delay = 0.5  # seconds
        delay = (max_delay - (speed/100)*max_delay)
        self.discovered.append(self.game.board)
        while self.discovered:
            sleep(delay)
            self.game.board = self.discovered.pop()
            self.visited.add(str(self.game.board))  # lists are not hashable
            for screen in self.screens:
                screen.draw(self.game.board)
            if self.game.is_full():
                return True
            empty_cell = self._find_empty_cell()
            row = empty_cell[0]
            col = empty_cell[1]
            for i in range(1, 10):
                if self.game.valid_move(row, col, i):
                    self.game[row][col] = i
                    if str(self.game) not in self.visited:
                        self.discovered.append(self.game.board)
        return False


def generate_random_board(game, board, sparsity=50):
    solver = SudokuSolver(game)
    random_row = randint(0, game.height-1)
    random_col = randint(0, game.width-1)
    random_value = randint(0, 9)
    game.board[random_row][random_col] = random_value
    solver.solve()
    number_of_tiles_to_remove = int((sparsity/100)*game.height*game.width)
    removed_tiles = set()
    for i in range(number_of_tiles_to_remove):
        random_row = randint(0, game.height-1)
        random_col = randint(0, game.width-1)
        while (random_row, random_col) in removed_tiles:
            random_row = randint(0, game.height-1)
            random_col = randint(0, game.width-1)
        game[random_row][random_col] = 0
        removed_tiles.add((random_row, random_col))
    game.set_board(game.board)  # freezes non-zero tiles
    board.draw(game.board)


def main():
    game = SudokuGame()
    sparsity = 60
    speed = 50
    root = Tk()
    board = SudokuFrame(game.height, game.width)
    solver = SudokuSolver(game)
    solver.add_screen(board)
    board.grid(row=0, column=0, rowspan=3)
    solve_button = Button(text="solve", command=lambda: solver.solve(speed))
    new_board_button = Button(text="new board", command=lambda: generate_random_board(game, board, sparsity))
    solve_button.grid(row=1, column=1, sticky="s")
    new_board_button.grid(row=2, column=1, sticky="n")
    root.mainloop()


if __name__ == "__main__":
    main()
