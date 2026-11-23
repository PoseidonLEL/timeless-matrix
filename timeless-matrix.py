import numpy as np
class timless_matrix:

    '''----INITIAL OBJECT DEFINITION & BOOTUP----'''

    def __init__(self, array):
        self.array = np.float32(array) #Initial matrix
        if(self.array.ndim!=2):
            raise ValueError("Input must be a 2D matrix!")
        self.array_history = [self.array.copy()] #Starts the matrix history with the initial matrix


    '''----MATRIX MODIFICATION OPERATIONS----'''

    #Adds an entire row (axis=0) or column (axis=1) at a specified index.
    #Uses one allocation and slice assignments instead of np.insert to minimize overhead.
    def add_to_array(self,value,index=None,to_end=False,axis=0):
        if(not isinstance(axis,(int,np.integer)) or isinstance(axis,(bool,np.bool_)) or axis not in (0,1)):
            raise ValueError("axis must be 0 (row) or 1 (column)!")

        axisSize = self.array.shape[axis]
        if(to_end):
            index = axisSize
        elif(index is None):
            raise TypeError("An index is required unless to_end is True!")

        if(not isinstance(index,(int,np.integer)) or isinstance(index,(bool,np.bool_))):
            raise TypeError("index must be an integer!")
        if(index<0):
            index += axisSize
        if(index<0 or index>axisSize):
            raise IndexError("Index is outside the matrix!")

        values = np.asarray(value)
        if(values.ndim!=1 or values.size!=self.array.shape[1-axis]):
            raise ValueError("value must be a 1D row or column matching the other matrix dimension!")

        if(axis==0):
            newArray = np.empty((axisSize+1,self.array.shape[1]),dtype=np.float32)
            newArray[:index,:] = self.array[:index,:]
            newArray[index,:] = values
            newArray[index+1:,:] = self.array[index:,:]
        else:
            newArray = np.empty((self.array.shape[0],axisSize+1),dtype=np.float32)
            newArray[:,:index] = self.array[:,:index]
            newArray[:,index] = values
            newArray[:,index+1:] = self.array[:,index:]

        self.array = newArray
        self.update_history(newArray)


    #Removes an entire row (axis=0) or column (axis=1) at a specified index.
    #Uses one allocation and slice assignments instead of np.delete.
    def remove_from_array(self,index,axis=0):
        if(not isinstance(axis,(int,np.integer)) or isinstance(axis,(bool,np.bool_)) or axis not in (0,1)):
            raise ValueError("axis must be 0 (row) or 1 (column)!")

        axisSize = self.array.shape[axis]
        if(not isinstance(index,(int,np.integer)) or isinstance(index,(bool,np.bool_))):
            raise TypeError("index must be an integer!")
        if(index<0):
            index += axisSize
        if(index<0 or index>=axisSize):
            raise IndexError("Index is outside the matrix!")

        if(axis==0):
            newArray = np.empty((axisSize-1,self.array.shape[1]),dtype=np.float32)
            newArray[:index,:] = self.array[:index,:]
            newArray[index:,:] = self.array[index+1:,:]
        else:
            newArray = np.empty((self.array.shape[0],axisSize-1),dtype=np.float32)
            newArray[:,:index] = self.array[:,:index]
            newArray[:,index:] = self.array[:,index+1:]

        self.array = newArray
        self.update_history(newArray)


    #Rewinds selected matrix cells using (row,column) pairs from a past matrix.
    #A depth of 1 retrieves the instance immediately before the current one.
    def rewind(self,index,how_far_back):
        if(not isinstance(how_far_back,(int,np.integer)) or isinstance(how_far_back,(bool,np.bool_))):
            raise TypeError("how_far_back must be an integer!")
        if(how_far_back>=len(self.array_history)):
            raise IndexError("Requested history instance does not exist!")

        indices = np.asarray(index)
        if(indices.size==0):
            return
        if(indices.ndim==1 and indices.size==2):
            indices = indices.reshape(1,2)
        if(indices.ndim!=2 or indices.shape[1]!=2 or not np.issubdtype(indices.dtype,np.integer)):
            raise TypeError("index must contain integer (row,column) pairs!")

        rows = indices[:,0]
        cols = indices[:,1]
        pastArray = self.array_history[-1-how_far_back]
        if(np.any((rows>=pastArray.shape[0]) | (rows < -pastArray.shape[0]) |
                  (cols>=pastArray.shape[1]) | (cols < -pastArray.shape[1]))):
            raise IndexError("Index does not exist in this past instance!")
        if(np.any((rows>=self.array.shape[0]) | (rows < -self.array.shape[0]) |
                  (cols>=self.array.shape[1]) | (cols < -self.array.shape[1]))):
            raise IndexError("Index is outside the current matrix!")

        newArray = self.array.copy() #Never modify an earlier history instance in-place
        newArray[rows,cols] = pastArray[rows,cols]

        self.array = newArray
        self.update_history(newArray)


    '''----MATRIX HISTORY MANAGEMENT----'''

    #Adds the new matrix instance to the history. Every modification allocates a
    #new array, so the history can retain it without an additional full copy.
    def update_history(self,new_array):
        self.array_history.append(new_array)
