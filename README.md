
#  CiberRato Robot Simulation – RMI Assignment 1

This project is based on the **CiberRato Robot Simulation Environment** developed at the University of Aveiro.  
It simulates autonomous robot agents navigating mazes, solving tasks such as control, mapping, and planning.

Our implementation was developed as part of **RMI – Assignment 1** and consists of three main challenges:

----------

##  Challenges

###  Control Challenge

-   **Goal:** Make the robot follow a path using only the **line sensor**.
    
-   **Approach:** Implemented a **purely reactive agent** that reads sensor data and makes decisions conditionally (e.g., turn left/right depending on line sensor input).
    

----------

###  Mapping Challenge

-   **Goal:** Explore an **unknown maze** and build its map using the **line sensor, GPS, and compass**.
    
-   **Approach:**
    
    -   Created a `Vertice` class to represent intersections (with coordinates and adjacency data).
        
    -   Implemented **intersection detection** and updated an adjacency dictionary.
        
    -   Used **wandering logic** (checking left, right, front) and turning strategies when no line was detected.
        
    -   Stored the explored graph in a matrix structure for later use.
        

----------

###  Planning Challenge

-   **Goal:** Locate multiple **target spots** in the maze and compute the **shortest closed path** visiting all of them, starting and ending at the robot’s initial position.
    
-   **Approach:**
    
    -   Extended the mapping code to include **target intersections**.
        
    -   Implemented a **cost calculation function** for paths.
        
    -   Used **Dijkstra’s algorithm** and path cost evaluation across all permutations of target orders.
        
    -   Exported the shortest path using a function that writes robot positions to a file every 2 units.
        

----------

##  Repository Contents

-   `simulator/` – CiberRato simulator source code
    
-   `viewer/` – Visualization tool
    
-   `logplayer/` – Log playback utility
    
-   `GUISample/` – Graphical robot agent (C++)
    
-   `robsample/` – Robot agent (C)
    
-   `jClient/` – Robot agent (Java)
    
-   `pClient/` – Robot agent (Python)
    
-   `Labs/` – Example labyrinths from past competitions
    
-   `startAll` – Script to run simulator, visualizer, and 5 GUI samples
    
-   `startSimViewer` – Script to run simulator and viewer
    
-   `rmi_assignment/` – Our implementation for the three challenges
    

----------

##  Installation

The project was developed and tested on **Ubuntu 20.04** with:

-   **gcc/g++ 9.3.0**
    
-   **Qt 5.12.8**
    
-   **CMake**
    

### Install dependencies:

`sudo apt-get install build-essential cmake qt5-default qtmultimedia5-dev` 

### Build:

`mkdir build cd build
cmake ..
make` 

----------

##  Running the Simulation

To launch the simulator, viewer, and sample C++ agent:

`./startAll` 

Or, just simulator + viewer:

`./startSimViewer` 

----------

##  Authors
-   **Nuno Cunha** (98124)

-   **Pedro Lima** (97860)
    

    

Based on work by:  
Nuno Lau, Artur C. Pereira, Andreia Melo, António Neves, João Figueiredo, Miguel Rodrigues, Eurico Pedrosa (University of Aveiro / IEETA)