# QDL Runtime Interpreter

class QDLRuntime:
    def __init__(self):
        self.regs = [0] * 16  # General-purpose registers
        self.pc = 0
        self.prog = []
        self.stack = []
        self.loop_stack = []
        self.labels = {}
        self.output = []
        self.input_queue = []
        self.memory = {}  # Indexed memory for state
        self.modules = {}

    def load_program(self, bytecode):
        self.prog = bytecode
        for i, instr in enumerate(bytecode):
            if instr[0] == ":":
                self.labels[instr[1]] = i

    def run(self):
        while self.pc < len(self.prog):
            instr = self.prog[self.pc]
            if instr[0] == ":":
                self.pc += 1
                continue
            op = instr[0]
            args = instr[1:]
            self.dispatch(op, args)
            self.pc += 1

    def dispatch(self, op, args):
        r = self.regs
        if op == 'A': r[int(args[0])] = int(args[1])                              # Assign
        elif op == 'B': r[int(args[0])] += r[int(args[1])]                        # Add
        elif op == 'C': r[int(args[0])] -= r[int(args[1])]                        # Subtract
        elif op == 'D': r[int(args[0])] *= r[int(args[1])]                        # Multiply
        elif op == 'E': r[int(args[0])] //= max(1, r[int(args[1])])              # Divide
        elif op == 'F': r[int(args[0])] <<= int(args[1])                          # Shift left
        elif op == 'G': r[int(args[0])] >>= int(args[1])                          # Shift right
        elif op == 'H': self.output.append(r[int(args[0])])                       # Output
        elif op == 'I': r[int(args[0])] = self.input_queue.pop(0) if self.input_queue else 0
        elif op == 'J': self.pc = self.labels[args[0]] - 1                         # Jump
        elif op == 'K':
            if r[int(args[0])] == 0: self.pc = self.labels[args[1]] - 1           # Jump if zero
        elif op == 'L': self.loop_stack.append((self.pc, int(args[0])))           # Loop start
        elif op == 'M':
            start_pc, test_reg = self.loop_stack[-1]
            r[test_reg] -= 1
            if r[test_reg] > 0: self.pc = start_pc
            else: self.loop_stack.pop()
        elif op == 'N': pass                                                       # No-op
        elif op == 'O':
            self.stack.append(self.pc)
            self.pc = self.labels[args[0]] - 1                                     # Call module
        elif op == 'P': self.pc = self.stack.pop()                                 # Return
        elif op == 'Q': self.memory[args[0]] = r[int(args[1])]                     # Store in memory
        elif op == 'R': r[int(args[0])] = self.memory.get(args[1], 0)              # Load from memory
        elif op == 'X': print("DEBUG:", self.regs, self.memory)                   # Debug

    def get_output(self):
        return self.output

    def queue_input(self, value):
        self.input_queue.append(value)

    def reset(self):
        self.__init__()

# --- QDL Compiler ---
def compile_qdl(script: str):
    lines = script.strip().split('\n')
    bytecode = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        bytecode.append(parts)
    return bytecode
