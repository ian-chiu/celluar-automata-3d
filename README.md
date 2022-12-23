# celluar-automata-3d

A software to simulate and visualize 3D cellular automata
![](https://i.imgur.com/Jlvoc9R.gif)

This is a homework project for [Numerical Software Development(NYCU 2022 autumn)](https://yyc.solvcon.net/en/latest/nsd/schedule/22au_nycu/schedule.html)

## Basic Information

Cellular Automata Definition from Tech Target:
> A cellular automation is a collection of cells arranged in a grid of specified shape, such that each cell changes state as a function of time, according to a defined set of rules driven by the states of neighboring cells.

### Cell Rules

Cell rules can be represented by:
**Survival / Spawn / State / Neighbor**

#### Survival

A list of acceptable numbers of neighbors that are alive (in state 1) to keep a cell survived (stay in state 1). If the number does not match any in the list, the cell start dying (its state start increasing every tick). If a cell's state is greater than or equal to its maximum state, it died (back to state 0).

#### Spawn

A list of acceptable numbers of neighbors that are alive (in state 1) to spawn a new cell. If a cell is empty (in state 0) and the number matches any in the list, the cell get spawned (go from state 0 to 1).

#### State

The maximum number of state a cell can have. If a cell's state is greater than or equal to this number, then it died (back to state 0).

#### Neighbor

There are two kinds of neighbor, Moore(M) and Von Neumann(VN). Moore is like a rubik cube, the cell at the center has 26 neighbors. Von Neumann has only 4 neighbors, top, down, front and back.

## Install and Execute

### Install pybind11

```bash
pip install pybind11
```

### Install python requirements

```bash
pip install -r requirements.txt
```

### Build the python wrapper for our C++ code

```bash
make
```

### Execute the program

```bash
./cellular_automata_3d.py
```

## Help

### General

* R: randomise by factors in settings
* E: erase all cells
* Spacebar: pause/continue simulation
* F: update one step forward
* Q/Esc: quit the application
* Different rules can be selected in Rules section
* You can add your own rules to rules.json file

### Camera

There are two camera controllers: Free and Orbit Controller
* C: toggle between two controllers

While in free mode:
* Pressed mouse right and move to rotate the camera
* WASD: move the camera
* Scroll mouse wheel to change the moving speed

While in orbit mode:
* Pressed mouse right and move to rotate the camera
* Scroll mouse wheel to zoom in/out

## Optimization
* Use multithreading (std::async) to speed up cell state calculation.
* Use greedy meshing algorithm to turn seperated cell meshes (cubes)  into connected quads. (reduce rendering time)
* Use batch rendering to reduce draw calls
