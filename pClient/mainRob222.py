
import sys
from typing import Counter
from croblink import *
from math import *
import xml.etree.ElementTree as ET


#import keyboard #!DELETE

CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.counter=0
        self.right=None
        self.direction=0
        #if it goes to the first if, it wont go to the second one
        self.Turn_to_0=1

        #number of sides detected 
        self.number_sides_detected=0

        #virar 180 graus - dead end
        self.turn_180=0

        # lista de vertices detectados
        self.vertices=[]

        # ultimo vertice visitado
        self.last_vertice = None

        # posicao inicial
        self.inicio = (0,0)


        # lista de arestas detectadas
        self.adjacent_dict={
            # (846,398): set{(856,400,270, 4)},
            # }
        }


    # In this map the center of cell (i,j), (i in 0..6, j in 0..13) is mapped to labMap[i*2][j*2].
    # to know if there is a wall on top of cell(i,j) (i in 0..5), check if the value of labMap[i*2+1][j*2] is space or not
    def setMap(self, labMap):
        self.labMap = labMap

    def printMap(self):
        for l in reversed(self.labMap):
            print(''.join([str(l) for l in l]))

    def run(self):
        if self.status != 0:
            print("Connection refused or error")
            quit()

        state = 'stop'
        stopped_state = 'run'

        while True:
            self.readSensors()

            if self.measures.endLed:
                print(self.rob_name + " exiting")
                quit()

            if state == 'stop' and self.measures.start:
                state = stopped_state

            if state != 'stop' and self.measures.stop:
                stopped_state = state
                state = 'stop'

            if state == 'run':
                if self.measures.visitingLed==True:
                    state='wait'
                if self.measures.ground==0:
                    self.setVisitingLed(True);
                self.wander()
            elif state=='wait':
                self.setReturningLed(True)
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    state='return'
                self.driveMotors(0.0,0.0)
            elif state=='return':
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    self.setReturningLed(False)
                self.wander()

    def createMatrix(self):

        m = 21
        n = 49
  
        matrix = [[0 for x in range(n)] for x in range(m)]

        #matrix = [ [0] * 49 ] * 21 

        # linha 11 e coluna 25
        matrix[10][24] = 3

        for key in self.adjacent_dict.keys():

            # arranjar os indices para a matrix do vertice novo

            #print(key)

            x_key = 10 + (self.inicio[1] - key[1])
            y_key = 24 + (key[0] - self.inicio[0])

            #print("x_key: " + str(x_key) + " y_key: " + str(y_key))

            set_key = self.adjacent_dict[key]

            for value in set_key:
                
                # numero de arestas
                n_arestas = value[3]//2
                if value[2] == 0:
                    for i in range(1,n_arestas+1,2):
                        matrix[x_key][y_key-i] = 1
                elif value[2] == 90:
                    for i in range(1,n_arestas+1,2):
                        matrix[x_key+i][y_key] = 2
                elif value[2] == 180:
                    for i in range(1,n_arestas+1,2):
                        matrix[x_key][y_key+i] = 1
                elif value[2] == 270:
                    for i in range(1,n_arestas+1,2):
                        matrix[x_key-i][y_key] = 2

        return matrix


    def check_falses(self):
        for i in range(0,len(self.vertices)):
            if False in self.vertices[i].visitados.values():
                return False

        return True

    def check_false_front(self,case):

        v_check = [v for v in self.vertices if v.x == self.round_positions(self.measures.x) and v.y == self.round_positions(self.measures.y)]
        
        if len(v_check) != 0:

            v = v_check[0]

            value = 90 * round(self.direction / 90)
            if value == 360:
                value = 0

            if case == "fe":

                if value == 0:
                    if v.visitados[270] != None: 
                        return False
                    else:
                        return True
                elif value == 90:
                    if v.visitados[0] != None: 
                        return False
                    else:
                        return True
                elif value == 180:
                    if v.visitados[90] != None: 
                        return False
                    else:
                        return True
                elif value == 270:
                    if v.visitados[180] != None: 
                        return False
                    else:
                        return True


            if case == "fd":
                if value == 0:
                    if v.visitados[90] != None: 
                        return False
                    else:
                        return True
                elif value == 90:
                    if v.visitados[180] != None: 
                        return False
                    else:
                        return True
                elif value == 180:
                    if v.visitados[270] != None: 
                        return False
                    else:
                        return True
                elif value == 270:
                    if v.visitados[0] != None: 
                        return False
                    else:
                        return True


    def wander(self):
            


        #print(self.measures.time)


        # Definir posição do robo
        if self.measures.time<=2:
            self.inicio = ( self.round_positions(self.measures.x), self.round_positions(self.measures.y) )


        if ( (int(self.simTime) - self.measures.time) <= 1500 and self.check_falses() ) or  ( (int(self.simTime) - self.measures.time) <= 200) :

            matrix = self.createMatrix()
            #print(matrix)

            with open('mapa.txt', 'w') as f:
                for i in range(len(matrix)):
                    for j in range(len(matrix[0])):
                        if matrix[i][j] == 0:
                            f.write(' ')
                        elif matrix[i][j] == 1:
                            f.write('-')
                        elif matrix[i][j] == 2:
                            f.write('|')
                        elif matrix[i][j] == 3:
                            f.write('I')
                        
                    f.write('\n')

            #print(self.adjacent_dict)
            #for i in self.vertices:
                #print("-------------")
                #print(str(i.x) + str(i.y))
                #print(i.visitados)
                #print("-------------")
            #print(self.check_falses())
            self.finish()


        compass=self.measures.compass+180
        

        if self.counter>0:
          

            if self.right==1:
                if self.direction>=80 and self.direction<=100 and compass<350:
                    self.driveMotors(0.1,0.0)
                    self.Turn_to_0=0
                    #print("turn right to 0")
                elif (self.direction>=350 or self.direction<=10) and compass>270:
                    self.driveMotors(0.1,0.0)
                    self.Turn_to_0=0
                    
                elif compass> self.direction-90 and self.Turn_to_0:
                    self.driveMotors(0.1,0.0)
                    #print("TURN LEFT")
                else:
                    self.counter=0
                    self.Turn_to_0=1
                    self.number_sides_detected=0
                    self.right=None

                if self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1' and self.number_sides_detected!=2:
                    #print('frente e direita')
                    if self.check_false_front("fd"):
                        self.check_intersections('front')
                    

                    

            elif self.right==0:

                if self.direction>=260 and self.direction<=280 and compass>10:
                    self.driveMotors(0.0,0.1)
                    self.Turn_to_0=0
                    #print("turn left to 0")
                elif (self.direction>=350 or self.direction<=10) and compass<90:
                    self.driveMotors(0.0,0.1)
                    self.Turn_to_0=0

                elif compass< self.direction+90 and self.Turn_to_0:
                    self.driveMotors(0.0,0.1)
                    #print("TURN LEFT")

                else:
                    self.counter=0
                    self.Turn_to_0=1
                    self.number_sides_detected=0
                    self.right=None


                if self.measures.lineSensor[5]=='1' and self.measures.lineSensor[6]=='1' and self.number_sides_detected!=2:
                    #print('frente e esquerda')
                    if self.check_false_front("fe"):
                        self.check_intersections('front')
            
            else:
                if self.turn_180 == 1:
                    value = 90 * round(self.direction / 90)
                    if value == 360:
                        value = 0

                    # print(value)
                    # print(compass)

                    if value==180:
                        if not (compass>=350 or compass<=10 ):
                            self.driveMotors(0.15,-0.15)
                        else:
                            self.turn_180=0
                            self.counter=0
 

                    elif value==270:
                        #print('TURN 180 111')
                        if 90<= compass:
                            #print('TURN 180 222')
                            self.driveMotors(0.15,-0.15)
                        else:
                            self.turn_180=0
                            self.counter=0

                        
                    elif value==90:
                        if 270 >= compass:
                            self.driveMotors(-0.15,0.15)
                        else:
                            self.turn_180=0
                            self.counter=0

                    elif value==0:
                        
                        if not (compass>=170 and compass<=190):
                            self.driveMotors(-0.15,0.15)
                        else:
                            self.turn_180=0
                            self.counter=0
                            
                            
  
        else:

            # None = nao pode ir, 0 = pode ir mas já foi , 1 = pode ir mas ainda nao foi
            right = None
            left = None
            front = None

            if self.can_turn('left'):

                if self.decide('left'):
                    left = 1
                else:
                    left = 0
            
            if self.can_turn('right'):

                if self.decide('right'):
                    right = 1
                else:
                    right = 0
            
            if self.can_turn('front') and (left == 0 or right == 0):

                if self.decide('front'):
                    front = 1
                else:
                    front = 0

            #if left != None or right != None or front != None:
                #print('left: '+str(left)+' front: '+str(front)+' right: '+str(right))
            #if left != 1  and right != 1 and front != 1 and (left==0 or right==0 or front==0):
                
            #    v_check = [v for v in self.vertices if v.visitados[0]==False or v.visitados[90]==False or v.visitados[180]==False or v.visitados[270]==False]
                
            #    if v_check==[]:
            #        print("TUDO PROCURADO")

            #    v = v_check[0]

            #    x=v.x
            #    y=v.y
            #    #print(self.a_star_algorithm((self.round_positions(self.measures.x),self.round_positions(self.measures.y)),(x,y)))



            if (left == 1 ) or (left==0 and right==None and front==None)  : ##cruzamento
                self.right=0
                self.counter+=1
                #guardar a ultima direçao do robô
                self.direction=compass
                self.driveMotors(-0.15,0.15)
                #print("cruzamento")

                self.check_intersections('left')

            #( right == 1 ) or (right==0 and left==None)
            elif (right == 1 ) or (right==0 and front==None) : ##cruzamento
                self.right=1
                self.counter+=1
                #guardar a ultima direçao do robô
                self.direction=compass
                self.driveMotors(0.15,-0.15)
                #print("cruzamento")

                self.check_intersections('right')
            
            elif self.measures.lineSensor[1]=='1' and self.measures.lineSensor[2]=='1':
                self.driveMotors(0.0,0.1)
                #print("adjust left")

            elif self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='1':
                self.driveMotors(0.1,0.0)
                #print("adjust right")

            elif self.measures.lineSensor[0]=='1':
                self.driveMotors(-0.1,0.1)
                #print('NEW STUFF left')


            elif self.measures.lineSensor[6]=='1':
                self.driveMotors(0.1,-0.1)
                #print('NEW STUFF rigth')

            elif self.measures.lineSensor==['0','0','0','0','0','0','0']:
                self.turn_180=1
                self.counter+= 1
                self.direction=compass

                value = 90 * round(self.direction / 90)
                if value == 360:
                    value = 0
                if value == 0 or value == 90:
                    self.driveMotors(-0.15,0.15)
                else:
                    self.driveMotors(0.15,-0.15)
                self.check_intersections('back')
                #print('-------------------------------------')
                 
            
            else:
                if front != None:
                    self.check_intersections(None)
                self.driveMotors(0.12,0.12)

    # funcao que decide se o robo devia virar para uma dada direcao
    def decide(self,side):

        compass=self.measures.compass+180
        v_check = [v for v in self.vertices if v.x == self.round_positions(self.measures.x) and v.y == self.round_positions(self.measures.y)]
        
        # se o vertice nao existir é porque vai ser criado neste cruzamento (DEVE SER TESTADO MAIS TARDE DE NOVO)
        if v_check == []:
            return True
        else:
            v = v_check[0]

            visitados = v.get_visitados()

            
            #cruzamento á direita
            if side == 'right':
                if compass>=80 and compass<=100:
                        
                    if visitados[0] == True:
                        return False
                    else:
                        return True

                elif compass>=350 and compass<=10:
                        
                    if visitados[270] == True:
                        return False
                    else:
                        return True 

                        
                elif compass>=260 and compass<=280:
                        
                    if visitados[180] == True:
                        return False
                    else:
                        return True


                elif compass>=170 and compass<=190: 

                    if visitados[90] == True:
                        return False
                    else:
                        return True



            #cruzamento á esquerda
            if side == 'left':
                if compass>=80 and compass<=100:
                        
                    if visitados[180] == True:
                        return False
                    else:
                        return True

                elif compass>=350 and compass<=10:
                        
                    if visitados[90] == True:
                        return False
                    else:
                        return True
                        
                elif compass>=260 and compass<=280:
                    
                    if visitados[0] == True:
                        return False
                    else:
                        return True 

                elif compass>=170 and compass<=190:

                    if visitados[270] == True:
                        return False
                    else:
                        return True
            
            #cruzamento á frente
            if side == 'front':
                if compass>=80 and compass<=100:
                        
                    if visitados[90] == True:
                        return False
                    else:
                        return True

                elif compass>=350 and compass<=10:
                        
                    if visitados[0] == True:
                        return False
                    else:
                        return True
                        
                elif compass>=260 and compass<=280:
                        
                    if visitados[270] == True:
                        return False
                    else:
                        return True

                elif compass>=170 and compass<=190:

                    if visitados[180] == True:
                        return False
                    else:
                        return True



    # funcao que verifica se o robo pode virar para uma dada direcao
    def can_turn(self,side):
        
        compass=self.measures.compass+180

        if side=='left':
            if self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1' and ( (compass>85 and compass<95) or (compass>175 and compass<185) or (compass>265 and compass<275) or (compass>355 and compass<360 or compass>0 and compass<5) ):
                
                return True
            else:
                return False
        elif side=='right':
            if self.measures.lineSensor[6]=='1' and self.measures.lineSensor[5]=='1' and ( (compass>85 and compass<95) or (compass>175 and compass<185) or (compass>265 and compass<275) or (compass>355 and compass<360 or compass>0 and compass<5) ):
                
                return True
            else:
                return False
        elif side == 'front':

            v_check = [v for v in self.vertices if v.x == self.round_positions(self.measures.x) and v.y == self.round_positions(self.measures.y)]

            if v_check == []:
                return False
            else:
                v = v_check[0]

                visitados = v.get_visitados()

                if compass>=80 and compass<=100:
                        
                    if visitados[90] == None:
                        return False
                    else:
                        return True

                elif compass>=350 and compass<=10:
                        
                    if visitados[0] == None:
                        return False
                    else:
                        return True
                        
                elif compass>=260 and compass<=280:
                        
                    if visitados[270] == None:
                        return False
                    else:
                        return True

                elif compass>=170 and compass<=190:

                    if visitados[180] == None:
                        return False
                    else:
                        return True



    def check_intersections(self,side):

        v_check = [v for v in self.vertices if v.x == self.round_positions(self.measures.x) and v.y == self.round_positions(self.measures.y)]
        #verificar se o vertice já existe no nosso array ou se é um vertice novo

        value = 90 * round(self.direction / 90)
        if value == 360:
            value = 0

        if self.last_vertice != None:

            cost = 0
            if self.last_vertice[0] == self.round_positions(self.measures.x):
                cost = abs(self.last_vertice[1] - self.round_positions(self.measures.y))

            if self.last_vertice[1] == self.round_positions(self.measures.y):
                cost = abs(self.last_vertice[0] - self.round_positions(self.measures.x))

            if cost != 0:
            
                if self.last_vertice not in self.adjacent_dict.keys():
                    self.adjacent_dict[self.last_vertice] = set()

                if self.adjacent_dict[(self.last_vertice[0],self.last_vertice[1])] == set():
                    self.adjacent_dict[(self.last_vertice[0],self.last_vertice[1])].add((self.round_positions(self.measures.x),self.round_positions(self.measures.y),value,cost))


                for s in self.adjacent_dict[(self.last_vertice[0],self.last_vertice[1])].copy():
                    if s[2] == value and s[3] > cost:
                        self.adjacent_dict[(self.last_vertice[0],self.last_vertice[1])].remove(s)
                        self.adjacent_dict[(self.last_vertice[0],self.last_vertice[1])].add((self.round_positions(self.measures.x),self.round_positions(self.measures.y),value,cost))
                        break
                    elif s[2] == value and s[3] < cost:
                        break
                    else:
                        self.adjacent_dict[(self.last_vertice[0],self.last_vertice[1])].add((self.round_positions(self.measures.x),self.round_positions(self.measures.y),value,cost))



                if value>=180:
                    value-=180
                else:
                    value+=180

                if (self.round_positions(self.measures.x),self.round_positions(self.measures.y)) not in self.adjacent_dict.keys():
                    self.adjacent_dict[(self.round_positions(self.measures.x),self.round_positions(self.measures.y))] = set()

                if self.adjacent_dict[(self.round_positions(self.measures.x),self.round_positions(self.measures.y))] == set():
                    self.adjacent_dict[(self.round_positions(self.measures.x),self.round_positions(self.measures.y))].add((self.last_vertice[0],self.last_vertice[1],value,cost))    
                

                for s in self.adjacent_dict[(self.round_positions(self.measures.x),self.round_positions(self.measures.y))].copy():
                    if s[2] == value and s[3] > cost:
                        self.adjacent_dict[(self.round_positions(self.measures.x),self.round_positions(self.measures.y))].remove(s)
                        self.adjacent_dict[(self.round_positions(self.measures.x),self.round_positions(self.measures.y))].add((self.last_vertice[0],self.last_vertice[1],value,cost))

                        break
                    elif s[2] == value and s[3] < cost:
                        break
                    else:
                        self.adjacent_dict[(self.round_positions(self.measures.x),self.round_positions(self.measures.y))].add((self.last_vertice[0],self.last_vertice[1],value,cost))
        
        
        self.last_vertice = (self.round_positions(self.measures.x),self.round_positions(self.measures.y))


        if  v_check == [] and side !=None:

            v = Vertice(self.round_positions(self.measures.x),self.round_positions(self.measures.y))
            
            v = self.check_adjacentes(v,side)
            
            
            self.vertices.append(v)
            #print("new Vertice")
            #print(v.get_visitados())

        
        #no caso do vertice já existir, verificar se o caminho já existe ou se é um caminho novo
        elif side !=None:
            v = v_check[0]
            v = self.check_adjacentes(v,side)

            index = next((i for i, item in enumerate(self.vertices) if item.x == v.x and item.y == v.y), None)

            if index!=None:
                self.vertices[index] = v
                #print("update Vertice")
            #print(v.get_visitados())

    #verificar adjacentes dos vertices
    def check_adjacentes(self,v,side):

        value = 90 * round(self.direction / 90)
        if value == 360:
            value = 0

        if value>=180:
            v.add_visitado(value-180, True)
        else:
            v.add_visitado(value+180, True)
        
        if side =='front':
            if v.visitados[value] !=True: 
                v.add_visitado(value, False)

        else:
            #print(self.direction)
            #cruzamento á direita
            if self.measures.lineSensor[6]=='1' and self.measures.lineSensor[5]=='1':

                if self.direction>=80 and self.direction<=100 and v.visitados[0] != True:
                        
                    #v.add_adjacente(0, v1)
                    v.add_visitado(0, True) if side == 'right' else v.add_visitado(0, False)

                    self.number_sides_detected+=1


                elif (self.direction>=350 or self.direction<=10) and v.visitados[270] != True:
                    #print('check adjacentes right')
                        
                    #v.add_adjacente(270, v1)
                    v.add_visitado(270, True) if side == 'right' else v.add_visitado(270, False)

                    self.number_sides_detected+=1


                        
                elif self.direction>=260 and self.direction<=280 and v.visitados[180] != True:
                        
                    #v.add_adjacente(180, v1)
                    v.add_visitado(180, True) if side == 'right' else v.add_visitado(180, False)

                    self.number_sides_detected+=1



                elif self.direction>=170 and self.direction<=190 and v.visitados[90] != True: 

                    #v.add_adjacente(90, v1)
                    v.add_visitado(90, True) if side == 'right' else v.add_visitado(90, False)

                    self.number_sides_detected+=1




            #cruzamento á esquerda
            if self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1':
                if self.direction>=80 and self.direction<=100 and v.visitados[180] != True:
                        
                    #v.add_adjacente(180, v1)
                    v.add_visitado(180, True) if side == 'left' else v.add_visitado(180, False)

                    self.number_sides_detected+=1


                elif (self.direction>=350 or self.direction<=10) and v.visitados[90] != True:
                    #print('check adjacentes left')
                        
                    #v.add_adjacente(90, v1)
                    v.add_visitado(90, True) if side == 'left' else v.add_visitado(90, False)

                    self.number_sides_detected+=1

                        
                elif self.direction>=260 and self.direction<=280 and v.visitados[0] != True:
                        
                    #v.add_adjacente(0, v1)
                    v.add_visitado(0, True) if side == 'left' else v.add_visitado(0, False)

                    self.number_sides_detected+=1


                elif self.direction>=170 and self.direction<=190 and v.visitados[270] != True:

                    #v.add_adjacente(270, v1)
                    v.add_visitado(270, True) if side == 'left' else v.add_visitado(270, False)

                    self.number_sides_detected+=1


        return v
    
    # arredondar para multiplos de 2
    def round_positions(self,number):
        return 2 * round(number / 2)
        
    def a_star_algorithm(self, start_node, stop_node):
        # open_list is a list of nodes which have been visited, but who's neighbors
        # haven't all been inspected, starts off with the start node
        # closed_list is a list of nodes which have been visited
        # and who's neighbors have been inspected
        open_list = set([start_node])
        closed_list = set([])

        # g contains current distances from start_node to all other nodes
        # the default value (if it's not found in the map) is +infinity
        g = {}

        g[start_node] = 0

        # parents contains an adjacency map of all nodes
        parents = {}
        parents[start_node] = start_node

        while len(open_list) > 0:
            n = None

            # find a node with the lowest value of f() - evaluation function
            for v in open_list:
                if n == None or g[v] < g[n]:
                    n = v

            if n == None:
                print('Path does not exist!')
                return None

            # if the current node is the stop_node
            # then we begin reconstructin the path from it to the start_node
            if n == stop_node:
                reconst_path = []

                while parents[n] != n:
                    reconst_path.append(n)
                    n = parents[n]

                reconst_path.append(start_node)

                reconst_path.reverse()

                print('Path found: {}'.format(reconst_path))
                return reconst_path

            # for all neighbors of the current node do
            # (self.round_positions(self.measures.x),self.round_positions(self.measures.y),value,cost)
            # (m,weight)
            for (x,y,value,cost) in self.adjacent_dict[n]:
                # if the current node isn't in both open_list and closed_list
                # add it to open_list and note n as it's parent
                if (x,y) not in open_list and (x,y) not in closed_list:
                    open_list.add((x,y))
                    parents[(x,y)] = n
                    g[(x,y)] = g[n] + cost

                # otherwise, check if it's quicker to first visit n, then m
                # and if it is, update parent data and g data
                # and if the node was in the closed_list, move it to open_list
                else:
                    if g[(x,y)] > g[n] + cost:
                        g[(x,y)] = g[n] + cost
                        parents[(x,y)] = n

                        if (x,y) in closed_list:
                            closed_list.remove((x,y))
                            open_list.add((x,y))

            # remove n from the open_list, and add it to closed_list
            # because all of his neighbors were inspected
            open_list.remove(n)
            closed_list.add(n)

        print('Path does not exist!')
        return None




