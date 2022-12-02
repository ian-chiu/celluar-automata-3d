#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>

namespace py = pybind11;

class Board {
 public:
    Board(int side, py::object rule, float evolveTime = 0.3f);
    void update();
    void randomise();
    void render();
    void setRule(py::object rule);
    size_t getQuadCount() const;

 public:
    py::array_t<float> mVertexBuffer;
    std::vector<float> mVertices;
    size_t mVertexBufferIndex;

 private:
    enum class Face { SOUTH, NORTH, EAST, WEST, TOP, BOTTOM, COUNT };

 private:
    void calculateGreedyMeshes();
    int applyRule(int neighborCount, int cellState);
    int countNeighbors(int index);
    int getIndex(int x, int y, int z);
    std::vector<int> getCoordinate(int index);
    void resetVertexBuffer();

 private:
    int mSide;
    float mEvolveTime;
    size_t mQuadCount;
    py::object mRule;
    py::object mCubeModel;
    std::vector<int> mCells;
    std::vector<int> mCellsBuffer;
    std::vector<std::vector<float>> mFaceNormals{
        {0.0f, 1.0f, 0.0f},  {0.0f, -1.0f, 0.0f}, {1.0f, 0.0f, 0.0f},
        {-1.0f, 0.0f, 0.0f}, {1.0f, 0.0f, 0.0f},
    };
};
