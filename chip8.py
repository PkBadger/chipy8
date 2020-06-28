from random import randrange

class Chip8:
    chip8_fontset = [
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
    ]

    def callOrDisplayOrFlow(self, opcode):
        def call(opcode):
            pass
        
        def display(opcode):
            self.gfx = [0] * 2048
            self.pc += 2

        def flow(opcode):
            self.pc = self.stack.pop() + 2

        codes = {
            0x00E0: display,
            0x00EE: flow
        }

        funcToCall = codes[opcode] or call

        funcToCall(opcode)

    def jumpFlow(self, opcode):
        #print(self.pc)
        self.pc = opcode & 0x0FFF % 4096

    def subroutineFlow(self, opcode):
        self.stack.append(self.pc)
        self.pc = opcode & 0x0FFF

    def setConst(self, opcode):
        index = int((opcode & 0x0F00) >> 8)
        self.V[index] = opcode & 0x00FF
        self.pc = self.pc + 2

    def setMem(self, opcode):
        value = opcode & 0x0FFF
        self.I = value
        self.pc = self.pc + 2

    def dispDraw(self, opcode):
        x = self.V[(opcode & 0x0F00) >> 8]
        y = self.V[(opcode & 0x00F0) >> 4]
        height = opcode & 0x000F
        pixel = None
        self.V[0xF] = 0

        for yline in range(height):
            pixel = self.memory[self.I + yline]
            for xline in range(8):
                if((pixel & (0x80 >> xline)) != 0):
                    index = (x + xline + ((y+yline) * 64)) % 2048
                    if(self.gfx[index] == 1):
                        self.V[0xF] = 1
                    self.gfx[index] = self.gfx[index] ^ 1
        
        self.drawFlag = True
        self.pc = self.pc + 2

    def selectFOpcode(self, opcode):
        def bcd(opcode):
            index = int((opcode & 0x0F00) >> 8)
            value = self.V[index]
            ones = value % 10
            value = value // 10
            tens = value % 10
            hundreds = value // 10
            self.memory[self.I] = hundreds
            self.memory[self.I + 1] = tens
            self.memory[self.I + 2] = ones

            self.pc = self.pc + 2

        def reg_load(opcode):
            index = int((opcode & 0x0F00) >> 8)
            for x in range(index + 1):
                self.V[x] = self.memory[self.I + x]

            self.pc = self.pc + 2

        def sprite_addr(opcode):
            index = int((opcode & 0x0F00) >> 8)
            self.I = self.V[index] * 5

            self.pc = self.pc + 2

        def delay_timer(opcode):
            index = int((opcode & 0x0F00) >> 8)
            self.delay_timer = self.V[index]

            self.pc = self.pc + 2

        def sound_timer(opcode):
            index = int((opcode & 0x0F00) >> 8)
            self.sound_timer = self.V[index]

            self.pc = self.pc + 2         

        def get_delay(opcode):
            index = int((opcode & 0x0F00) >> 8)
            self.V[index] = self.delay_timer 

            self.pc = self.pc + 2

        def get_key(opcode):
            index = int((opcode & 0x0F00) >> 8)
            self.paused = True
            def callback(key):
                self.V[index] = key
                self.paused = False
                self.pc = self.pc + 2
            self.callback = callback        

        def reg_dump(opcode):
            index = int((opcode & 0x0F00) >> 8)
            for x in range(index + 1):
                self.memory[self.I + x] = self.V[x]
            self.pc = self.pc + 2

        def sumToI(opcode):
            index = int((opcode & 0x0F00) >> 8)
            self.I = self.I + self.V[index]
            self.pc = self.pc + 2

        codes = {
            0x0007: get_delay,
            0x000A: get_key,
            0x0015: delay_timer,
            0x0018: sound_timer,
            0x001e: sumToI,
            0x0029: sprite_addr,
            0x0033: bcd,
            0x0055: reg_dump,
            0x0065: reg_load,
            
        }

        lastByte = opcode & 0x00FF

        funcToCall = codes.get(lastByte, self.default)

        funcToCall(opcode)
        #exit()

    def sumConst(self, opcode):
        index = int((opcode & 0x0F00) >> 8)
        self.V[index] = (self.V[index] + (opcode & 0x00FF)) % 256
        self.pc = self.pc + 2

    def eqlCond(self, opcode):
        index = int((opcode & 0x0F00) >> 8)
        value = opcode & 0x00FF
        toSkip = 2
        if (self.V[index] == value): toSkip = 4

        self.pc = self.pc + toSkip

    def vEqlCond(self, opcode):
        indexX = int((opcode & 0x0F00) >> 8)
        indexY = int((opcode & 0x00F0) >> 4)
        toSkip = 2
        if (self.V[indexX] == self.V[indexY]): toSkip = 4

        self.pc = self.pc + toSkip

    def notEqlCond(self, opcode):
        index = int((opcode & 0x0F00) >> 8)
        value = opcode & 0x00FF
        toSkip = 2
        if (self.V[index] != value): toSkip = 4

        self.pc = self.pc + toSkip

    def notEqlVyCond(self, opcode):
        indexX = int((opcode & 0x0F00) >> 8)
        indexY = int((opcode & 0x00F0) >> 4)
        toSkip = 2
        if (self.V[indexX] != self.V[indexY]): toSkip = 4

        self.pc = self.pc + toSkip

    def rand(self, opcode):
        index = int((opcode & 0x0F00) >> 8)
        value = opcode & 0x00FF
        randNumber = randrange(255)

        self.V[index] = randNumber & value

        self.pc = self.pc + 2

    def select8OpCode(self, opcode):
        def andBitOp(opcode):
            indexX = int((opcode & 0x0F00) >> 8)
            indexY = int((opcode & 0x00F0) >> 4)

            self.V[indexX] = self.V[indexX] & self.V[indexY] 

            self.pc = self.pc + 2

        def sumWithCarry(opcode):
            indexX = int((opcode & 0x0F00) >> 8)
            indexY = int((opcode & 0x00F0) >> 4)

            result = self.V[indexX] + self.V[indexY]

            self.V[15] = 1 if result // 256 == 1 else 0

            self.V[indexX] = result % 256

            self.pc = self.pc + 2

        def assign(opcode):
            indexX = int((opcode & 0x0F00) >> 8)
            indexY = int((opcode & 0x00F0) >> 4)

            self.V[indexX] = self.V[indexY]

            self.pc = self.pc + 2

        def substractWithCarry(opcode):
            indexX = int((opcode & 0x0F00) >> 8)
            indexY = int((opcode & 0x00F0) >> 4)

            result = self.V[indexX] - self.V[indexY]

            self.V[15] = 0 if result < 0 else 1

            self.V[indexX] = 256 + result if result < 0 else result

            self.pc = self.pc + 2

        def orBitOp(opcode):
            indexX = int((opcode & 0x0F00) >> 8)
            indexY = int((opcode & 0x00F0) >> 4)

            self.V[indexX] = self.V[indexX] | self.V[indexY]

            self.pc = self.pc + 2

        def xorBitOp(opcode):
            indexX = int((opcode & 0x0F00) >> 8)
            indexY = int((opcode & 0x00F0) >> 4)

            self.V[indexX] = self.V[indexX] ^ self.V[indexY]

            self.pc = self.pc + 2

        def shiftRight(opcode):
            index = int((opcode & 0x0F00) >> 8)

            self.V[15] = (self.V[index] & 0x1)

            self.V[index] = self.V[index] >> 1

            self.pc = self.pc + 2

        def shiftLeft(opcode):
            index = int((opcode & 0x0F00) >> 8)

            self.V[15] = (self.V[index] & 0x80)

            self.V[index] = (self.V[index] << 1) % 256

            self.pc = self.pc + 2

        def substractVY(opcode):
            indexX = int((opcode & 0x0F00) >> 8)
            indexY = int((opcode & 0x00F0) >> 4)

            result = self.V[indexY] - self.V[indexX]

            self.V[15] = 0 if result < 0 else 1

            self.V[indexX] = 256 + result if result < 0 else result

            self.pc = self.pc + 2

        codes = {
            0x0000: assign,
            0x0001: orBitOp,
            0x0002: andBitOp,
            0x0003: xorBitOp,
            0x0004: sumWithCarry,
            0x0005: substractWithCarry,
            0x0006: shiftRight,
            0x0007: substractVY,
            0x000e: shiftLeft,
        }

        lastByte = opcode & 0x000F

        funcToCall = codes.get(lastByte, self.default)

        funcToCall(opcode)

    def keyCond(self, opcode):
        def eqlKey(opcode):
            index = int((opcode & 0x0F00) >> 8)
            toSkip = 2
            if(self.key[self.V[index]] == 1): toSkip = 4
            self.pc = self.pc + toSkip

        def notEqlKey(opcode):
            index = int((opcode & 0x0F00) >> 8)
            toSkip = 2
            if(self.key[self.V[index]] != 1): toSkip = 4
            self.pc = self.pc + toSkip

        codes = {
            0x009E: eqlKey,
            0x00A1: notEqlKey,
        }

        lastByte = opcode & 0x00FF

        funcToCall = codes.get(lastByte, self.default)

        funcToCall(opcode)

    def juptToAdress(self, opcode):
        adress = (opcode & 0x0FFF) % 4096

        self.pc = self.V[0] + adress    
    
    def default(self, opcode):
        print("Unknown opcode: " + hex(opcode))
  
    def getOpcodeFunction(self, opcode):
        opcodes = {
            0x0000: self.callOrDisplayOrFlow,
            0x1000: self.jumpFlow,
            0x2000: self.subroutineFlow,
            0x3000: self.eqlCond,
            0x4000: self.notEqlCond,
            0x5000: self.vEqlCond,
            0x6000: self.setConst,
            0x7000: self.sumConst,
            0x8000: self.select8OpCode,
            0x9000: self.notEqlVyCond,
            0xa000: self.setMem,
            0xb000: self.juptToAdress,
            0xc000: self.rand,
            0xd000: self.dispDraw,
            0xe000: self.keyCond,
            0xF000: self.selectFOpcode,
        }

        return opcodes.get(opcode, self.default)

    def __init__(self):
        self.pc = 0x200
        self.opcode = 0
        self.I = 0
        self.sp = 0
        self.stack = []
        self.memory = [0] * 4096
        self.drawFlag = False
        self.gfx = [0] * 2048
        self.delay_timer = 0
        self.sound_timer = 0
        self.key = [0] * 16
        self.V = bytearray(16)
        self.paused = False
        self.callback = None
        self.soundFlag = False

        for i in range(80):
            self.memory[i] = self.chip8_fontset[i]


    def emulateCycle(self): 
        current = self.memory[self.pc]
        nextByte = self.memory[self.pc + 1]
        opcode = current << 8 | nextByte

        #print(hex(opcode))

        firt4Bits = opcode & 0xF000

        funcToCall = self.getOpcodeFunction(firt4Bits)

        if(not self.paused):
            funcToCall(opcode)

            if(self.delay_timer > 0): self.delay_timer = self.delay_timer - 1
            if(self.sound_timer > 0): 
                self.sound_timer = self.sound_timer - 1
                if(self.sound_timer == 0): self.soundFlag = True

            #self.printStatus()

    def loadGame(self, fileName):
        gameFile = open(fileName, 'rb')
        counter = 0

        byteArray = gameFile.read()

        for currentByte in byteArray:
            self.memory[counter + 512] = currentByte
            counter += 1

        gameFile.close() 

    def printStatus(self):
        json = {
            'V': [hex(v) for v in self.V],
            'stack':self.stack,
            'pc': self.pc,
            'i': self.I,
            'delay': self.delay_timer,
            'sound': self.sound_timer
        }

        print(json)        

if __name__ == '__main__':
    chip8 = Chip8()

    chip8.loadGame('c8games/TANK')

    chip8.emulateCycle()