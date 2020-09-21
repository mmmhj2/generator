import mido             #pip install mido
from bisect import *

class note:
    F_1 = 42
    F_3 = 66
    F_5 = 90
    F_7 = 114
    def __init__(self, note, duration, start, volume = 100, track = 1):
        self.note = note
        self.duration = duration
        self.start = start
        self.volume = volume
        self.track = track

    def __str__(self):
        return "NOTE {} DUR {} STR {}".format(self.note, self.duration, self.start)

    def toMCNote(self, offset = 0):
        if self.F_1 - offset <= self.note and self.note <= self.F_3 - offset:
            '''
            if(self.track % 2 == 1):
                return (self.note - (42 - offset), 0, self.volume)   #minecraft:block.note_block.bass
            else:
                return (self.note - (42 - offset), 1, self.volume)   #minecraft:block.note_block.didgeridoo
            '''
            return (self.note - (42 - offset), 0, self.volume)
        if self.F_3 - offset <= self.note and self.note <= self.F_5 - offset:
            '''
            if(self.track % 2 == 1):
                return (self.note - (66 - offset), 7, self.volume)   #minecraft:block.note_block.harp
            else:
                return (self.note - (66 - offset), 3, self.volume)   #minecraft:block.note_block.iron_xylophone
            '''
            return (self.note - (66 - offset), 7, self.volume)
        if self.F_5 - offset <= self.note and self.note <= self.F_7 - offset:
            '''
            if(self.track % 2 == 1):
                return (self.note - (90 - offset), 12, self.volume)  #minecraft:block.note_block.chime
            else:
                return (self.note - (90 - offset), 13, self.volume)  #minecraft:block.note_block.xylophone
            '''
            return (self.note - (90 - offset), 12, self.volume)

        if(self.note + offset <= self.F_1):
            return (0,0,self.volume)
        if(self.note + offset >= self.F_7):
            return (24,12,self.volume)
        
        raise ValueError("Unexpected value of note : {0}({1} modified)".format(self.note, self.note + offset))

def CalcPrefixTime(tempoList, tpb):
    prefix = []
    for i in range(len(tempoList)):
        prefix.append(0)
    for index, tempo in enumerate(tempoList):
        if(index > 0):
            prefix[index] = prefix[index - 1]
            prefix[index] += mido.tick2second(tempo[1] - tempoList[index-1][1], tpb, tempoList[index-1][0])
    print("Prefix Sum:", prefix)
    return prefix
        

def GetAccTime(tick, tempoList, tpb, prefixSum):
    ret = 0
    '''
    i = 0
    while(i <= len(tempoList) - 1):
        tempo = tempoList[i]
        if(i == len(tempoList) - 1 or tempoList[i+1][1] > tick):
            #ret = ret + (tick - tempoList[i][1]) * tempoList[i][0]
            ret += mido.tick2second(tick - tempoList[i][1], tpb, tempoList[i][0])
            #print(ret, tick, tempoList[i][1], tempoList[i][0])
            break
        #ret = ret + (tempoList[i + 1][1] - tempoList[i][1]) * tempoList[i][0]
        ret += mido.tick2second(tempoList[i+1][1] - tempoList[i][1], tpb, tempoList[i][0])
        i = i + 1
    '''

    if(not hasattr(GetAccTime, "tickTable")):
        GetAccTime.tickTable = []
        for i in tempoList:
            GetAccTime.tickTable.append(i[1])
    

    index = bisect(GetAccTime.tickTable, tick)

    #print(neoList, index)
    ret = prefixSum[index - 1] + mido.tick2second(tick - tempoList[index-1][1], tpb, tempoList[index-1][0])
    
    #print("Time(", tick,"):", ret)
    return ret

def finishNote(currentTime, dic, notes, tempoList, volume, track, tpb, prefixSum):
    nt = dic["note"]
    tim = GetAccTime(notes[nt][0], tempoList, tpb, prefixSum)
    result = note(nt, GetAccTime(currentTime, tempoList, tpb, prefixSum) - tim, tim, (notes[nt][1] / 127) * (volume / 127) * 100, track)
    notes[nt] = (0,0)
    #print("note begins at", tim, "ends at", currentTime)
    return result
    

def LoadMidiFile(fileName):
    with mido.MidiFile(fileName) as midifile:

        #for i, track in enumerate(midifile.tracks):
        #    print("Track {}:{}".format(i, track))
        
        tempoList = []
        for tk in midifile.tracks:
            currentTime = 0
            for msg in tk:
                if "time" in msg.dict():
                    currentTime += msg.dict()["time"]
                if msg.is_meta:
                    print(msg)
                    if msg.dict()["type"] == "set_tempo":
                        dic = msg.dict()
                        #currentTime = currentTime + dic["time"]
                        #_tps = mido.tick2second(1, midifile.ticks_per_beat, dic['tempo'])
                        tempoList.append((dic['tempo'], currentTime))
                        print("Change Tempo at", currentTime)
        if(len(tempoList) <= 0):
            raise ValueError("This MIDI file does not designate tempo")
                
        prefixSum = CalcPrefixTime(tempoList, midifile.ticks_per_beat)
        parsedNotes = []

        fp = open("midimsg.txt", "w")
        
        for trackcounter, track in enumerate(midifile.tracks):
            print(track, ":", file = fp)
            percussion = False
            volume = 127
            currentTime = 0
            notes = []
            for i in range(128):
                notes.append((0,0))
                
            for msg in track:
                print(msg, file = fp)
                dic = msg.dict()
                if dic["type"] == "note_on" and dic["velocity"] > 0:
                    currentTime = currentTime + dic["time"]
                    if(notes[dic["note"]] != (0, 0)):
                        parsedNotes.append(finishNote(currentTime, dic, notes, tempoList, volume, trackcounter, midifile.ticks_per_beat, prefixSum))
                        notes[dic["note"]] = (0, 0)
                    notes[dic["note"]] = (currentTime, dic["velocity"])
                    #noteCnt[dic["note"]] = noteCnt[dic["note"]] + 1
                        
                elif dic["type"] == "note_off" or (dic["type"] == "note_on" and dic["velocity"] == 0):
                    currentTime = currentTime + dic["time"]
                    parsedNotes.append(finishNote(currentTime, dic, notes, tempoList, volume, trackcounter, midifile.ticks_per_beat, prefixSum))
                else:
                    if "time" in dic:
                        currentTime = currentTime + dic["time"]
                    if dic["type"] == "control_change":
                        if(dic["control"] == 7):            # volume
                            volume = dic["value"]
                    else:
                        print(msg)

        fp.close()
                    
        #for i in parsedNotes:
        #    print(i)
        #for i in range(128):
        #    print(i, noteCnt[i])
        parsedNotes = sorted(parsedNotes, key = lambda notes: notes.start)
        return parsedNotes

if __name__ == '__main__':
        LoadMidiFile("Only_my_Railgun_-_Animenz_Piano_Sheets.mid")
