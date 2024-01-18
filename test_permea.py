import unittest,os,sys
import numpy as np

from apply_permea import *

class TestStringMethods(unittest.TestCase):


    def test_read_nodes(self):
        nodes=np.array(get_Nodecoords_of_File('test_files/read_test.dat'))
        nodes_true=np.array([[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.5, 0.0], [0.5, 0.5, 0.0], [0.0, 0.5, 0.0], [1.5, 0.0, 0.0], [1.5, 0.5, 0.0]])
        assert((nodes==nodes_true).all())

    def test_read_elements(self):
        elements=np.array(get_Elements_of_File('test_files/read_test.dat','--STRUCTURE ELEMENTS','WALLQ4PORO'))
        elements_true=np.array([[1, 2, 5, 6] ,[2, 3, 4, 5], [3, 7, 8, 4]])
        assert((elements==elements_true).all())

    def test_empty_file(self):
        with self.assertRaises(ValueError):
             create_Lines('1','1',"WALLQ4PORO",'2')
    
    def test_wrong_element(self):
        with self.assertRaises(ValueError):
             create_Lines('1','1','WALL','2')

    def test_element_ids_middle_point(self):

        def find_middle_point(coord):
            # search for point located at center
            center=np.array([0,0.5,0.0])
            # search radius 
            d=0.1
            if(np.sqrt(np.linalg.norm(coord-center))<d):
                return True
            return False

        filename='test_files/read_test.dat'
        element_type="WALLQ4PORO"

        nodes=np.array(get_Nodecoords_of_File(filename))
        elements=np.array(get_Elements_of_File(filename,'---STRUCTURE ELEMENTS',element_type))

        element_ids=get_ElementIDs(elements,nodes,find_middle_point)
        assert([[1, [4]]]==element_ids)

    def test_element_ids_multiple_points(self):

        def find_middle_point(coord):
            # search for point located between node 1 and 2
            center=np.array([0.25,0.0,0.0])

            # search radius 
            if(np.sqrt(np.linalg.norm(coord-center))<=0.5):
                return True
            return False

        filename='test_files/read_test.dat'
        element_type="WALLQ4PORO"

        nodes=np.array(get_Nodecoords_of_File(filename))
        elements=np.array(get_Elements_of_File(filename,'---STRUCTURE ELEMENTS',element_type))
        
        element_ids=get_ElementIDs(elements,nodes,find_middle_point)
        # found index 1,2 of element 1 and  in element 2 at index 1
        assert([[1, [1, 2]], [2, [1]]]==element_ids)    


    def test_newline_creation(self):

        def find_middle_point(coord):
            # search for point located between node 1 and 2
            center=np.array([0.25,0.0,0.0])

            # search radius 
            if(np.sqrt(np.linalg.norm(coord-center))<=0.5):
                return True
            return False

        filename='test_files/read_test.dat'
        element_type="WALLQ4PORO"
        permea_coeffs=[3, 10]
        element_ids=[[1, [1, 2]], [2, [1]]]
        adjustments=create_Lines(filename,element_ids,element_type,permea_coeffs)
        #print(adjustments)
        results=[['1 WALLQ4PORO QUAD4 1 2 5 6 MAT 1 KINEM nonlinear EAS none THICK 0.1 STRESS_STRAIN plane_strain GP 2 2 POROANISODIR1 1.0 0.0 POROANISODIR2 0.0 1.0 POROANISONODALCOEFFS1 3.0 3.0 1.0 1.0 POROANISONODALCOEFFS2 2.5 2.5 1.0 1.0\n', '1 WALLQ4PORO QUAD4 1 2 5 6 MAT 1 KINEM nonlinear EAS none THICK 0.1 STRESS_STRAIN plane_strain GP 2 2 POROANISODIR1 1.0 0.0 POROANISODIR2 0.0 1.0 POROANISONODALCOEFFS1 3 3 1.0 1.0 POROANISONODALCOEFFS2 10 10 1.0 1.0\n'], ['2 WALLQ4PORO QUAD4 2 3 4 5 MAT 1 KINEM nonlinear EAS none THICK 0.1 STRESS_STRAIN plane_strain GP 2 2 POROANISODIR1 1.0 0.0 POROANISODIR2 0.0 1.0 POROANISONODALCOEFFS1 2.0 2.0 1.0 1.0 POROANISONODALCOEFFS2 1.5 1.5 1.0 1.0\n', '2 WALLQ4PORO QUAD4 2 3 4 5 MAT 1 KINEM nonlinear EAS none THICK 0.1 STRESS_STRAIN plane_strain GP 2 2 POROANISODIR1 1.0 0.0 POROANISODIR2 0.0 1.0 POROANISONODALCOEFFS1 3 2.0 1.0 1.0 POROANISONODALCOEFFS2 10 1.5 1.0 1.0\n']]
        # find node 1,2 located at element 1 and  in element 2 node 1
        assert(adjustments==results)    
    
    def test_write_empty_file(self):
        filename='test_files/read_test.dat'
        with self.assertRaises(ValueError):
            update_File_with_Lines(filename,'')
   
      
    def test_is_in_coil(self):
        centers=[np.array([8.4,0.8,0.0]),np.array([6.0,1.0,0.0]),np.array([7.0,2.0,0.0]),np.array([5.3,1.25,0.0]),np.array([5.6,3.0,0.0]),np.array([8.0,3.0,0.0]),np.array([8.0,2.0,0.0]),np.array([7.0,1.0,0.0]),np.array([7.0,3.0,0.0]),np.array([6.0,2.0,0.0])]
        for c in centers:
            print(c)

    def test_is_in_web(self):
        assert(is_web([4.5,1.1,0]))
        assert(is_web([4.5,1.5,0]))
        assert(is_web([5.07,0.89,0]))
        assert(is_web([5.1,1.19,0]))

if __name__ == '__main__':
    unittest.main()