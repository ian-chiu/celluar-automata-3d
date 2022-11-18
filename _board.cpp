#include <algorithm>
#include <memory>
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl_bind.h>
#include <pybind11/stl.h>

#include <iostream>

PYBIND11_MAKE_OPAQUE(std::vector<int>);

namespace py = pybind11;
py::object Rule = py::module_::import("rule").attr("Rule");

static const std::vector<std::vector<int>> mooreOffsets{
    {1, -1, -1}, {1, -1, 0}, {1, -1, 1},
    {1, 0, -1}, {1, 0, 0}, {1, 0, 1},
    {1, 1, -1}, {1, 1, 0}, {1, 1, 1},
    {-1, -1, -1}, {-1, -1, 0}, {-1, -1, 1},
    {-1, 0, -1}, {-1, 0, 0}, {-1, 0, 1},
    {-1, 1, -1}, {-1, 1, 0}, {-1, 1, 1},
    {0, -1, -1}, {0, -1, 0}, {0, -1, 1},
    {0, 1, -1}, {0, 1, 0}, {0, 1, 1},
    {0, 0, 1}, {0, 0, -1}
};

static const std::vector<std::vector<int>> vnOffsets{
    {1, 0, 0}, {-1, 0, 0},
    {0, 1, 0}, {0, -1, 0},
    {0, 0, 1}, {0, 0, -1}
};

class Board
{
public:
    Board(int side, py::object rule)
        : mSide(side)
        , mRule(rule)
        , mCells(side * side * side)
    {
        randomise();
    }

    void update(float deltaTime)
    {
        std::vector<int> updatedCells(mCells.size());
        for (int index = 0; index < mCells.size(); index++) {
            int neighborCount = countNeighbors(index);
            updatedCells[index] = applyRule(neighborCount, mCells[index]);
        }
        mCells = std::move(updatedCells);
        calculateGreedyMeshes();
    }


    void randomise()
    {
        std::fill(mCells.begin(), mCells.end(), 0);
        float density = mRule.attr("initial_density").cast<float>();
        float radius = mRule.attr("initial_radius").cast<float>();
        float side = mSide;
        for (int index = 0; index < mCells.size(); index++) {
            std::vector<int> coordinate = getCoordinate(index);
            if ((rand() % 100) / 100.0f < density
                    && coordinate[0] < side / 2 + radius * side / 2
                    && coordinate[0] > side / 2 - radius * side / 2
                    && coordinate[1] < side / 2 + radius * side / 2
                    && coordinate[1] > side / 2 - radius * side / 2
                    && coordinate[2] < side / 2 + radius * side / 2
                    && coordinate[2] > side / 2 - radius * side / 2) {
                mCells[index] = 1;
            }
        }
        calculateGreedyMeshes();
    }

    int getIndex(int x, int y, int z)
    {
        return (z * mSide * mSide) + (y * mSide) + x;
    }

    std::vector<int> getCoordinate(int index)
    {
        int z = index / (mSide * mSide);
        index -= (z * mSide * mSide);
        int y = index / mSide;
        int x = index % mSide;
        return { x, y, z };
    }

public:
    int mSide;
    py::object mRule;
    std::vector<int> mCells;
    std::vector<int> mGreedyMeshes;

private:
    void calculateGreedyMeshes()
    {
        mGreedyMeshes.clear();
        std::vector<bool> visited(mCells.size(), false);
        for (int x = 0; x < mSide; x++) {
            for (int y = 0; y < mSide; y++) {
                for (int z = 0; z < mSide; z++) {
                    if (visited[getIndex(x, y, z)]) {
                        continue;
                    }
                    visited[getIndex(x, y, z)] = true;
                    int startX = x, startY = y, startZ = z;
                    int endX = x, endY = y, endZ = z;

                    while (endX < mSide) {
                        int newEndX = endX + 1;
                        int index = getIndex(newEndX, y, z);
                        if (visited[index] || mCells[index] == 0) {
                            break;
                        }
                        visited[index] = true;
                        endX = newEndX;
                    }

                    while (endY < mSide) {
                        int newEndY = endY + 1;
                        bool usable = true;
                        for (int dx = startX; dx <= endX; dx++) {
                            int index = getIndex(dx, newEndY, z);
                            if (index >= mCells.size() || visited[index]
                                    || mCells[index] == 0) {
                                usable = false;
                                break;
                            }
                        }
                        if (!usable) {
                            break;
                        }
                        for (int dx = startX; dx <= endX; dx++) {
                            visited[getIndex(dx, newEndY, z)] = true;
                        }
                        endY = newEndY;
                    }

                    while (endZ < mSide) {
                        int newEndZ = endZ + 1;
                        bool usable = true;
                        for (int dx = startX; dx <= endX; dx++) {
                            for (int dy = startY; dy <= endY; dy++) {
                                int index = getIndex(dx, dy, newEndZ);
                                if (index >= mCells.size() || visited[index]
                                        || mCells[index] == 0) {
                                    usable = false;
                                    break;
                                }
                            }
                            if (!usable) {
                                break;
                            }
                        }
                        if (!usable) {
                            break;
                        }
                        for (int dx = startX; dx <= endX; dx++) {
                            for (int dy = startY; dy <= endY; dy++) {
                                visited[getIndex(dx, dy, newEndZ)] = true;
                            }
                        }
                        endZ = newEndZ;
                    }
                    mGreedyMeshes.insert(mGreedyMeshes.end(),
                        {startX, startY, startZ, endX, endY, endZ});
                }
            }
        }
    }

    int applyRule(int neighborCount, int cellState)
    {
        py::set spawn = mRule.attr("spawn");
        py::set survival = mRule.attr("survival");
        int maxState = mRule.attr("max_state").cast<int>();
        if (cellState == 0 && spawn.contains(neighborCount)) {
            cellState = 1;
        }
        else if (cellState > 1 || (cellState == 1 && !survival.contains(
                neighborCount))) {
            cellState++;
            if (cellState >= maxState) {
                cellState = 0;
            }
        }
        return cellState;
    }

    int countNeighbors(int index)
    {
        int neighbors = 0;
        int side = mSide;
        std::string neighborType = mRule.attr("neighbor").cast<std::string>();
        const auto &offsets = neighborType == "M" ? mooreOffsets : vnOffsets;
        const auto coordinate = getCoordinate(index);
        for (const auto &offset : offsets) {
            int offX = coordinate[0] + offset[0];
            int offY = coordinate[1] + offset[1];
            int offZ = coordinate[2] + offset[2];
            if (offX >= side) {
                offX = 0;
            }
            else if (offX < 0) {
                offX = side - 1;
            }
            if (offY >= side) {
                offY = 0;
            }
            else if (offY < 0) {
                offY = side - 1;
            }
            if (offZ >= side) {
                offZ = 0;
            }
            else if (offZ < 0) {
                offZ = side - 1;
            }
            neighbors += (mCells[getIndex(offX, offY, offZ)] == 1);
        }
        neighbors -= (mCells[index] == 1);
        return neighbors;
    }
};

PYBIND11_MODULE(_board, m)
{
    py::bind_vector<std::vector<int>>(m, "VectorInt");
    py::class_<Board>(m, "Board")
        .def(py::init<int, py::object>())
        .def("update", &Board::update)
        .def("get_coordinate", &Board::getCoordinate)
        .def_readwrite("side", &Board::mSide)
        .def_readonly("cells", &Board::mCells)
        .def_readonly("greedy_meshes", &Board::mGreedyMeshes);
}
