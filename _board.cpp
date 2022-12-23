#include "./_board.hpp"

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include <algorithm>
#include <cmath>
#include <cstring>
#include <future>
#include <iostream>
#include <memory>
#include <queue>

namespace py = pybind11;
using namespace pybind11::literals;

PYBIND11_MAKE_OPAQUE(std::vector<int>);
PYBIND11_MAKE_OPAQUE(std::vector<float>);

py::object glm = py::module_::import("moderngl");
py::object Rule = py::module_::import("rule").attr("Rule");
py::object Renderer = py::module_::import("engine.renderer").attr("Renderer");
py::object drawBatch = Renderer.attr("draw_batch");
const size_t MAX_BUFFER_SIZE =
    py::module_::import("engine.renderer").attr("MAX_BUFFER_SIZE").cast<int>();

static const std::vector<std::vector<int>> mooreOffsets{
    {1, -1, -1}, {1, -1, 0},  {1, -1, 1},  {1, 0, -1},  {1, 0, 0},
    {1, 0, 1},   {1, 1, -1},  {1, 1, 0},   {1, 1, 1},   {-1, -1, -1},
    {-1, -1, 0}, {-1, -1, 1}, {-1, 0, -1}, {-1, 0, 0},  {-1, 0, 1},
    {-1, 1, -1}, {-1, 1, 0},  {-1, 1, 1},  {0, -1, -1}, {0, -1, 0},
    {0, -1, 1},  {0, 1, -1},  {0, 1, 0},   {0, 1, 1},   {0, 0, 1},
    {0, 0, -1}};

static const std::vector<std::vector<int>> vnOffsets{
    {1, 0, 0}, {-1, 0, 0}, {0, 1, 0}, {0, -1, 0}, {0, 0, 1}, {0, 0, -1}};

Board::Board(int side, py::object rule)
    : mSide(side),
      mQuadCount(0),
      mRule(rule),
      mCells(side * side * side),
      mCellsBuffer(side * side * side) {
    setRuleBuffer(rule);
    mVertexBuffer.reserve(MAX_BUFFER_SIZE);
}

void Board::update() {
    static std::queue<std::future<void>> futures;
    auto asyncTask = [&](size_t divider) {
        for (size_t i = 0; i < getSize() / mSide; i++) {
            size_t index = getSize() / mSide * divider + i;
            int neighborCount = countNeighbors(index);
            mCellsBuffer[index] = applyRule(neighborCount, mCells[index]);
        }
    };
    for (size_t divider = 0; divider < mSide; divider++) {
        futures.emplace(std::async(std::launch::async, asyncTask, divider));
    }
    while (!futures.empty()) {
        futures.front().wait();
        futures.pop();
    }
    std::swap(mCellsBuffer, mCells);
    calculateGreedyMeshes();
}

void Board::render() {
    int batchCount = mVertexBuffer.size() / MAX_BUFFER_SIZE;
    for (int count = 0; count < batchCount; count++) {
        drawBatch(py::memoryview::from_memory(
            mVertexBuffer.data() + count * MAX_BUFFER_SIZE,
            sizeof(float) * MAX_BUFFER_SIZE));
    }
    int remain = mVertexBuffer.size() - batchCount * MAX_BUFFER_SIZE;
    if (remain > 0) {
        drawBatch(py::memoryview::from_memory(
            mVertexBuffer.data() + batchCount * MAX_BUFFER_SIZE,
            sizeof(float) * remain));
    }
}

void Board::clear() {
    mVertexBuffer.clear();
    mCells.resize(mSide * mSide * mSide, 0);
    mCellsBuffer.resize(mSide * mSide * mSide, 0);
    std::fill(mCells.begin(), mCells.end(), 0);
    std::fill(mCellsBuffer.begin(), mCellsBuffer.end(), 0);
}

void Board::setSide(size_t side) {
    mSide = side;
    clear();
    randomise(mRule);
}

void Board::setRule(py::object rule) {
    mRule = rule;
    setRuleBuffer(rule);
    clear();
    randomise(rule);
}

size_t Board::coordToIndex(size_t x, size_t y, size_t z) const {
    return x + mSide * (y + mSide * z);
}

int Board::getCellState(size_t x, size_t y, size_t z) const {
    return mCells[coordToIndex(x, y, z)];
}

void Board::setCellState(int state, size_t x, size_t y, size_t z) {
    mCells[coordToIndex(x, y, z)] = state;
}

