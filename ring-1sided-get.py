import numpy as np
from mpi4py import MPI

rcv_buf = np.empty((), dtype=np.intc) # uninitialized 0 dimensional integer array
status = MPI.Status()

comm_world = MPI.COMM_WORLD
my_rank = comm_world.Get_rank()
size = comm_world.Get_size()

right = (my_rank+1) % size;
left  = (my_rank-1+size) % size;
# ... this SPMD-style neighbor computation with modulo has the same meaning as:
# right = my_rank + 1
# if (right == size):
#    right = 0
#    left = my_rank - 1
# if (left == -1):
#    left = size-1

sum = 0
snd_buf = np.array(my_rank, dtype=np.intc) # 0 dimensional integer array with 1 element initialized with the value of my_rank

win = MPI.Win.Create(memory=snd_buf, comm=comm_world)

for i in range(size):
    win.Fence()
    win.Get(origin=rcv_buf, target_rank=(left+i)%size)
    win.Fence()
    sum += rcv_buf
win.Free()
print(f"PE{my_rank}:\tSum = {sum}")
