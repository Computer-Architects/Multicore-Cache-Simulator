# A cli to use the simulator
from cache_sim import Computer
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--protocol', type=str, default='MSI')
parser.add_argument('--n', type=int, default=2)
parser.add_argument('--cacheSz', type=int, default=64)
parser.add_argument('--blockSz', type=int, default=16)
parser.add_argument('--a', type=int, default=1)
parser.add_argument('--instr', type=str, default='testcases/testcase1')

args = parser.parse_args()

instructions = []
files = [f'{args.instr}/p{i}.txt' for i in range(args.n)]
for f in files:
    instructions_per_core = []
    file1 = open(f, 'r')
    count = 0
  
    while True: 
        count += 1 
        line = file1.readline() 
        if not line: 
            break
        instruction = line.split(' ')
        instruction[0] = 'READ' if instruction[0] == 'r' else 'WRITE'
        instruction[1] = int(instruction[1], 16)
        instructions_per_core.append(instruction)
    instructions.append(instructions_per_core) 
# print(instructions)

computer = Computer(args.protocol, args.n, instructions, args.cacheSz, args.blockSz, args.a)

computer.run()