import mido             #pip install mido

class note:
    F_1 = 42
    F_3 = 66
    F_5 = 90
    F_7 = 114
    def __init__(self, note, duration, start, volume=100):
        self.note = note
        self.duration = duration
        self.start = start
        self.volume = volume

    def __str__(self):
        return "NOTE {} DUR {} STR {}".format(self.note, self.duration, self.start)

    def toMCNote(self, offset = 0):
        if self.F_1 - offset <= self.note and self.note <= self.F_3 - offset:
            return (self.note - (42 - offset), 0, self.volume)   #minecraft:block.note_block.bass
        if self.F_3 - offset <= self.note and self.note <= self.F_5 - offset:
            return (self.note - (66 - offset), 7, self.volume)   #minecraft:block.note_block.harp
        if self.F_5 - offset <= self.note and self.note <= self.F_7 - offset:
            return (self.note - (90 - offset), 12, self.volume)  #minecraft:block.note_block.chime

        if(self.note + offset <= self.F_1):
            return (0,0,self.volume)
        if(self.note + offset >= self.F_7):
            return (24,12,self.volume)
        
        raise ValueError("Unexpected value of note : {0}({1} modified)".format(self.note, self.note + offset))

def GetAccTime(tick, tempoList):
    ret = 0
    i = 0
    while(i <= len(tempoList) - 1):
        tempo = tempoList[i]
        if(i == len(tempoList) - 1 or tempoList[i+1][1] > tick):
            ret = ret + (tick - tempoList[i][1]) * tempoList[i][0]
            #print(ret, tick, tempoList[i][1], tempoList[i][0])
            break
        ret = ret + (tempoList[i + 1][1] - tempoList[i][1]) * tempoList[i][0]
        i = i + 1
    #print("Time(", tick,"):", ret)
    return ret

def finishNote(currentTime, dic, notes, tps, volume):
    nt = dic["note"]
    tim = GetAccTime(notes[nt][0], tps)
    result = note(nt, GetAccTime(currentTime,tps) - tim, tim, (notes[nt][1] / 127) * (volume / 127) * 100)
    notes[nt] = (0,0)
    return result
    

def LoadMidiFile(fileName):
    with mido.MidiFile(fileName) as midifile:

        for i, track in enumerate(midifile.tracks):
            print("Track {}:{}".format(i, track))
        
        tps = []
        for tk in midifile.tracks:
            currentTime = 0
            for msg in tk:
                #print(msg)
                if msg.is_meta:
                    if msg.dict()["type"] == "set_tempo":
                        dic = msg.dict()
                        currentTime = currentTime + dic["time"]
                        _tps = mido.tick2second(1, midifile.ticks_per_beat, dic['tempo'])
                        tps.append((_tps, currentTime))
                
        
        parsedNotes = []
        for track in midifile.tracks:
            print(track, ":")
            percussion = False
            volume = 127
            currentTime = 0
            notes = []
            for i in range(128):
                notes.append((0,0))
                
            for msg in track:
                #print(msg)
                if not msg.is_meta:
                    dic = msg.dict()
                    if dic["type"] == "note_on" and dic["velocity"] > 0:
                        currentTime = currentTime + dic["time"]
                        if(notes[dic["note"]] != (0, 0)):
                            parsedNotes.append(finishNote(currentTime, dic, notes, tps, volume))
                            notes[dic["note"]] = (0, 0)
                        notes[dic["note"]] = (currentTime, dic["velocity"])
                        #noteCnt[dic["note"]] = noteCnt[dic["note"]] + 1
                        
                    elif dic["type"] == "note_off" or (dic["type"] == "note_on" and dic["velocity"] == 0):
                        currentTime = currentTime + dic["time"]
                        parsedNotes.append(finishNote(currentTime, dic, notes, tps, volume))
                        
                    elif dic["type"] == "control_change":
                        if(dic["control"] == 7):            # volume
                            volume = dic["value"]
                    else:
                        print(msg)
                    
        #for i in parsedNotes:
        #    print(i)
        #for i in range(128):
        #    print(i, noteCnt[i])
        parsedNotes = sorted(parsedNotes, key = lambda notes: notes.start)
        return parsedNotes

if __name__ == '__main__':
        LoadMidiFile("kebab_march.mid")
