def ConvertTick(sec):
    return sec / 0.05

def ConvertDelta(delta = [0, 0, 0]):
    return ["~"+str(delta[0]), "~"+str(delta[1]), "~"+str(delta[2])]

def ConvertSoundName(soundname):
    return "minecraft:block.note_block." + soundname

def ConvertDelta2Facing(delta):
    if(delta[2] != 0):
        if(delta[2] > 0):
            return "south"
        else:
            return "north"
    if(delta[0] != 0):
        if(delta[0] > 0):
            return "east"
        else:
            return "west"
    return "up";

def ConvertFacing2Delta(facing, length = 1):
    if(facing == "south"):
        return [0, 0, length]
    if(facing == "north"):
        return [0, 0, -length];
    if(facing == "east"):
        return [length, 0 ,0];
    if(facing == "west"):
        return [-length, 0 ,0];
    raise ValueError('"facing" must be "south", "north", "east" or "west"');

def GetOppositeFacing(facing):
    if(facing == "south"):
        return "north"
    if(facing == "north"):
        return "south"
    if(facing == "west"):
        return "east";
    if(facing == "east"):
        return "west"
    raise ValueError('"facing" must be "south", "north", "east" or "west"');
	
def MoveForward(current, facing, length = 1):
    delta = ConvertFacing2Delta(facing, length)
    return (current[0] + delta[0], current[1] + delta[1], current[2] + delta[2])

def RotateClockwise(facing):
    if(facing == "north"):
        return "east"
    if(facing == "east"):
        return "south"
    if(facing == "south"):
        return "west"
    if(facing == "west"):
        return "north"
    raise ValueError('"facing" must be "south", "north", "east" or "west"');

def RotateCounterclockwise(facing):
    if(facing == "north"):
        return "west"
    if(facing == "west"):
        return "south"
    if(facing  == "south"):
        return "east"
    if(facing == "east"):
        return "north"
    raise ValueError('"facing" must be "south", "north", "east" or "west"');
    

def publishDatapack(functionList):
    pass
