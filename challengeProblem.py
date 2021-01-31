
#    *********************************************************************
#    |                                                                   |                                                                    
#    |   iQuHACK2021                                                     |            
#    |                                                                   |        
#    |    TEAM - SYCAMORE                                                |  
#    |                                                                   |
#    |    AUTHORS -                                                      | 
#    |        Rishabh Singhal     : r.singhal.com@gmail.com              |
#    |        Niranjan P N        : niranjanpn.official@gmail.com        |
#    |        Rohit K S S Vuppala : rvuppal@okstate.edu                  |
#    |                                                                   |
#    ********************************************************************* 
    


'''
    This module is designed to solve the n*n SUDOKU probelm using Discrete Quadratic Model by converting into a variant of graph coloring problem

    Constraints of Sudoku - 
        1. Each row must have a unique value
        2. Ecah column must have a unique value
        3. Each sub-square must have a unique value
        4. Each cell can have only one value

    We model the sudoku probelm as mathematical graph structure. we will then color the graph, using n colors. 
    The new constraints then are - 
        a. Node sharing an edge cannot share same color
        b. Each node will have exactly one color
        c. Some nodes have pre-defined color
    
    Constraint a takes care of constraint 1,2 and 3.
    Constraint b takes care of constraint 4.
    DQM solver automatically implement one-hot constraint. Thus we are now concerned about constraint a and c.
'''


from dimod import DiscreteQuadraticModel
from dwave.system import LeapHybridDQMSampler
import networkx as nx
import dimod
import math
import os

def readFile(file_path):
    '''
        This method reads the text file which contains the Sudoku layout.
        
        Parameters:
            file_path : path of the text file where in sudoku problem is present.

        Returns:
            sudoku : 2D list which contains the content of text file viz. sudoku problem statement.
    '''

    file_content = open(file_path,"r")

    sudoku = []

    line = file_content.readline()
    while(line != ''):
        line = line.replace("\n",'')
        line = line.split(" ")
        sudoku.append(line)

        line = file_content.readline()
    
    return sudoku

def nodeMapping(global_row):
    '''
        This method maps the matrix representation({row,col}) of 2D array to node represenation of graph(numerical value) 

        Parameters:
            global_row : Size of the Sudoku. For n*n sudoku layout, this parameter is n

        Returns:
            node_dict : dictionary mapping (row,col) to numerical value 
    '''
    node_dict = {}
    global_col = global_row

    #keeps account of number of nodes currently present in graph
    node = 1

    for row in range(global_row):
        for col in range(global_col):
            node_dict[(row,col)] = node
            node += 1
    
    return node_dict

def graphModelling(global_row):
    '''
        This method models the generic layout of n*n sudoku as mathematical graph.

        When modelled as graph, each cell of a big sudoku square shares an edge with all other cells in that particular row and  column. Also, each cell shares an edge with every other in that particular sub-square.

        Parameters :
            global_row : Size of the Sudoku. For n*n sudoku layout, this parameter is n.

        Returns :
            G : networkx graph object, which represents the modelled graph

    '''

    G = nx.Graph()

    global_col = global_row

    #defining the dimensions of sub-squares
    local_row = int(math.sqrt(global_row))
    local_col = int(math.sqrt(global_row))

    #to map the matrix representation of sudoku to node represenation of graph
    node_dict = nodeMapping(global_row)

    for row_cell in range(global_row):
        for col_cell in range(global_col):

            #connect a cell to every other cell in its row 
            for target_col in range(col_cell+1,global_col):
                G.add_edge(node_dict[(row_cell,col_cell)],node_dict[(row_cell,target_col)])
            
            #connect a cell to every other cell in its column 
            for target_row in range(row_cell+1,global_row):
                G.add_edge(node_dict[(row_cell,col_cell)],node_dict[(target_row,col_cell)])

            #defining the range of rows and columns that are part of this particular sub-square             
            sub_square_row_index = row_cell//local_row
            sub_square_col_index = col_cell//local_col

            sub_square_row = range(sub_square_row_index*local_row, (sub_square_row_index+1)*local_row)
            sub_square_col = range(sub_square_col_index*local_col, (sub_square_col_index+1)*local_col)

            #connect each cell to every other cell in its sub-square
            for sub_row in sub_square_row:
                for sub_col in sub_square_col:
                    if(sub_row==row_cell and sub_col==col_cell):
                        continue
                    else:
                        G.add_edge(node_dict[(row_cell,col_cell)],node_dict[(sub_row,sub_col)])

    return G

