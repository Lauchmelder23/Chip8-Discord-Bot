from instruction import Opcode
import random
import time


class CPU:
    display = ["．"] * 64 * 32
    drawFlag = False

    memory = [0x00] * 4096
    stack = [0x00] * 12
    V = [0x00] * 0x10
    PC = 0x200
    SP = 0x00
    I = 0x0000

    delay_timer = 0x00
    sound_timer = 0x00
    tick_timer = int(round(time.time() * 1000))

    interrupt = True
    jumps = 0

    instruction = Opcode

    def load_rom(self, rom: str):
        with open(rom, "rb") as f:
            byte = f.read(1)
            offset = 0
            while byte != b"":
                self.memory[0x200 + offset] = int.from_bytes(byte, byteorder='little')
                offset += 1
                byte = f.read(1)

    def reset(self):
        self.display = ["．"] * 64 * 32
        self.drawFlag = False

        self.memory = [0x00] * 4096
        self.stack = [0x00] * 12
        self.V = [0x00] * 0x10
        self.PC = 0x200
        self.SP = 0x00
        self.I = 0x0000

        self.delay_timer = 0x00
        self.sound_timer = 0x00

        self.interrupt = True
        self.jumps = 0

        self.instruction = Opcode
        self.tick_timer = int(round(time.time() * 1000))

    def tick(self):
        if self.jumps >= 5 and self.drawFlag is False:
            self.interrupt = True
        self.execute(self, Opcode((self.memory[self.PC] << 8) | self.memory[self.PC + 1]))

        # print(time.localtime(time.time())[6])
        if (int(round(time.time() * 1000)) - self.tick_timer) >= 1000 / 60:
            if self.delay_timer is not 0:
                self.delay_timer -= 1
            if self.sound_timer is not 0:
                self.sound_timer -= 1
            self.tick_timer = int(round(time.time() * 1000))

    def execute(self, opc: Opcode):
        self.instruction = opc
        print(hex(self.instruction.op))

        if opc.i == 0x0:        # multi case
            if opc.kk == 0xE0:
                self.display = ["．"] * 64 * 32
                self.PC += 2
                print("Screen cleared")
                self.jumps = 0
                return

            if opc.kk == 0xEE:      # return from subroutine
                self.SP -= 1
                self.PC = self.stack[self.SP]
                self.PC += 2
                print("Returned from subroutine")
                self.jumps = 0
                return

        if opc.i == 0x1:        # 1NNN: Jump to address NNN
            if hex(opc.nnn) is 0x349:
                print("klklklkl")
            self.PC = opc.nnn
            print("=>Jumped to address " + hex(opc.nnn))
            self.jumps += 1
            return

        if opc.i == 0x2:        # 2NNN Call subroutnie at NNN
            self.stack[self.SP] = self.PC
            self.SP += 1
            self.PC = self.instruction.nnn
            print("=>Called subroutine at " + str(hex(self.instruction.nnn)))
            self.jumps = 0
            return

        if opc.i == 0x3:        # 3XKK: Skip next instruction if VX == KK
            if self.V[self.instruction.x] == self.instruction.kk:
                self.PC += 4
                print("V" + str(self.instruction.x) + " == KK"
                      + " [" + str(self.V[self.instruction.x]) + " == " + str(self.instruction.kk)
                      + "] || Skipped instruction")
            else:
                self.PC += 2
                print("V" + str(self.instruction.x) + " != KK"
                      + " [" + str(self.V[self.instruction.x]) + " != " + str(self.instruction.kk)
                      + " || Didn't skip instruction")
            self.jumps = 0
            return

        if opc.i == 0x4:  # 4XKK: Skip next instruction if VX != KK
            if self.V[self.instruction.x] != self.instruction.kk:
                self.PC += 4
                print("V" + str(self.instruction.x) + " != KK"
                      + " [" + str(self.V[self.instruction.x]) + " != " + str(self.instruction.kk)
                      + "] || Skipped instruction")
            else:
                self.PC += 2
                print("V" + str(self.instruction.x) + " == KK"
                      + " [" + str(self.V[self.instruction.x]) + " == " + str(self.instruction.kk)
                      + " || Didn't skip instruction")
            self.jumps = 0
            return

        if opc.i == 0x5:        # 5XY0: Skip next instruction if VX == VY
            if self.V[self.instruction.x] == self.V[self.instruction.y]:
                self.PC += 4
                print("V" + str(self.instruction.x) + " == V" + str(self.instruction.y)
                      + " [" + str(self.V[self.instruction.x]) + " == " + str(self.V[self.instruction.y])
                      + "] || Skipped instruction")
            else:
                self.PC += 2
                print("V" + str(self.instruction.x) + " != V" + str(self.instruction.y)
                      + " [" + str(self.V[self.instruction.x]) + " != " + str(self.V[self.instruction.y])
                      + " || Didn't skip instruction")
            self.jumps = 0
            return

        if opc.i == 0x6:        # 6XKK: Set VX to KK
            self.V[self.instruction.x] = opc.kk
            self.PC += 2
            print("=>Set V" + str(self.instruction.x) + " to " + str(opc.kk))
            self.jumps = 0
            return

        if opc.i == 0x7:        # 7XKK: Set VX = VX + KK
            self.V[self.instruction.x] = (self.V[self.instruction.x] + self.instruction.kk) & 0xFF
            self.PC += 2
            print("=>Added V" + str(self.instruction.x) + " and KK ("
                  + str(self.instruction.kk) + ") = " + str(self.V[self.instruction.x]))
            self.jumps = 0
            return

        if opc.i == 0x8:        # Multi Case
            if opc.n == 0x0:        # 8XY0: VX = VY
                self.V[self.instruction.x] = self.V[self.instruction.y]
                self.PC += 2
                print("=>Set V" + str(self.instruction.x) + " = V" + str(self.instruction.y) + " ("
                      + str(self.V[self.instruction.x]) + ")")
                self.jumps = 0
                return

            if opc.n == 0x2:        # 8XY2: VX = VX AND VY
                self.V[self.instruction.x] = (self.V[self.instruction.x] & self.instruction.y)
                self.PC += 2
                print("=>ANDed V" + str(self.instruction.x) + " and V" + str(self.instruction.y) + "("
                      + str(self.V[self.instruction.y]) + ") = " + str(self.V[self.instruction.x]))
                self.jumps = 0
                return

            if opc.n == 0x3:        # 8XY3: Set VX = VX XOR VY
                self.V[self.instruction.x] = self.V[self.instruction.x] ^ self.V[self.instruction.y]
                self.PC += 2
                print("=>XORed V" + str(self.instruction.x) + " and V" + str(self.instruction.y) + "("
                      + str(self.V[self.instruction.y]) + ") = " + str(self.V[self.instruction.x]))
                self.jumps = 0
                return

            if opc.n == 0x4:        # 8XY4: Set VX = VX + VY. Set Carry if overflow
                self.V[0xF] = 0
                if self.V[self.instruction.y] > (255 - self.V[self.instruction.x]):
                    self.V[0xF] = 1

                self.V[self.instruction.x] = (self.V[self.instruction.x] + self.V[self.instruction.y]) & 0xFF
                self.PC += 2
                print("=>Added V" + str(self.instruction.x) + " and V" + str(self.instruction.y) + "("
                      + str(self.V[self.instruction.y]) + ") = " + str(self.V[self.instruction.x])
                      + " ; Carry is now " + str(self.V[0xF]))
                self.jumps = 0
                return

            if opc.n == 0x5:        # 8XY5: Set VX = VX - VY. Set Flag if NOT borrow
                self.V[0xF] = 0
                if self.V[self.instruction.x] > self.V[self.instruction.y]:
                    self.V[0xF] = 1

                self.V[self.instruction.x] = (self.V[self.instruction.x] - self.V[self.instruction.y]) & 0xFF
                self.PC += 2
                print("=>Subtracted V" + str(self.instruction.x) + " and V" + str(self.instruction.y) + "("
                      + str(self.V[self.instruction.y]) + ") = " + str(self.V[self.instruction.x])
                      + " ; Flag is now " + str(self.V[0xF]))
                self.jumps = 0
                return

            if opc.n == 0x6:
                self.V[0xF] = self.V[self.instruction.x] & 0x1
                self.V[self.instruction.x] >>= 0x1
                self.PC += 2
                print("=>Shifted V" + str(self.instruction.x) + " right. Is now: " + str(self.V[self.instruction.x])
                      + " | VF: " + str(self.V[0xF]))
                self.jumps = 0
                return

            if opc.n == 0xE:
                self.V[0xF] = self.V[self.instruction.x] & 0x1
                self.V[self.instruction.x] <<= 0x1
                self.PC += 2
                print("=>Shifted V" + str(self.instruction.x) + " left. Is now: " + str(self.V[self.instruction.x])
                      + " | VF: " + str(self.V[0xF]))
                self.jumps = 0
                return

        if opc.i == 0x9:        # 9XY0: Skip next instruction if VX != VY
            if self.V[self.instruction.x] != self.V[self.instruction.y]:
                self.PC += 4
                print("V" + str(self.instruction.x) + " != V" + str(self.instruction.y)
                      + " [" + str(self.V[self.instruction.x]) + " != " + str(self.V[self.instruction.y])
                      + "] || Skipped instruction")
            else:
                self.PC += 2
                print("V" + str(self.instruction.x) + " == V" + str(self.instruction.y)
                      + " [" + str(self.V[self.instruction.x]) + " == " + str(self.V[self.instruction.y])
                      + " || Didn't skip instruction")
            self.jumps = 0
            return

        if opc.i == 0xA:        # ANNN: Set I = NNN
            self.I = opc.nnn
            self.PC += 2
            print("=>Set I to " + str(hex(opc.nnn)))
            self.jumps = 0
            return

        if opc.i == 0xC:        # CXNN: Set VX = random(255) & KK
            self.V[self.instruction.x] = random.randint(0, 255) & self.instruction.kk
            self.PC += 2
            print("Set V" + str(self.instruction.x) + " to " + str(self.V[self.instruction.x]))
            self.jumps = 0
            return

        if opc.i == 0xD:        # DXYN: Draw Sprite located at I with height N at X, Y
            self.V[0xF] = 0x00

            for y in range(0, opc.n):
                line = self.memory[self.I + y]
                print("----" + str(line) + "----")
                for x in range(0, 8):
                    pixel = line & (0x80 >> x)
                    if pixel is not 0:
                        total_x = self.V[self.instruction.x] + x
                        total_y = self.V[self.instruction.y] + y
                        index = total_y * 64 + total_x

                        if self.display[index] is "＃":
                            self.V[0xF] = 1

                        if self.display[index] is "＃":
                            self.display[index] = "．"
                        else:
                            self.display[index] = "＃"

            self.PC += 2
            self.drawFlag = True

            print("=>Drew sprite located at " + str(hex(self.I)) + " that is " + str(opc.n)
                  + " bytes long at position (" + str(self.V[self.instruction.x]) + ", "
                  + str(self.V[self.instruction.y]) + ")")
            self.jumps = 0
            return

        if opc.i == 0xF:        # Multi Case
            if opc.kk == 0x07:
                self.V[self.instruction.x] = self.delay_timer
                self.PC += 2
                print("Set V" + str(self.instruction.x) + " to delay timer (" + str(self.delay_timer) + ")")
                return

            if opc.kk == 0x15:
                self.delay_timer = self.V[self.instruction.x]
                self.PC += 2
                print("Set delay timer to V" + str(self.instruction.x) + " (" + str(self.delay_timer) + ")")
                return

            if opc.kk == 0x1E:      # FX1E: Set I = I + VX
                self.I = (self.I + self.V[self.instruction.x]) & 0xFFFF
                self.PC += 2
                print("=>Added V" + str(self.instruction.x) + "(" + str(self.V[self.instruction.x])
                      + ") to I. Is now: " + str(hex(self.I)))
                self.jumps = 0
                return

            if opc.kk == 0x55:      # FX55: Copy values of register V0-VX into memory, starting at register I
                for offset in range(0, self.instruction.x + 1):
                    self.memory[self.I + offset] = self.V[offset]
                self.PC += 2
                print("=>Stored " + str(self.V[0:self.instruction.x + 1]) + " at " + str(hex(self.I)))
                self.jumps = 0
                return

            if opc.kk == 0x65:      # FX55: Copy values of register V0-VX into memory, starting at register I
                for offset in range(0, self.instruction.x + 1):
                    self.V[offset] = self.memory[self.I + offset]
                self.PC += 2
                print("=>Stored " + str(self.V[0:self.instruction.x + 1]) + " from " + str(hex(self.I)))
                self.jumps = 0
                return

        self.interrupt = True
        return "Unknown Opcode: " + str(hex(self.instruction.op))

    # TODO: Redo opcodes. Weird stuff happening. Probably typo. Do it carefully this time
