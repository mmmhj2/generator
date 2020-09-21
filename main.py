from gen import *
from sys import argv
from os import *
from getopt import getopt


doc ='''Minecraft Redstone Music Datapack Generator
Usage: main.py [-f:|--folder:][-d:|--desc:] *.mid 
folder        Specifies the name of the folder where functions are placed
desc          Specifies the description of the generated datapack

'''

def prepare(desc):
    if(not access("datapack", F_OK)):
        mkdir("datapack")
    chdir("datapack")
    writeMcmeta(desc)

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

def generateFolderName(midiName):
    result = ""
    for i in midiName:
        if i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            result += i.lower()
        elif i in "abcdefghijklmnopqrstuvwxyz":
            result += (i)
        elif i in "1234567890":
            if len(result) <= 0:
                result += "_"
            result += i
        else:
            result += "_"
    return result

if __name__ == "__main__":

    print(generateFolderName("aB2"))
    
    opts, args = getopt(argv[1:], "-f:-d:", ["folder:", "desc:"])
    if(len(args) != 1):
        print(doc)
        exit()
    folderName = ""
    desc = "Auto-generated music datapack"
    for opt, arg in opts:
        if(opt in ("-f", "--folder")):
            folderName = arg
        if(opt in ("-d", "--desc")):
            desc = arg
    prepare(desc)
    
    notelist = LoadMidiFile(args[0])
    
    if(not access("std", F_OK)):
        mkdir("std")
    chdir("std")
    if(not access("functions", F_OK)):
        mkdir("functions")
    chdir("functions")

    if(len(folderName) <= 0):
        folderName = generateFolderName(args[0])
    
    g = Generator(folderName)
    
    g.writeInitFunc()
    g.generateTickingFunction()
    g.generateTimeline(notelist)
    g.generateFunctions(notelist)
    



