
from datapack import *
from mparser import *
from utils import *
from math import ceil
from os import access, F_OK, mkdir, chdir, getcwd
from shutil import rmtree


class Generator:

    STRING_TICKING_SCORE_ADD = "scoreboard objectives add ticking dummy"
    STRING_TICKING_SCORE_ENABLE = "scoreboard players set @a ticking 0"
    STRING_TICKING_SCORE_DISABLE = "scoreboard players set @a ticking -1"
    STRING_TICKING_SCORE_TICK = "scoreboard players add @a[scores={ticking=0..}] ticking 1"

    def __init__(self, folder = "msc", funcPrefix = "music_func_", namespace = "std", datapack = "datapack", tupletThreshold = 10, tupletInterval = 3, tupletFactor = 0.8):
        if(len(folder) <= 0):
            raise ValueError("Folder name must not be empty")
        
        self.pX = self.pY = self.pZ = 0
        self.facing = "south"
        self.facing_clockwise = RotateClockwise(self.facing)
        self.folder = folder
        self.func_prefix = funcPrefix if len(funcPrefix) > 0 else "music_func_"
        self.namespace = namespace if len(namespace) > 0 else "std"
        self.datapack = datapack if len(datapack) > 0 else "datapack"
        self.tupletThd = tupletThreshold
        self.tupletInv = tupletInterval
        self.tupletFactor = tupletFactor

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


    def getExecString(self, cmd):
        return "execute positioned ~{} ~{} ~{} run {}".format(self.pX, self.pY, self.pZ, cmd)

    def getSetblockString(self, x, y, z, block, data = "", nbt = ""):
        pat1 = "setblock ~{} ~{} ~{} {}[{}]".format(x, y, z, block, data)
        return pat1 + "{" + nbt + "} replace"

    def getPlaysoundString(self, name, vol, pitch, cond = ""):
        #if(vol < 0 or vol > 1):
        #    raise ValueError("Volume is " + str(vol))
        return "execute as @a[{}] at @s run playsound {} block @s ~ ~ ~ {} {}".format(cond, name, vol / 100, pitch)


    def getFullFuncDir(self):
        return "./" + self.datapack + "/data/" + self.namespace + "/functions/"

    def getTickFuncName(self, tick):
        return self.namespace + ":" + self.folder + "/" + self.func_prefix + str(tick)

    def getTickFuncFile(self, tick):
        return self.getFullFuncDir() + self.folder + "/" + self.func_prefix + str(tick) + ".mcfunction"


    def generateTimeline(self, notelist):

        maxTime = -1
        maxDur = -1

        for note in notelist:
            maxTime = max(maxTime, note.start)
            if(maxTime == note.start):
                maxDur = max(maxDur, note.duration)
        
        print("This piece lasts for", maxTime, "seconds")

        lengthTicks = round((maxTime + maxDur) * 20)
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

        filename = self.getFullFuncDir() + self.folder + "_result.mcfunction"
        with open(filename, "w") as fp:
            for entity in result:
                print(entity, file = fp)

    def generateFunctions(self, notelist):

        # delete original files
        fullFolder = self.getFullFuncDir() + self.folder
        if(access(fullFolder, F_OK)):
            rmtree(fullFolder)
        mkdir(fullFolder)

        dicResult = dict()

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
            
            _startTick = round(i.start * 20)
            startTick = round_half_up(i.start * 20)
            if(startTick != _startTick):
                print("Different values:", startTick, _startTick)
            _durationTick = round(i.duration * 20)
            durationTick = round_half_up(i.duration * 20)
            #print(durationTick)

            #func = self.getTickFuncFile(startTick)
            #with open(func, "a") as fp:

            pitch = self.PITCH[nt[0]]
            instrument = self.INSTRUMENT[nt[1]]
            volume = nt[2]
            cond = "scores={ticking=" + str(startTick) + "}"
                
            cmd = self.getPlaysoundString(instrument, volume, pitch, cond)
            #print(cmd, file = fp)

            if not startTick in dicResult:
                dicResult[startTick] = []
            dicResult[startTick].append(cmd)

            if(durationTick >= self.tupletThd):
                tickCnt = self.tupletInv
                while(tickCnt <= durationTick):
                    curTick = startTick + tickCnt
                    func = self.getTickFuncFile(curTick)
                    #with open(func, "a") as fp:
                    pitch = self.PITCH[nt[0]]
                    instrument = self.INSTRUMENT[nt[1]]
                    volume = nt[2] * (self.tupletFactor ** (tickCnt / self.tupletInv))
                    cond = "scores={ticking=" + str(curTick) + "}"

                    cmd = self.getPlaysoundString(instrument, volume, pitch, cond)
                    #print(cmd, file = fp)

                    if not curTick in dicResult:
                        dicResult[curTick] = []
                    dicResult[curTick].append(cmd)
                        
                    tickCnt += self.tupletInv


        for tick, cmds in dicResult.items():
            func = self.getTickFuncFile(tick)
            with open(func, "w") as fp:
                for item in cmds:
                    print(item, file = fp)
            
    def generateExtra(self, fp):
        cmds = parseExtra(fp)
        for tick, cmd in cmds:
            func = self.getTickFuncFile(tick)
            with open(func, "a") as fp:
                print(cmd, file = fp)

    def writeInitFunc(self):
        funcName = self.getFullFuncDir() + "initialize.mcfunction"
        with open(funcName, "w") as fp:
            print("scoreboard objectives add ticking dummy", file = fp)
            print("scoreboard objectives setdisplay sidebar ticking", file = fp)
            print("scoreboard players set @a ticking -1", file = fp)
            print("gamerule commandBlockOutput false", file = fp)

    def generateTickingFunction(self):
        funcName = self.getFullFuncDir() + "ticking.mcfunction"
        with open(funcName, "w") as fp:
            print(Generator.STRING_TICKING_SCORE_TICK, file = fp)
        

if __name__ == "__main__":
    notelist = LoadMidiFile("LEVEL5_-judgelight-.mid")
    #fp = open("exampleExtra.txt", "r")

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
    if(not access("tags", F_OK)):
        mkdir("tags")
    chdir("tags")
    if(not access("functions", F_OK)):
        mkdir("functions")
    chdir("functions")
        #with open("tick.json", "w") as fp:
        #    print('{"replace":false,"values":["std:ticking"]}', file = fp)
    writeTag("tick", ["std:ticking"])
    chdir("..\..\..")

    if(not access("std", F_OK)):
        mkdir("std")
    chdir("std")
    if(not access("functions", F_OK)):
        mkdir("functions")
    chdir("functions")
    chdir("..\..\..\..")
    print(getcwd())
    g = Generator("lvl")

    g.writeInitFunc()
    g.generateTickingFunction()
    g.generateTimeline(notelist)
    g.generateFunctions(notelist)
    #g.generateExtra(fp)
    #fp.close()
    
