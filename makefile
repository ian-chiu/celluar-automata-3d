CXX := c++
SRCS := _board.cpp
TARGET := _board$(shell python3-config --extension-suffix)
INCLUDES := $(shell python3 -m pybind11 --includes) $(shell python3-config --includes)
CXXFLAGS := -O3 -Wall -shared -std=c++11 -fPIC $(INCLUDES)

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) $^ -o $(TARGET)

.PHONY: test
test: $(TARGET)
	python3 -m pytest

.PHONY: clean
clean:
	rm -rf $(TARGET) __pycache__ .pytest_cache imgui.ini
