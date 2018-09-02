class Opcode:
    def __init__(self, opc: int):
        self.op = opc
        self.i = (opc & 0xF000) >> 12
        self.nnn = opc & 0x0FFF
        self.n = (opc & 0x000F)
        self.x = (opc & 0x0F00) >> 8
        self.y = (opc & 0x00F0) >> 4
        self.kk = (opc & 0x00FF)
