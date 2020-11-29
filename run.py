# A cli to use the simulator
from cache_sim import Computer
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--protocol', type=str, default='MSI')
parser.add_argument('--cacheSz', type=int, default=64)
parser.add_argument('--blockSz', type=int, default=16)
parser.add_argument('--a', type=int, default=1)
parser.add_argument('--testcase', type=int, default='1')

args = parser.parse_args()

instructions = []
config = f'testcases/testcase{args.testcase}/config'
file1 = open(config, 'r')
n = int(file1.readline().strip())
files = [f'testcases/testcase{args.testcase}/p{i}.trace' for i in range(n)]
for f in files:
    instructions_per_core = []
    file1 = open(f, 'r')
    count = 0
  
    while True: 
        count += 1 
        line = file1.readline().strip() 
        if not line: 
            break
        instruction = line.split(' ')
        print(instruction)
        instruction[0] = 'READ' if instruction[0] == 'r' else 'WRITE'
        instruction[1] = int(instruction[1], 16)
        instructions_per_core.append(instruction)
    instructions.append(instructions_per_core) 
# print(instructions)

computer = Computer(args.protocol, n, instructions, args.cacheSz, args.blockSz, args.a)

computer.run()