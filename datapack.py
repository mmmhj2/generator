import json

def writeMcmeta(desp = "No description provided", version = 6):
    pack = {"pack":{"description":desp, "pack_format":version}}
    with open("pack.mcmeta", "w") as fp:
        json.dump(pack, fp, indent = 4)

if __name__ == "__main__":
    writeMcmeta()

