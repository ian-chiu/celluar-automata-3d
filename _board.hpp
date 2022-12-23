#pragma once

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <vector>

class Board {
 public:
    Board(int side, pybind11::object rule);
    void update();
    void randomise(float radius, float density);
    void randomise(pybind11::object rule);
    void render();
    void clear();
    void setRule(pybind11::object rule);
    void setSide(size_t side);
    int getCellState(size_t x, size_t y, size_t z) const;
    void setCellState(int state, size_t x, size_t y, size_t z);
    inline pybind11::object getRule() const { return mRule; }
    inline size_t getQuadCount() const { return mQuadCount; }
    inline size_t getSide() const { return mSide; }
    inline size_t getSize() const { return mSide * mSide * mSide; }

 public:
    std::vector<float> mVertexBuffer;

 private:
    enum class Face { BACK, FRONT, RIGHT, LEFT, UP, DOWN, COUNT };
    struct Rule {
        std::unordered_set<int> spawn;
        std::unordered_set<int> survival;
        uint32_t maxState;
        std::string neighbor;
    };

 private:
    void calculateGreedyMeshes();
    int applyRule(int neighborCount, int cellState);
    int countNeighbors(int index);
    int getIndex(int x, int y, int z);
    std::vector<int> getCoordinate(int index);
    void setRuleBuffer(pybind11::object rule);
    size_t coordToIndex(size_t x, size_t y, size_t z) const;

 private:
    int mSide;
    size_t mQuadCount;
    pybind11::object mRule;
    Rule mRuleBuffer;
    std::vector<int> mCells;
    std::vector<int> mCellsBuffer;
};
