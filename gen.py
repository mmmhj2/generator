
from datapack import *
from mparser import *
from utils import *
from math import ceil
from os import access, F_OK, mkdir, chdir
from shutil import rmtree


class Generator:

    STRING_TICKING_SCORE_ADD = "scoreboard objectives add ticking dummy"
    STRING_TICKING_SCORE_ENABLE = "scoreboard players set @a ticking 0"
    STRING_TICKING_SCORE_DISABLE = "scoreboard players set @a ticking -1"
    STRING_TICKING_SCORE_TICK = "scoreboard players add @a[scores={ticking=0..}] ticking 1"

    def __init__(self, folder = "msc"):
        if(len(folder) <= 0):
            raise ValueError("Folder name must not be empty")
        
        self.pX = self.pY = self.pZ = 0
        self.facing = "south"
        self.facing_clockwise = RotateClockwise(self.facing)
        self.folder = folder
        self.func_prefix = "music_func_"
        self.namespace = "std"

        self.PITCH = []
        for i in range(25):
            self.PITCH.append(2 ** (-1 + i / 12))
            
        self.INSTRUMENT = []
        self.INSTRUMENT.append("minecraft:block.note_block.bass")           # F#1-F#3
        self.INSTRUMENT.append("minecraft:block.note_block.didgeridoo")
        self.INSTRUMENT.append("minecraft:block.note_block.guitar")         # F#2-F#4
        self.INSTRUMENT.append("minecraft:block.note_block.iron_xylophone") # F#3-F#5
        self.INSTRUMENT.append("minecraft:block.note_block.bit")
        self.INSTRUMENT.append("minecraft:block.note_block.banjo")
        self.INSTRUMENT.append("minecraft:block.note_block.pling")
        self.INSTRUMENT.append("minecraft:block.note_block.harp")
        self.INSTRUMENT.append("minecraft:block.note_block.flute")          # F#4-F#6
        self.INSTRUMENT.append("minecraft:block.note_block.cow_bell")
        self.INSTRUMENT.append("minecraft:block.note_block.bell")           # F#5-F#7
        self.INSTRUMENT.append("minecraft:block.note_block.chime")
        self.INSTRUMENT.append("minecraft:block.note_block.xylophone")
        self.INSTRUMENT.append("minecraft:block.note_block.snare")
        self.INSTRUMENT.append("minecraft:block.note_block.basedrum")
        self.INSTRUMENT.append("minecraft:block.note_block.hat")

    def writeInitFunc(self):
        with open("initialize.mcfunction", "w") as fp:
            print("scoreboard objectives add ticking dummy", file = fp)
            print("scoreboard objectives setdisplay sidebar ticking", file = fp)
            print("scoreboard players set @a ticking -1", file = fp)
            print("gamerule commandBlockOutput false", file = fp)

    def getExecString(self, cmd):
        return "execute positioned ~{} ~{} ~{} run {}".format(self.pX, self.pY, self.pZ, cmd)

    def getSetblockString(self, x, y, z, block, data = "", nbt = ""):
        pat1 = "setblock ~{} ~{} ~{} {}[{}]".format(x, y, z, block, data)
        return pat1 + "{" + nbt + "} replace"

    def getPlaysoundString(self, name, vol, pitch, cond = ""):
        return "playsound {} block @a[{}] ~ ~ ~ {} {}".format(name, cond, vol, pitch)

    def generateTickingFunction(self):
        with open("ticking.mcfunction", "w") as fp:
            print(Generator.STRING_TICKING_SCORE_TICK, file = fp)

    def getTickFuncName(self, tick):
        return self.namespace + ":" + self.folder + "/" + self.func_prefix + str(tick)

    def getTickFuncFile(self, tick):
        return self.folder + "/" + self.func_prefix + str(tick) + ".mcfunction"


    def generateTimeline(self, notelist):
        print("This piece lasts for", notelist[-1].start, "seconds")

        lengthTicks = round(notelist[-1].start / 0.05)
        loopCnt = ceil(lengthTicks / 2)
        result = []

        for i in range(loopCnt):
            #func1 = "" + str(i * 2)
            #func2 = "music_func_" + str(i * 2 + 1)
            func1 = self.getTickFuncName(i * 2)
            func2 = self.getTickFuncName(i * 2 + 1)

            self.pX, self.pY, self.pZ = MoveForward((self.pX, self.pY, self.pZ), self.facing, 1)
            if i > 0:
                # place redstone repeater
                delta = ConvertFacing2Delta(self.facing_clockwise, 2)
                setblock = self.getSetblockString(delta[0], delta[1], delta[2], "repeater", data="facing={}".format(GetOppositeFacing(self.facing)))
                result.append(self.getExecString(setblock))
            else:
                # place command block and reset the ticking score
                delta = ConvertFacing2Delta(self.facing_clockwise, 2)
                cmd = Generator.STRING_TICKING_SCORE_ENABLE
                setblock = self.getSetblockString(delta[0], delta[1], delta[2], "command_block", nbt='Command:"{}", auto:0b'.format(cmd))
                result.append(self.getExecString(setblock))
            
            # place command blocks
            self.pX, self.pY, self.pZ = MoveForward((self.pX, self.pY, self.pZ), self.facing, 1)

            # block 1
            delta = ConvertFacing2Delta(self.facing_clockwise, 0)
            cmd = "function " + func1
            setblock = self.getSetblockString(delta[0], delta[1], delta[2], "repeating_command_block", nbt='Command:"{}", auto:0b'.format(cmd))
            result.append(self.getExecString(setblock))
            # wires
            delta = ConvertFacing2Delta(self.facing_clockwise, 1)
            setblock = self.getSetblockString(delta[0], delta[1], delta[2], "redstone_wire")
            result.append(self.getExecString(setblock))
            delta = ConvertFacing2Delta(self.facing_clockwise, 2)
            setblock = self.getSetblockString(delta[0], delta[1], delta[2], "redstone_wire")
            result.append(self.getExecString(setblock))
            delta = ConvertFacing2Delta(self.facing_clockwise, 3)
            setblock = self.getSetblockString(delta[0], delta[1], delta[2], "redstone_wire")
            result.append(self.getExecString(setblock))
            # block 2
            delta = ConvertFacing2Delta(self.facing_clockwise, 4)
            cmd = "function "+ func2
            setblock = self.getSetblockString(delta[0], delta[1], delta[2], "repeating_command_block", nbt='Command:"{}", auto:0b'.format(cmd))
            result.append(self.getExecString(setblock))

        # Reset the ticking score
        self.pX, self.pY, self.pZ = MoveForward((self.pX, self.pY, self.pZ), self.facing, 1)
        delta = ConvertFacing2Delta(self.facing_clockwise, 2)
        setblock = self.getSetblockString(delta[0], delta[1], delta[2], "repeater", data="facing={}".format(GetOppositeFacing(self.facing)))
        result.append(self.getExecString(setblock))
        self.pX, self.pY, self.pZ = MoveForward((self.pX, self.pY, self.pZ), self.facing, 1)
        delta = ConvertFacing2Delta(self.facing_clockwise, 2)
        cmd = Generator.STRING_TICKING_SCORE_DISABLE
        setblock = self.getSetblockString(delta[0], delta[1], delta[2], "command_block", nbt='Command:"{}", auto:0b'.format(cmd))
        result.append(self.getExecString(setblock))

        filename = self.folder + "_result.mcfunction"
        with open(filename, "w") as fp:
            for entity in result:
                print(entity, file = fp)

    def generateFunctions(self, notelist):

        # delete original files
        if(access(self.folder, F_OK)):
            rmtree(self.folder)
        mkdir(self.folder)
        
        
        tick = 0
        lastTime = 0
        
        for i in notelist:
            try:
                nt = i.toMCNote(+12)
            except ValueError as e:
                print(e)
                continue

            #deltaTime = i.start - lastTime
            #if(deltaTime < 0):
            #    raise ValueError("Notes are not sorted")
            #deltaTick = round(deltaTime / 0.05)
            
            startTick = round(i.start * 20)
            durationTick = round(i.duration / 0.05)
            #print(i.start, i.start * 20, startTick)

            func = self.getTickFuncFile(startTick)
            with open(func, "a") as fp:

                pitch = self.PITCH[nt[0]]
                instrument = self.INSTRUMENT[nt[1]]
                volume = nt[2]
                cond = "scores={ticking=" + str(startTick) + "}"
                
                cmd = self.getPlaysoundString(instrument, volume, pitch, cond)
                print(cmd, file = fp)
            

        

if __name__ == "__main__":
    notelist = LoadMidiFile("Only_my_Railgun_-_Animenz_Piano_Sheets.mid")

    #if(access("datapack", F_OK)):
    #    rmtree("datapack")

    if(not access("datapack", F_OK)):
        mkdir("datapack")
    chdir("datapack")
    writeMcmeta("Auto-generated music datapack")

    if(not access("data", F_OK)):
        mkdir("data")
    chdir("data")

    if(not access("minecraft", F_OK)):
        mkdir("minecraft")
        chdir("minecraft")
        mkdir("tags")
        chdir("tags")
        mkdir("functions")
        chdir("functions")
        with open("tick.json", "w") as fp:
            print('{"replace":false,"values":["std:ticking"]}', file = fp)
        chdir("..\..\..")

    if(not access("std", F_OK)):
        mkdir("std")
    chdir("std")
    if(not access("functions", F_OK)):
        mkdir("functions")
    chdir("functions")
    g = Generator("omr")

    g.writeInitFunc()
    g.generateTickingFunction()
    g.generateTimeline(notelist)
    g.generateFunctions(notelist)
    