def buildDQM(G, sudoku):
    '''
        This method builds the DQM based on Sudoku Constraints now modelled as Graph

        Parameters :
            G : networkx graph object, which represents the modelled graph
            sudoku : 2D list which contains the content of text file viz. sudoku problem statement.

        Returns :
            dqm : Discrete Quadratic Model object
    '''

    #number of colors required to color the graph
    num_colors = int(math.sqrt(len(G.nodes())))
    colors = range(num_colors)

    global_row = num_colors
    global_col = global_row

    #to map the matrix representation of sudoku to node represenation of graph
    node_dict = nodeMapping(global_row)

    dqm = DiscreteQuadraticModel()
    lagrange = 1000

    #adding the variables
    for p in G.nodes:
        dqm.add_variable(num_colors,label=p)

    #linear biasing
    for p in G.nodes:
        dqm.set_linear(p,colors)

    '''
        constraints:
        1. Nodes sharing an edge cannot share the same color
        2. Color of certain nodes are pre-defined
    '''

    #quadratic biasing for constraint 1
    for p0,p1 in G.edges:
        #penalising the case which violate constraint 1
        dqm.set_quadratic(p0,p1,{(c,c):lagrange for c in colors})

    #quadratic biasing for constraint 2
    color_list = list(colors)
    for i in range(global_row):
        for j in range(global_col):
            if(sudoku[i][j] == '*'):
                continue

            #penalize_color_list = list(colors)
            #penalize_color_list.remove(int(sudoku[i][j])-1)

            #finding the neighbouring nodes of the given node
            node = node_dict[(i,j)]
            node_neighbour_set = set()

            for edge in G.edges():
                if(node in edge):
                    node_neighbour_set.add(edge[0])
                    node_neighbour_set.add(edge[1])
            node_neighbour_set.remove(node)

            '''for node_neighbour in node_neighbour_set:
                for c1 in color_list:
                    for c2 in penalize_color_list:
                        dqm.set_quadratic(node,node_neighbour,{(c2,c1):lagrange})'''

            node_color = int(sudoku[i][j])-1
            for node_neighbour in node_neighbour_set:
                for c1 in color_list:
                    if(c1 == node_color):
                        continue
                    #favoring the case which agrees upon constraint 2
                    dqm.set_quadratic(node,node_neighbour,{(node_color,c1):0})

    return dqm

def solveSudoku(dqm, G):
    '''
        This method solves the sudoku and also verify the result

        Parameters:
            dqm : Discrete Quadratic Model object
            G : networkx graph object, which represents the modelled graph

        Returns:
            valid : Boolean variable which tells if the solution is valid or invalid
            solution : 2D solution list to our Sudoku problem
    '''

    sampler = LeapHybridDQMSampler()
    sampleset = sampler.sample_dqm(dqm)
    sample = sampleset.first.sample
    energy = sampleset.first.energy

    valid = True

    for edge in G.edges:
        i,j = edge
        if(sample[i]==sample[j]):
            valid = False
            break

    print("Solution :",sample)
    print("Solution Energy :",energy)
    print("Solution validty:",valid)

    global_row = int(math.sqrt(len(G.nodes())))
    solution = []

    for i in range(1,(global_row**2)+1):
        row = []
        row.append(sample[i])
        print(sample[i]+1,end=' ')

        if((i)%global_row==0):
            print("\n")
            solution.append(row)
    
    return valid, solution



if __name__ == '__main__':
    file_path = "C:\\Users\\Rishabh Singhal\\Desktop\\2021_sycamore\\sudoku.txt"
    
    #read text file
    sudoku = readFile(file_path)

    #prepare a general layout of sudoku as graph
    G = graphModelling(len(sudoku[0]))

    #prepare dqm
    dqm = buildDQM(G, sudoku)

    #solve dqm
    valid, solution = solveSudoku(dqm, G)