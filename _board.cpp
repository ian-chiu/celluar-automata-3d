#include "./_board.hpp"

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include <algorithm>
#include <cstring>
#include <iostream>
#include <memory>
#include <unordered_set>

namespace py = pybind11;
using namespace pybind11::literals;

PYBIND11_MAKE_OPAQUE(std::vector<int>);
PYBIND11_MAKE_OPAQUE(std::vector<float>);

py::object glm = py::module_::import("moderngl");
py::object Rule = py::module_::import("rule").attr("Rule");
py::object Renderer = py::module_::import("engine.renderer").attr("Renderer");
const int MAX_BUFFER_SIZE =
    py::module_::import("engine.renderer").attr("MAX_BUFFER_SIZE").cast<int>();
py::object Model = py::module_::import("engine.model").attr("Model");
py::object PhongMaterial =
    py::module_::import("engine.material").attr("PhongMaterial");
py::object BoxGeometry =
    py::module_::import("engine.geometry").attr("BoxGeometry");

static const std::vector<std::vector<int>> mooreOffsets{
    {1, -1, -1}, {1, -1, 0},  {1, -1, 1},  {1, 0, -1},  {1, 0, 0},
    {1, 0, 1},   {1, 1, -1},  {1, 1, 0},   {1, 1, 1},   {-1, -1, -1},
    {-1, -1, 0}, {-1, -1, 1}, {-1, 0, -1}, {-1, 0, 0},  {-1, 0, 1},
    {-1, 1, -1}, {-1, 1, 0},  {-1, 1, 1},  {0, -1, -1}, {0, -1, 0},
    {0, -1, 1},  {0, 1, -1},  {0, 1, 0},   {0, 1, 1},   {0, 0, 1},
    {0, 0, -1}};

static const std::vector<std::vector<int>> vnOffsets{
    {1, 0, 0}, {-1, 0, 0}, {0, 1, 0}, {0, -1, 0}, {0, 0, 1}, {0, 0, -1}};

Board::Board(int side, py::object rule, float evolveTime)
    : mSide(side),
      mEvolveTime(evolveTime),
      mRule(rule),
      mCells(side * side * side),
      mCellsBuffer(side * side * side),
      mVertexBuffer(MAX_BUFFER_SIZE),
      mVertexBufferIndex(0) {
    py::object material =
        PhongMaterial("color"_a = py::make_tuple(0.5, 0.8, 0.1));
    mCubeModel = Model(BoxGeometry(), material);
    randomise(rule);
}

void Board::update() {
    for (size_t index = 0; index < mCells.size(); index++) {
        int neighborCount = countNeighbors(index);
        mCellsBuffer[index] = applyRule(neighborCount, mCells[index]);
    }
    std::swap(mCellsBuffer, mCells);
    resetVertexBuffer();
    calculateGreedyMeshes();
}

void Board::render() {
    py::object drawModel = Renderer.attr("draw_model");
    for (size_t index = 0; index < mCells.size(); index++) {
        if (mCells[index] == 0) {
            continue;
        }
        py::list pos;
        std::vector<int> coord = getCoordinate(index);
        for (int value : coord) {
            pos.append(value - mSide / 2.0f);
        }
        drawModel(mCubeModel, pos);
    }
}

void Board::clear() {
    resetVertexBuffer();
    std::fill(mCells.begin(), mCells.end(), 0);
    std::fill(mCellsBuffer.begin(), mCellsBuffer.end(), 0);
}

void Board::setSide(size_t side) {
    mSide = side;
    clear();
}

void Board::setRule(py::object rule) {
    mRule = rule;
    clear();
    randomise(rule);
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

void Board::resetVertexBuffer() {
    float* data = mVertexBuffer.mutable_data(0);
    std::memset(data, 0, sizeof(float) * MAX_BUFFER_SIZE);
}

int Board::applyRule(int neighborCount, int cellState) {
    py::set spawn = mRule.attr("spawn");
    py::set survival = mRule.attr("survival");
    int maxState = mRule.attr("max_state").cast<int>();
    if (cellState == 0 && spawn.contains(neighborCount)) {
        cellState = 1;
    } else if (cellState > 1 ||
               (cellState == 1 && !survival.contains(neighborCount))) {
        cellState++;
        if (cellState >= maxState) {
            cellState = 0;
        }
    }
    return cellState;
}

int Board::countNeighbors(int index) {
    int neighbors = 0;
    int side = mSide;
    std::string neighborType = mRule.attr("neighbor").cast<std::string>();
    const auto& offsets = neighborType == "M" ? mooreOffsets : vnOffsets;
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
    mVertexBufferIndex = 0;
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

                    int index = mVertexBufferIndex;
                    int uvs[4][2] = {{0, 0}, {1, 0}, {1, 1}, {0, 1}};
                    for (int i = 0; i < 4; i++) {
                        // positions
                        mVertexBuffer.mutable_at(index) =
                            positions[i][0] - (mSide / 2.0f + 0.5f);
                        mVertexBuffer.mutable_at(index + 1) =
                            positions[i][1] - (mSide / 2.0f + 0.5f);
                        mVertexBuffer.mutable_at(index + 2) =
                            positions[i][2] - (mSide / 2.0f + 0.5f);

                        // uvs
                        mVertexBuffer.mutable_at(index + 3) = uvs[i][0];
                        mVertexBuffer.mutable_at(index + 4) = uvs[i][1];

                        // normal
                        mVertexBuffer.mutable_at(index + 5) = 1.0f;
                        mVertexBuffer.mutable_at(index + 6) = 0.0f;
                        mVertexBuffer.mutable_at(index + 7) = 0.0f;

                        // color
                        mVertexBuffer.mutable_at(index + 8) = 0.0f;
                        mVertexBuffer.mutable_at(index + 9) = 0.3f;
                        mVertexBuffer.mutable_at(index + 10) = 1.0f;
                        mVertexBuffer.mutable_at(index + 11) = 1.0f;

                        index += 12;
                    }
                    mVertexBufferIndex = index;
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
        .def(py::init<int, py::object, float>())
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
        .def_readonly("vertex_buffer", &Board::mVertexBuffer);
}
