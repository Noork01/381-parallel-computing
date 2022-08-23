#!/usr/bin/env python3
from mpi4py import MPI

# application-related data
a = None
b = None
n = None
h = None
result = None

comm_world = MPI.COMM_WORLD
# MPI-related data
my_rank = comm_world.Get_rank() # or my_rank = MPI.COMM_WORLD.Get_rank()
num_procs = comm_world.Get_size() # or ditto ...

if (my_rank == 0):
   # reading the application data "n" from stdin only by process 0:
   a = int(input("Enter the left endpoint: "))
   b = int(input("Enter the right endpoint: "))
   n = int(input("Enter the number of elements (n): "))

# broadcasting the content of variable "n" in process 0
# into variables "n" in all other processes:
a = comm_world.bcast(a, root=0)
b = comm_world.bcast(b, root=0)
n = comm_world.bcast(n, root=0)

h = (b-a)/n
local_n = int(n/num_procs)
local_a = a + my_rank*local_n*h
local_b = local_a + local_n*h

def Trap(a,b,n,h):
   estimate = (a**2 + b**2)/2
   for i in range(1,n-1):
      estimate += (a+(i*h))**2
   estimate *= h
   return estimate

local_calc = Trap(local_a,local_b,local_n,h)

if (my_rank != 0):
   # sending some results from all processes (except 0) to process 0:
   comm_world.send(local_calc, dest=0, tag=99)
else:
   # receiving all these messages and, e.g., printing them
   rank = None
   for rank in range(1,num_procs):
      result = comm_world.recv(source=rank, tag=99)
      local_calc += result

if (my_rank == 0):
   print(f"estimate of x^2 from {a} to {b} is {local_calc}")
