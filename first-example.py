#!/usr/bin/env python3
from mpi4py import MPI

# application-related data
n = None
result = None

comm_world = MPI.COMM_WORLD
# MPI-related data
my_rank = comm_world.Get_rank() # or my_rank = MPI.COMM_WORLD.Get_rank()
num_procs = comm_world.Get_size() # or ditto ...

if (my_rank == 0):
   # reading the application data "n" from stdin only by process 0:
   n = int(input("Enter the number of elements (n): "))

# broadcasting the content of variable "n" in process 0 
# into variables "n" in all other processes:
n = comm_world.bcast(n, root=0)

# doing some application work in each process, e.g.:
result = 1.0 * my_rank * n
print(f"I am process {my_rank} out of {num_procs} handling the {my_rank}ith part of n={n} elements, result={result}")

if (my_rank != 0):
   # sending some results from all processes (except 0) to process 0:
   comm_world.send(result, dest=0, tag=99)
else:
   # receiving all these messages and, e.g., printing them 
   rank = None
   print(f"I'm proc 0: My own result is {result}") 
   for rank in range(1,num_procs):
      result = comm_world.recv(source=rank, tag=99)
      print(f"I'm proc 0: received result of process {rank} is {result}")
