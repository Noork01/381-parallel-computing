from mpi4py import MPI
import numpy as np


comm_world = MPI.COMM_WORLD
# MPI-related data
my_rank = comm_world.Get_rank() # or my_rank = MPI.COMM_WORLD.Get_rank()
num_procs = comm_world.Get_size() # or ditto ...



arr = np.array([15,11,9,16,3,14,8,7,4,6,12,10,5,2,13,1])

local_array = arr[int(my_rank*int(arr.size/num_procs)):int((my_rank+1)*int(arr.size/num_procs))]
#print(f"{my_rank}:{local_array}")
#1st phase
sorted_array = local_array.tolist()
sorted_array.sort()

def compute_partner(phase, rank):
    partner = None
    if phase % 2 == 0:
        if rank % 2 != 0:
            partner = rank - 1
        else:
            partner = rank + 1
    else:
        if rank % 2 != 0:
            partner = rank + 1
        else:
            partner = rank - 1
    if (partner == -1) or (partner == num_procs):
        partner = MPI.PROC_NULL
    return partner


def mergeSort(arr):
    if len(arr) > 1:

        # Finding the mid of the array
        mid = len(arr) // 2

        # Dividing the array elements
        L = arr[:mid]

        # into 2 halves
        R = arr[mid:]

        # Sorting the first half
        mergeSort(L)

        # Sorting the second half
        mergeSort(R)

        i = j = k = 0

        # Copy data to temp arrays L[] and R[]
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1

        # Checking if any element was left
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1

def keep_smaller(my_keys,recv_keys):
    count = 0
    keys = []
    keys.extend(my_keys)
    keys.extend(recv_keys)
    mergeSort(keys)
    keys = keys[0:4]
    print(f"{my_rank}:lower:recieved{recv_keys}:mine{my_keys}:new{keys}")
    return keys



def keep_higher(my_keys,recv_keys):
    count = 0
    keys = []
    keys.extend(my_keys)
    keys.extend(recv_keys)
    mergeSort(keys)
    keys = keys[4:8]
    print(f"{my_rank}:higher:recieved{recv_keys}:mine{my_keys}:new{keys}")
    return keys

for phase in range(num_procs):
    partner = compute_partner(phase,my_rank)
    #print(f"{my_rank}:{partner}")

    if(partner > -1 and partner < num_procs):
        received_array = None
        #print(f"{my_rank}:{sorted_array}")
        received_array = comm_world.sendrecv(sendobj=sorted_array, dest=partner, source=partner, recvbuf=received_array)
        #print(f"{my_rank}:{received_array}")

        if(my_rank < partner):
            sorted_array = keep_smaller(sorted_array, received_array)
        else:
            sorted_array = keep_higher(sorted_array, received_array)

print(f"{my_rank}:final {sorted_array}")


