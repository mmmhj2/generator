from gen import *
from sys import argv
from os import chdir, mkdir, F_OK, getcwd
from getopt import getopt


doc ='''Minecraft Redstone Music Datapack Generator
Usage: main.py [-f:|--folder:][-d:|--desc:][-e:|--extra:] *.mid 
folder        Specifies the name of the folder where functions are placed
desc          Specifies the description of the generated datapack
extra         Specifies the extra file to generate commands other than playing the midi file(For example, subtitles or special effects)
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
    index = midiName.rfind("\\")
    if index != -1:
        midiName = midiName[index + 1:]
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
    
    opts, args = getopt(argv[1:], "-f:-d:", ["folder:", "desc:"])
    if(len(args) == 0):
        args.append("Only_my_Railgun_-_Animenz_Piano_Sheets.mid")
    if(len(args) != 1):
        print(doc)
        exit()
        
    folderName = ""
    extra = "exampleExtra.txt"
    desc = "Auto-generated music datapack"
    
    for opt, arg in opts:
        if(opt in ("-f", "--folder")):
            folderName = arg
        if(opt in ("-d", "--desc")):
            desc = arg
        if(opt in ("-e", "--extra")):
            extra = arg
            
    notelist = LoadMidiFile(args[0])
    
    prepare(desc)
    
    if(not access("std", F_OK)):
        mkdir("std")
    chdir("std")
    if(not access("functions", F_OK)):
        mkdir("functions")
    chdir("functions")

    chdir("..\..\..\..")

    if(len(folderName) <= 0):
        folderName = generateFolderName(args[0])
    print(getcwd())
    g = Generator(folderName)
    
    g.writeInitFunc()
    g.generateTickingFunction()
    g.generateTimeline(notelist)
    g.generateFunctions(notelist)
    if(len(extra) > 0):
        with open(extra, "r") as fp:
            g.generateExtra(fp)



