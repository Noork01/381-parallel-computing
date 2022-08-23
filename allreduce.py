import numpy as np
from mpi4py import MPI

rcv_buf = np.empty((), dtype=np.intc) # uninitialized 0 dimensional integer array
status = MPI.Status()

comm_world = MPI.COMM_WORLD
my_rank = comm_world.Get_rank()
size = comm_world.Get_size()

#sum = 0
snd_buf = np.array(my_rank, dtype=np.intc) # 0 dimensional integer array with 1 element initialized with the value of my_rank

comm_world.Allreduce(sendbuf=snd_buf, recvbuf=rcv_buf)

print(f"PE{my_rank}:\tSum = {rcv_buf}")
