# QuSudoku: SUDOKU SOLVER USING DISCRETE QUANTUM MODEL
## iQuHACK 2021! TEAM SYCAMORE 
### Rishabh Singhal, Niranjan P N, Rohit K S S Vuppala 

## Introduction
<p> Solving $n x n$ Sudoku is shown to NP Complete problem. NP-completeness is a concept that applies to decision problems with variable input size, so that it can be analyzed the running time of an algorithm as that input size grows asymptotically. We are using DQM model to solve these sudoku problem.

<p> The general problem of solving Sudoku puzzles on $n^{2} × n^{2}$ grids of $n×n$ blocks is known to be NP-complete.
 
## Description
* Constraints of Sudoku - 
        1. Each row must have a unique value
        2. Ecah column must have a unique value
        3. Each sub-square must have a unique value
        4. Each cell can have only one value

* We model the sudoku probelm as mathematical graph structure. Now we will color this graph, using n colors. The new constraints then are - 
        1. Node sharing an edge cannot share same color
        2. Each node will have exactly one color
        3. Some nodes have pre-defined color

* Constraint a takes care of constraint 1,2 and 3.
* Constraint b takes care of constraint 4.
* DQM solver automatically implement one-hot constraint. Thus resultant constraints now are a and c.

* The algorithm presented here can be applied on any general graph coloring problem.

## References
* "NP complete – Sudoku" (PDF). Imai.is.su-tokyo.ac.jp. Retrieved 20 October 2013.
* https://arxiv.org/pdf/1302.5843.pdf
