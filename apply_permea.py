import readline

# read file
import numpy as np
import math
import fileinput
import sys,os

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


# not working
def is_in_web(coord):
    x=coord[0]
    y=coord[1]
    
    # conditions from example
    r_art=1.0
    scaling=1.5
    web_diameter=0.125*scaling
    r_major=(7.0+r_art)*scaling
    #r_minor=r_major-web_diameter*scaling
    r_outer=(7.0+2.0*r_art)*scaling
    
    dist_inner=np.square(r_outer-web_diameter)
    dist_outer=np.square(r_outer)
    #transform according to last dy
    dist_point=((y+r_major)*(y+r_major)+x*x)
    #print(coord)
    angle=180/math.pi*angle_between((coord[0],coord[1]+r_major,coord[2]),(0,1,0))
    #print(coord,angle)

    if(dist_inner< dist_point and dist_point< dist_outer):
    #if((x*x+(y+1.6488*9)*(y+1.6488*9)-1.6488*10*1.6488*10>0)and (x*x+(y+1.6488*9)*(y+1.6488*9)-1.6488*12*1.6488*12<0)):
        if(5.0<angle and angle<45):
            return True
    return False

# defines a coll at the given position(with radius)
def is_in_coil(coord):
    d=0.5
    # define everything which is not in "coil"
    centers=[np.array([8.4,0.8,0.0]),np.array([6.0,1.0,0.0]),np.array([7.0,2.0,0.0]),np.array([5.3,1.25,0.0]),np.array([5.6,3.0,0.0]),np.array([8.0,3.0,0.0]),np.array([8.0,2.0,0.0]),np.array([7.0,1.0,0.0]),np.array([7.0,3.0,0.0]),np.array([6.0,2.0,0.0])]
    for c in centers:
        if(np.sqrt(np.linalg.norm(coord-c))<=d):
            return True
    return False


# checks wheater we are in the anyeursm
# if yes apply sinus pattern
def is_in_aneuyrsm(coord):
    x=coord[0]
    y=coord[1]
    # changed from 6 to 4= approx 0.25 = approx size of real coil
    if((x*x+(y+1.6488*9)*(y+1.6488*9)-1.6488*10*1.6488*10*1.02)>0 and np.sin(x*np.pi*6*1.6488/2)>0 and np.sin(y*np.pi*6*1.6488/2)>0):
        #print("yes")
        return True
    return False

"""linear scale the porosity values towards center """
def scale_factor(coord):
    d=0.3
    # define everything which is not in "coil"
    centers=[np.array([7.0,2.0,0.0]),np.array([9.0,2.0,0.0]),np.array([7.0,1.0,0.0]),np.array([7.0,3.0,0.0]),np.array([6.0,2.0,0.0])]
    for c in centers:
        norm=np.sqrt(np.linalg.norm(coord-c))
        if(norm<=d):
            return (d-norm)/d
    return False

""" read all nodes and elements """
def get_Nodecoords_of_File(filename):
    f = open(filename,'r')
    node_strings=[]
    starting_nodesets=False
    for l in f:
        if(l.find('---NODE COORDS')>-1):
            starting_nodesets=True
        elif(starting_nodesets and l.find('NODE')>-1):
            node_strings.append(l)
        else:
            pass
    f.close()

    #snode_string
    nodes=[]
    # number is n-1 eg. the first element is found at 0 Position
    for n in node_strings:
        splitnode=n.split()
        nodes.append([float(splitnode[3]),float(splitnode[4]),float(splitnode[5])])
    return nodes

""" read all elements """
def get_Elements_of_File(filename,section,elementtype):
    f = open(filename,'r')
    line_strings=[]
    starting_nodesets=False
    for l in f:
        if(l.find(section)>-1):
            starting_nodesets=True
        elif(starting_nodesets and l.find(elementtype)>-1):
            line_strings.append(l)
        else:
            pass
    f.close()
    
    nodes=[]
    # number is n-1 eg. the first element is found at 0 Position
    for n in line_strings:
        splitnode=n.split()
        nodes.append([int(splitnode[3]),int(splitnode[4]),int(splitnode[5]),int(splitnode[6])])
    return nodes


"""
loops through existing dat file and create new lines
reetruns the old line and new line
"""
def create_Lines(filename,elements_nodes, element_name,value,dim=2):

    if(element_name == "WALLQ4PORO"):
        pass
    elif (element_name =="WALLQ4POROP1"):
        pass
    else:
        raise ValueError('The requested element type: {0} is not implemented yet!'.format(element_name))
    
    if( not os.path.isfile(filename)):
        raise ValueError('{0} is not found.'.format(filename))

    f = open(filename)
    lines_for_replace=[]
    starting_nodesets=False
    for l in f:
        # find structure element start
        if(l.find('---STRUCTURE ELEMENTS')>-1):
            starting_nodesets=True
        elif(starting_nodesets and len(l.split())):
            for en in elements_nodes:
                newline=l.split()                
                if(newline[0]==str(en[0])): # and newline[1]=element_name):
                    # start adjusting the line
                    for d in range(1,dim+1):
                        # every element may have more nodes that must be adjusted
                        for local_n in en[1]:
                            coef_start=newline.index('POROANISONODALCOEFFS'+str(d))+local_n
                            newline[coef_start]=str(value[d-1])
                    lines_for_replace.append([l,' '.join(n for n in newline)+ '\n'])

        else:
            pass
    f.close()
    return lines_for_replace

""" 
updates the lines of the file accordingly
old_new_lines is a list of length n, where on the first entry the old line(to be replaced)
and in the second entry the new line(replacement) is
"""
def update_File_with_Lines(filename, old_new_lines):
    if( not os.path.isfile(filename)):
        raise ValueError('{0} is not found.'.format(filename))
    if( len(old_new_lines)==0):
        #print(old_new_lines)
        raise ValueError('old_new_lines is empty, therefore I have nothing to change in the file')
    for line in fileinput.input(filename, inplace=1):
        for onl in old_new_lines:
            if onl[0] in line:
                line = line.replace(onl[0],onl[1])
        sys.stdout.write(line)

""" loop through all elements and returns element numbers with local node index """
def get_ElementIDs(elements,nodes,func):

    element_ids=[]

    # we loop through all elements and set the nodal coordinate in the element list
    for e_idx,e in enumerate(elements):
        element_node_coordinates=nodes[e-1]
        loc_node_found=[]
        for  node_num ,coord in enumerate(element_node_coordinates):
            # checks if the nodal coordinate is within the set of nodes to be adjusted
            if func(coord):
                loc_node_found.append(node_num+1)
        if(loc_node_found):
            element_ids.append([e_idx+1,loc_node_found])
    return element_ids

# driver files
if __name__ == '__main__':
    
    filename='poro.dat'
    element_type="WALLQ4PORO"

    nodes=np.array(get_Nodecoords_of_File(filename))
    elements=np.array(get_Elements_of_File(filename,'---STRUCTURE ELEMENTS',element_type))

    #decide what permea - domain you want (coil, flow diverter)
    element_ids=get_ElementIDs(elements,nodes,is_in_aneuyrsm)
    
    #check if we potentially overwrite something
    for e_idx,e in enumerate(element_ids):
        for n_idx,n in enumerate(element_ids):
            if(e==n and e_idx != n_idx):
                raise ValueError ("Error Element index is not unique")
    #permea_coeffs=np.array([7.4245e-3/4, 7.4245e-3/4])
    permea_coeffs=np.array([1.0e-10, 1.0e-10])



    lines=create_Lines(filename,element_ids,element_type,permea_coeffs)

    update_File_with_Lines(filename,lines)
