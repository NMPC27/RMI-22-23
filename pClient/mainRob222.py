
import sys
from typing import Counter
from croblink import *
from math import *
import xml.etree.ElementTree as ET

CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.counter=0
        self.right=0
        self.direction=0
        #if it goes to the first if, it wont go to the second one
        self.Turn_to_0=1

        # lista de vertices detectados
        self.vertices=[]

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
            

    def wander(self):

        #print('|'+''.join(self.measures.lineSensor).replace('1','█').replace('0',' ')+'|')

        
        compass=self.measures.compass+180
        #print(str(compass)+'     '+str(self.counter))

        #print(self.measures.x,self.measures.y)

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

                if self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1':
                    print('frente e direita')
                    self.check_intersections('front')

                    

            else:
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

                if self.measures.lineSensor[5]=='1' and self.measures.lineSensor[6]=='1':
                    print('frente e esquerda')
                    self.check_intersections('front')

  
        else:

            if self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1' and ( (compass>82.5 and compass<97.5) or (compass>172.5 and compass<187.5) or (compass>262.5 and compass<277.5) or (compass>352.5 and compass<360 or compass>0 and compass<7.5)  ): ##cruzamento
                self.right=0
                self.counter+=1
                #guardar a ultima direçao do robô
                self.direction=compass
                self.driveMotors(-0.15,0.15)
                #print("cruzamento")

                self.check_intersections('left')

            elif self.measures.lineSensor[6]=='1' and self.measures.lineSensor[5]=='1' and ( (compass>82.5 and compass<97.5) or (compass>172.5 and compass<187.5) or (compass>262.5 and compass<277.5) or (compass>352.5 and compass<360 or compass>0 and compass<7.5)  ):
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

            else:
                self.driveMotors(0.12,0.12)


    def check_intersections(self,side):

        v_check = [v for v in self.vertices if v.x == self.round_positions(self.measures.x) and v.y == self.round_positions(self.measures.y)]
        #verificar se o vertice já existe no nosso array ou se é um vertice novo
        if  v_check == []:

            v = Vertice(self.round_positions(self.measures.x),self.round_positions(self.measures.y))
            
            v = self.check_adjacentes(v,side)
            
            
            self.vertices.append(v)
            #print("new Vertice")
            print(v.get_visitados())

        
        #no caso do vertice já existir, verificar se o caminho já existe ou se é um caminho novo
        else:
            v = v_check[0]
            v = self.check_adjacentes(v,side)

            index = next((i for i, item in enumerate(self.vertices) if item.x == v.x and item.y == v.y), None)

            if index!=None:
                self.vertices[index] = v
                #print("update Vertice")
            print(v.get_visitados())


        


    
    #verificar adjacentes dos vertices
    def check_adjacentes(self,v,side):

        value = 90 * round(self.direction / 90)
        if value == 360:
            value = 0
        
        adjacentes = v.get_visitados()
        if side =='front' and adjacentes[value] !=True:
            v.add_visitado(value, False)
        else:
        
            #cruzamento á direita
            if self.measures.lineSensor[6]=='1' and self.measures.lineSensor[5]=='1':
                if self.direction>=80 and self.direction<=100 and adjacentes[0] != True:
                        
                    #v.add_adjacente(0, v1)
                    v.add_visitado(0, True) if side == 'right' else v.add_visitado(0, False) 

                elif self.direction>=350 and self.direction<=10 and adjacentes[270] != True:
                        
                    #v.add_adjacente(270, v1)
                    v.add_visitado(270, True) if side == 'right' else v.add_visitado(270, False) 

                        
                elif self.direction>=260 and self.direction<=280 and adjacentes[180] != True:
                        
                    #v.add_adjacente(180, v1)
                    v.add_visitado(180, True) if side == 'right' else v.add_visitado(180, False) 


                elif self.direction>=170 and self.direction<=190 and adjacentes[90] != True: 

                    #v.add_adjacente(90, v1)
                    v.add_visitado(90, True) if side == 'right' else v.add_visitado(90, False) 



            #cruzamento á esquerda
            if self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1':
                if self.direction>=80 and self.direction<=100 and adjacentes[180] != True:
                        
                    #v.add_adjacente(180, v1)
                    v.add_visitado(180, True) if side == 'left' else v.add_visitado(180, False) 

                elif self.direction>=350 and self.direction<=10 and adjacentes[90] != True:
                        
                    #v.add_adjacente(90, v1)
                    v.add_visitado(90, True) if side == 'left' else v.add_visitado(90, False) 
                        
                elif self.direction>=260 and self.direction<=280 and adjacentes[0] != True:
                        
                    #v.add_adjacente(0, v1)
                    v.add_visitado(0, True) if side == 'left' else v.add_visitado(0, False) 

                elif self.direction>=170 and self.direction<=190 and adjacentes[270] != True:

                    #v.add_adjacente(270, v1)
                    v.add_visitado(270, True) if side == 'left' else v.add_visitado(270, False) 

        return v
    
    # arredondar para multiplos de 2
    def round_positions(self,number):
        return 2 * round(number / 2)
        
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
        self.visitados[angulo] = False

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
