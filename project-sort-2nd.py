import math
import random
import time

from mpi4py import MPI
import numpy as np

start = time.time()
comm_world = MPI.COMM_WORLD
# MPI-related data
my_rank = comm_world.Get_rank() # or my_rank = MPI.COMM_WORLD.Get_rank()
num_procs = comm_world.Get_size() # or ditto ...

n = 1000
b = num_procs
length = int(n/b)

localRandomArray = np.random.randint(1000, size=length)

# random array in each thread
localsamplesize = 10

localsampleindex = np.empty(localsamplesize,dtype=np.intc)
localsample = np.empty(localsamplesize,dtype=np.intc)


for i in range(localsamplesize):
    sub = random.randint(0,length-1)
    while sub in localsampleindex:
        sub = random.randint(0, length-1)
    localsampleindex[i] = sub
    localsample[i] = localRandomArray[sub]


#transposition sort


sorted_array = localsample.tolist()
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
    keys = keys[0:localsamplesize]
    #print(f"{my_rank}:lower:recieved{recv_keys}:mine{my_keys}:new{keys}")
    return keys



def keep_higher(my_keys,recv_keys):
    count = 0
    keys = []
    keys.extend(my_keys)
    keys.extend(recv_keys)
    mergeSort(keys)
    keys = keys[localsamplesize:localsamplesize*2]
    #print(f"{my_rank}:higher:recieved{recv_keys}:mine{my_keys}:new{keys}")
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

#print(f"{my_rank}:final {sorted_array}")

#find splitters and send them

snd_buf = np.array(sorted_array[localsamplesize-1], dtype=np.intc)
rcv_buf = np.empty((), dtype=np.intc)

for i in range(b-1):
    if(my_rank == i):
        request = comm_world.Issend((snd_buf, 1, MPI.INT), dest=i+1, tag=17)
    if(my_rank == i+1):
        comm_world.Recv((rcv_buf, 1, MPI.INT), source=i, tag=17, status=MPI.Status())

my_splitter = 0

for i in range(1,b):
    if(my_rank == i):
        my_splitter = int((rcv_buf + sorted_array[0])/2)

#print(f"{my_rank}:{my_splitter}")

splitters = np.array([0], dtype=np.intc)
#sending the splitters
if (my_rank != 0):
   # sending some results from all processes (except 0) to process 0:
   comm_world.send(my_splitter, dest=0, tag=99)
else:
   # receiving all these messages and, e.g., printing them
   rank = None
   for rank in range(1,num_procs):
      result = comm_world.recv(source=rank, tag=99)
      splitters = np.append(splitters,np.array([result]))
splitters = np.append(splitters,np.array([1000]))

splitters = comm_world.bcast(splitters, root=0)

#print(f"{my_rank}:{splitters}")
##################################################


#butterfly algorithm
p = int(math.log2(num_procs))
which = num_procs >> 1
x = int(num_procs/2)
keeparray = localRandomArray



for i in range(p):
    #print(f"rank {my_rank}: checking:{keeparray}")
    #print(f"{my_rank}:check:{keeparray}")
    partner = my_rank ^ x
    tempkeep = []
    tempsend = []
    if(my_rank < partner):
        for i in range(len(keeparray)):
            if(keeparray[i]<splitters[which]):
                tempkeep.append(keeparray[i])
            else:
                tempsend.append(keeparray[i])
    else:
        for i in range(len(keeparray)):
            if(keeparray[i]>splitters[which]):
                tempkeep.append(keeparray[i])
            else:
                tempsend.append(keeparray[i])
    received_array = None
    received_array = comm_world.sendrecv(sendobj=tempsend, dest=partner, source=partner, recvbuf=received_array)
    #print(received_array)
    keeparray = np.append(tempkeep,received_array)
    #print(type(keeparray))
    #print(which)
    x = x >> 1
    if (my_rank < partner):
        which -= x
    else:
        which += x
    #print(which)


#each bucket is now separated by splitters

keeparray = sorted(keeparray)


#sending to process 0

if (my_rank != 0):
   # sending some results from all processes (except 0) to process 0:
   comm_world.send(keeparray, dest=0, tag=99)
else:
   # receiving all these messages and, e.g., printing them
   rank = None
   for rank in range(1,num_procs):
      result = comm_world.recv(source=rank, tag=99)
      keeparray.append(result)
if (my_rank == 0):
   #print(f"{my_rank}: final: {keeparray}")
   print(f"num processes: {num_procs}: runtime: {time.time()-start}")