void Board::randomise(float radius, float density) {
    float side = mSide;
    for (size_t index = 0; index < mCells.size(); index++) {
        std::vector<int> coordinate = getCoordinate(index);
        if ((rand() % 100) / 100.0f < density &&
            coordinate[0] < side / 2 + radius * side / 2 &&
            coordinate[0] > side / 2 - radius * side / 2 &&
            coordinate[1] < side / 2 + radius * side / 2 &&
            coordinate[1] > side / 2 - radius * side / 2 &&
            coordinate[2] < side / 2 + radius * side / 2 &&
            coordinate[2] > side / 2 - radius * side / 2) {
            mCells[index] = 1;
        }
    }
    calculateGreedyMeshes();
}

void Board::randomise(py::object rule) {
    float density = rule.attr("initial_density").cast<float>();
    float radius = rule.attr("initial_radius").cast<float>();
    randomise(radius, density);
}

int Board::getIndex(int x, int y, int z) {
    return (z * mSide * mSide) + (y * mSide) + x;
}

std::vector<int> Board::getCoordinate(int index) {
    int z = index / (mSide * mSide);
    index -= (z * mSide * mSide);
    int y = index / mSide;
    int x = index % mSide;
    return {x, y, z};
}

void Board::setRuleBuffer(py::object rule) {
    mRuleBuffer.spawn = mRule.attr("spawn").cast<std::unordered_set<int>>();
    mRuleBuffer.survival =
        mRule.attr("survival").cast<std::unordered_set<int>>();
    mRuleBuffer.maxState = mRule.attr("max_state").cast<uint32_t>();
    mRuleBuffer.neighbor = mRule.attr("neighbor").cast<std::string>();
}

int Board::applyRule(int neighborCount, int cellState) {
    if (cellState == 0 && mRuleBuffer.spawn.count(neighborCount)) {
        cellState = 1;
    } else if (cellState > 1 || (cellState == 1 &&
                                 !mRuleBuffer.survival.count(neighborCount))) {
        cellState++;
        if (cellState >= mRuleBuffer.maxState) {
            cellState = 0;
        }
    }
    return cellState;
}

int Board::countNeighbors(int index) {
    int neighbors = 0;
    int side = mSide;
    const auto& offsets =
        mRuleBuffer.neighbor == "M" ? mooreOffsets : vnOffsets;
    const auto coordinate = getCoordinate(index);
    for (const auto& offset : offsets) {
        int offX = coordinate[0] + offset[0];
        int offY = coordinate[1] + offset[1];
        int offZ = coordinate[2] + offset[2];
        if (offX >= side) {
            offX = 0;
        } else if (offX < 0) {
            offX = side - 1;
        }
        if (offY >= side) {
            offY = 0;
        } else if (offY < 0) {
            offY = side - 1;
        }
        if (offZ >= side) {
            offZ = 0;
        } else if (offZ < 0) {
            offZ = side - 1;
        }
        neighbors += (mCells[getIndex(offX, offY, offZ)] == 1);
    }
    neighbors -= (mCells[index] == 1);
    return neighbors;
}