class Vertice():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        #exemplo {0: v1, 90: v2, 180: v3, 270: v4} se fosse um cruzamento
        self.adjacentes = {}
        #exemplo {0: false, 90: false, 180: true, 270: false} se fosse um cruzamento
        self.visitados = {0: None, 90: None, 180: None, 270: None}

    # adiciona um vertice adjacente no dicionario, com o angulo como key
    def add_adjacente(self,angulo, vertice):
        self.adjacentes[angulo] = vertice

    def get_adjacentes(self):
        return self.adjacentes

    def add_visitado(self,angulo,cond):
        self.visitados[angulo] = cond

    def get_visitados(self):
        return self.visitados

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def __str__(self):
        return "V(%d, %d)" % (self.x, self.y)


class Map():
    def __init__(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        
        self.labMap = [[' '] * (CELLCOLS*2-1) for i in range(CELLROWS*2-1) ]
        i=1
        for child in root.iter('Row'):
           line=child.attrib['Pattern']
           row =int(child.attrib['Pos'])
           if row % 2 == 0:  # this line defines vertical lines
               for c in range(len(line)):
                   if (c+1) % 3 == 0:
                       if line[c] == '|':
                           self.labMap[row][(c+1)//3*2-1]='|'
                       else:
                           None
           else:  # this line defines horizontal lines
               for c in range(len(line)):
                   if c % 3 == 0:
                       if line[c] == '-':
                           self.labMap[row][c//3*2]='-'
                       else:
                           None
               
           i=i+1


rob_name = "pClient1"
host = "localhost"
pos = 1
mapc = None

for i in range(1, len(sys.argv),2):
    if (sys.argv[i] == "--host" or sys.argv[i] == "-h") and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    elif (sys.argv[i] == "--pos" or sys.argv[i] == "-p") and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    elif (sys.argv[i] == "--robname" or sys.argv[i] == "-r") and i != len(sys.argv) - 1:
        rob_name = sys.argv[i + 1]
    elif (sys.argv[i] == "--map" or sys.argv[i] == "-m") and i != len(sys.argv) - 1:
        mapc = Map(sys.argv[i + 1])
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':
    rob=MyRob(rob_name,pos,[0.0,60.0,-60.0,180.0],host)
    if mapc != None:
        rob.setMap(mapc.labMap)
        rob.printMap()
    
    rob.run()