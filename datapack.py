import json

class Datapack:
    pass

def writeMcmeta(desp = "No description provided", version = 6):
    pack = {"pack":{"description":desp, "pack_format":version}}
    with open("pack.mcmeta", "w") as fp:
        json.dump(pack, fp, indent = 4)

def writeTag(tagName, contain, replace = False):
    jsonFile = {"replace":replace, "values":contain}
    with open(tagName + ".json", "w") as fp:
        json.dump(jsonFile, fp, indent = 4) 

if __name__ == "__main__":
    writeMcmeta()

