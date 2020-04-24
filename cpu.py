"""CPU functionality."""

import sys

SP = 7

# Instructions
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL= 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100

# Masks
INSTRUCTION_MASK = 0b11000000
ALU_MASK = 0b00100000
AUTOINCREMENT_MASK = 0b00010000
LGE_MASK = 0b00000111

# CMP codes
L = 0b100
G = 0b10
E = 0b1

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.fl = 0b0000000

        self.reg[SP] = 0xf4

        self.pc = 0
        self.running = True

        self.branch_table = {
            LDI: self.LDI,
            PRN: self.PRN,
            HLT: self.HLT,
            PUSH: self.PUSH,
            POP: self.POP,
            CALL: self.CALL,
            RET: self.RET,
        }

    def LDI(self):
        register_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)

        self.reg[register_num] = value


    def PRN(self):
        register_num = self.ram_read(self.pc + 1)

        print(self.reg[register_num])

    def PUSH(self, call=False):
        # shift stack pointer down to the next empty slot
        self.reg[SP] -= 1

        if call:
            # push the address of pc + 2 to the stack
            self.ram_write(self.reg[SP], self.pc + 2)
        else:
            # push the value at pc + 1 to the stack
            register_num = self.ram_read(self.pc + 1)
            self.ram_write(self.reg[SP], self.reg[register_num])

    def POP(self, ret=False):
        register_num = self.ram_read(self.pc + 1)

        if ret:
            # set pc to the address stored at the top of the stack
            self.pc = self.ram_read(self.reg[SP])
        else:
            # pop the value at the top of the stack to a specific register number
            self.reg[register_num] = self.ram_read(self.reg[SP])

        # shift stack pointer up to the next item on the stack
        self.reg[SP] += 1
    
    def ADD(self, reg_a, reg_b):
        self.reg[reg_a] += self.reg[reg_b]
    
    def MUL(self, reg_a, reg_b):
        self.reg[reg_a] *= self.reg[reg_b]
    
    def CMP(self, reg_a, reg_b):
        if self.reg[reg_a] < self.reg[reg_b]:
            self.fl |= L
        else:
            self.fl &= 0b011

        if self.reg[reg_a] < self.reg[reg_b]:
            self.fl |= G
        else:
            self.fl &= 0b101

        if self.reg[reg_a] > self.reg[reg_b]:
            self.fl |= E
        else:
            self.fl &= 0b110
    
    def CALL(self):
        # set the pc to the value stored in the register number
        register_number = self.ram_read(self.pc + 1)
        self.PUSH(call=True)
        self.pc = self.reg[register_number]

    def RET(self):
        self.POP(ret=True)

    def HLT(self):
        self.running = False

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self, file_path):
        """Load a program into memory."""
        address = 0

        with open(file_path, 'r') as f:
            for line in f.readlines():
                line = line.split('#')[0].strip()
                if line.startswith(('0', '1')) and len(line) == 8:
                    instruction = int(line, 2)
                    self.ram_write(address, instruction)
                    address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op in self.branch_table:
            self.branch_table[op](reg_a, reg_b)
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while self.running:
            ir = self.ram_read(self.pc)
            instruction_length = ((ir & INSTRUCTION_MASK) >> 6 ) + 1
            is_alu = (ir & ALU_MASK) >> 5 == 0b1
            sets_pc = (ir & AUTOINCREMENT_MASK) >> 4 == 0b1

            if is_alu:
                register_a = self.ram_read(self.pc + 1)
                register_b = self.ram_read(self.pc + 2)
                self.alu(ir, register_a, register_b)

            elif ir in self.branc_table:
                self.dispatcher[ir]()

            else:
                self.running = False
            
            if not sets_pc:
                self.pc += instruction_length