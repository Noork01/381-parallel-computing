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

for i in range(size):
   request = comm_world.Issend((snd_buf, 1, MPI.INT), dest=right, tag=17)
   # WRONG program, because if MPI_Send is implemented with a
   # synchronous communication protocol then this program will deadlock!
   comm_world.Recv((rcv_buf, 1, MPI.INT), source=left,  tag=17, status=status)
   np.copyto(snd_buf, rcv_buf)
   sum += rcv_buf
print(f"PE{my_rank}:\tSum = {sum}")
