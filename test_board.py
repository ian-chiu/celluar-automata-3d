import unittest
from _board import Board
from rule import Rule
import glm


side = 10
rule = Rule("0,1,2,3,4,5,6/1,3/2/VN", 1.0, 0.1)
center = glm.ivec3(side / 2, side / 2, side / 2)


class TestClass(unittest.TestCase):
    def make_test_board(self, iteration):
        test_board = Board(side, rule)
        test_board.set_cell_state(1, center.x, center.y, center.z)
        for i in range(iteration):
            test_board.update()
        return test_board

    def compare_answer(self, test_board, answer_board):
        for x in range(side):
            for y in range(side):
                for z in range(side):
                    self.assertEqual(answer_board.get_cell_state(x, y, z),
                                     test_board.get_cell_state(x, y, z),
                                     f"cell state at ({x}, {y}, {z}) is different...")

    def test_iteration_1(self):
        test_board = self.make_test_board(1)

        answer_board = Board(side, rule)
        answer_board.set_cell_state(1, center.x + 1, center.y, center.z)
        answer_board.set_cell_state(1, center.x, center.y + 1, center.z)
        answer_board.set_cell_state(1, center.x, center.y, center.z + 1)
        answer_board.set_cell_state(1, center.x - 1, center.y, center.z)
        answer_board.set_cell_state(1, center.x, center.y - 1, center.z)
        answer_board.set_cell_state(1, center.x, center.y, center.z - 1)

        self.compare_answer(test_board, answer_board)


    def test_iteration_2(self):
        test_board = self.make_test_board(2)

        answer_board = Board(side, rule)
        answer_board.set_cell_state(1, center.x + 2, center.y, center.z)
        answer_board.set_cell_state(1, center.x, center.y + 2, center.z)
        answer_board.set_cell_state(1, center.x, center.y, center.z + 2)
        answer_board.set_cell_state(1, center.x - 2, center.y, center.z)
        answer_board.set_cell_state(1, center.x, center.y - 2, center.z)
        answer_board.set_cell_state(1, center.x, center.y, center.z - 2)

        for x in range(side):
            for y in range(side):
                for z in range(side):
                    self.assertEqual(answer_board.get_cell_state(x, y, z),
                                     test_board.get_cell_state(x, y, z),
                                     f"cell state at ({x}, {y}, {z}) is different...")

    def test_iteration_3(self):
        test_board = self.make_test_board(3)

        answer_board = Board(side, rule)
        answer_board.set_cell_state(1, center.x + 2 + 1, center.y, center.z)
        answer_board.set_cell_state(1, center.x + 2, center.y + 1, center.z)
        answer_board.set_cell_state(1, center.x + 2, center.y, center.z + 1)
        answer_board.set_cell_state(1, center.x + 2 - 1, center.y, center.z)
        answer_board.set_cell_state(1, center.x + 2, center.y - 1, center.z)
        answer_board.set_cell_state(1, center.x + 2, center.y, center.z - 1)

        answer_board.set_cell_state(1, center.x + 1, center.y + 2, center.z)
        answer_board.set_cell_state(1, center.x, center.y + 2 + 1, center.z)
        answer_board.set_cell_state(1, center.x, center.y + 2, center.z + 1)
        answer_board.set_cell_state(1, center.x - 1, center.y + 2, center.z)
        answer_board.set_cell_state(1, center.x, center.y + 2 - 1, center.z)
        answer_board.set_cell_state(1, center.x, center.y + 2, center.z - 1)

        answer_board.set_cell_state(1, center.x + 1, center.y, center.z + 2)
        answer_board.set_cell_state(1, center.x, center.y + 1, center.z + 2)
        answer_board.set_cell_state(1, center.x, center.y, center.z + 2 + 1)
        answer_board.set_cell_state(1, center.x - 1, center.y, center.z + 2)
        answer_board.set_cell_state(1, center.x, center.y - 1, center.z + 2)
        answer_board.set_cell_state(1, center.x, center.y, center.z + 2 - 1)

        answer_board.set_cell_state(1, center.x - 2 + 1, center.y, center.z)
        answer_board.set_cell_state(1, center.x - 2, center.y + 1, center.z)
        answer_board.set_cell_state(1, center.x - 2, center.y, center.z + 1)
        answer_board.set_cell_state(1, center.x - 2 - 1, center.y, center.z)
        answer_board.set_cell_state(1, center.x - 2, center.y - 1, center.z)
        answer_board.set_cell_state(1, center.x - 2, center.y, center.z - 1)

        answer_board.set_cell_state(1, center.x + 1, center.y - 2, center.z)
        answer_board.set_cell_state(1, center.x, center.y - 2 + 1, center.z)
        answer_board.set_cell_state(1, center.x, center.y - 2, center.z + 1)
        answer_board.set_cell_state(1, center.x - 1, center.y - 2, center.z)
        answer_board.set_cell_state(1, center.x, center.y - 2 - 1, center.z)
        answer_board.set_cell_state(1, center.x, center.y - 2, center.z - 1)
        
        answer_board.set_cell_state(1, center.x + 1, center.y, center.z - 2)
        answer_board.set_cell_state(1, center.x, center.y + 1, center.z - 2)
        answer_board.set_cell_state(1, center.x, center.y, center.z - 2 + 1)
        answer_board.set_cell_state(1, center.x - 1, center.y, center.z - 2)
        answer_board.set_cell_state(1, center.x, center.y - 1, center.z - 2)
        answer_board.set_cell_state(1, center.x, center.y, center.z - 2 - 1)

        self.compare_answer(test_board, answer_board)