void Board::calculateGreedyMeshes() {
    mVertexBuffer.clear();
    mQuadCount = 0;

    // sweep over each axis (X, Y, Z)
    for (int d = 0; d < 3; d++) {
        int i, j, k, l, w, h;
        int u = (d + 1) % 3;
        int v = (d + 2) % 3;
        int x[3] = {0};
        int q[3] = {0};

        std::vector<bool> mask(mSide * mSide);
        q[d] = 1;  // determine the searching direction

        // check each slice one at a time
        for (x[d] = -1; x[d] < mSide;) {
            // compute the mask
            int n = 0;
            for (x[v] = 0; x[v] < mSide; x[v]++) {
                for (x[u] = 0; x[u] < mSide; x[u]++) {
                    bool blockCurrent = false;
                    if (x[d] >= 0) {
                        blockCurrent = mCells[getIndex(x[0], x[1], x[2])] > 0;
                    }
                    bool blockCompare = false;
                    if (x[d] < mSide - 1) {
                        blockCompare =
                            mCells[getIndex(x[0] + q[0], x[1] + q[1],
                                            x[2] + q[2])] > 0;
                    }
                    mask[n++] = blockCurrent != blockCompare;
                }
            }
            x[d]++;

            bool isBackFace = x[d] % 2;
            Face face;
            if (d == 0) {
                face = isBackFace ? Face::LEFT : Face::RIGHT;
            } else if (d == 1) {
                face = isBackFace ? Face::DOWN : Face::UP;
            } else if (d == 2) {
                face = isBackFace ? Face::BACK : Face::FRONT;
            }

            // Generate mesh for mask using lexicographic ordering
            n = 0;
            for (j = 0; j < mSide; j++) {
                for (i = 0; i < mSide;) {
                    if (!mask[n]) {
                        i++;
                        n++;
                        continue;
                    }

                    // Compute width
                    for (w = 1; mask[n + w] && i + w < mSide; w++) {
                        // null statement
                    }

                    // Compute height
                    bool done = false;
                    for (h = 1; j + h < mSide; h++) {
                        for (k = 0; k < w; k++) {
                            if (!mask[n + k + h * mSide]) {
                                done = true;
                                break;
                            }
                        }
                        if (done) {
                            break;
                        }
                    }

                    // Add quad
                    x[u] = i;
                    x[v] = j;

                    int du[3] = {0};
                    du[u] = w;
                    int dv[3] = {0};
                    dv[v] = h;

                    int tl[3] = {x[0], x[1], x[2]};
                    int tr[3] = {x[0] + du[0], x[1] + du[1], x[2] + du[2]};
                    int br[3] = {x[0] + du[0] + dv[0], x[1] + du[1] + dv[1],
                                 x[2] + du[2] + dv[2]};
                    int bl[3] = {x[0] + dv[0], x[1] + dv[1], x[2] + dv[2]};

                    int* positions[4] = {bl, br, tr, tl};
                    if (isBackFace) {
                        std::swap(positions[1], positions[3]);
                    }

                    int uvs[4][2] = {{0, 0}, {1, 0}, {1, 1}, {0, 1}};
                    for (int i = 0; i < 4; i++) {
                        // positions
                        mVertexBuffer.push_back(positions[i][0] -
                                                (mSide / 2.0f + 0.5f));
                        mVertexBuffer.push_back(positions[i][1] -
                                                (mSide / 2.0f + 0.5f));
                        mVertexBuffer.push_back(positions[i][2] -
                                                (mSide / 2.0f + 0.5f));

                        mVertexBuffer.push_back(uvs[i][0]);
                        mVertexBuffer.push_back(uvs[i][1]);

                        // normal
                        float normal[3] = {0};
                        if (face == Face::RIGHT) {
                            normal[0] = 1;
                            normal[1] = 0;
                            normal[2] = 0;
                        } else if (face == Face::LEFT) {
                            normal[0] = -1;
                            normal[1] = 0;
                            normal[2] = 0;
                        } else if (face == Face::UP) {
                            normal[0] = 0;
                            normal[1] = 1;
                            normal[2] = 0;
                        } else if (face == Face::DOWN) {
                            normal[0] = 0;
                            normal[1] = -1;
                            normal[2] = 0;
                        } else if (face == Face::FRONT) {
                            normal[0] = 0;
                            normal[1] = 0;
                            normal[2] = 1;
                        } else {
                            normal[0] = 0;
                            normal[1] = 0;
                            normal[2] = -1;
                        }

                        mVertexBuffer.push_back(normal[0]);
                        mVertexBuffer.push_back(normal[1]);
                        mVertexBuffer.push_back(normal[2]);

                        // color
                        int rgb[3] = {0};
                        if (face == Face::RIGHT || face == Face::LEFT) {
                            rgb[0] = 244;
                            rgb[1] = 125;
                            rgb[2] = 126;
                        } else if (face == Face::UP || face == Face::DOWN) {
                            rgb[0] = 117;
                            rgb[1] = 236;
                            rgb[2] = 125;
                        } else {
                            rgb[0] = 128;
                            rgb[1] = 126;
                            rgb[2] = 250;
                        }

                        mVertexBuffer.push_back(rgb[0] / 255.0f);
                        mVertexBuffer.push_back(rgb[1] / 255.0f);
                        mVertexBuffer.push_back(rgb[2] / 255.0f);
                        mVertexBuffer.push_back(1.0f);
                    }
                    mQuadCount++;

                    // zero-out mask
                    for (l = 0; l < h; l++) {
                        for (k = 0; k < w; k++) {
                            mask[n + k + l * mSide] = false;
                        }
                    }

                    i += w;
                    n += w;
                }
            }
        }
    }
}

PYBIND11_MODULE(_board, m) {
    py::class_<Board>(m, "Board")
        .def(py::init<int, py::object>())
        .def("update", &Board::update)
        .def("render", &Board::render)
        .def("clear", &Board::clear)
        .def("randomise",
             [](Board& board, float radius, float density) {
                 board.randomise(radius, density);
             })
        .def("set_side", &Board::setSide)
        .def("get_side", &Board::getSide)
        .def("set_rule", &Board::setRule)
        .def("get_rule", &Board::getRule)
        .def("get_quad_count", &Board::getQuadCount)
        .def("get_cell_state", &Board::getCellState)
        .def("set_cell_state", &Board::setCellState)
        .def_readonly("vertex_buffer", &Board::mVertexBuffer);
}
