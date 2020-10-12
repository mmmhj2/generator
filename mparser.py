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
        self.instru = [["minecraft:block.note_block.bass"],["minecraft:block.note_block.harp"],["minecraft:block.note_block.chime"]]

    def __str__(self):
        return "NOTE {} DUR {} STR {}".format(self.note, self.duration, self.start)

    def toMCNote(self, offset = 0, instruIndex = 0):
        if self.F_1 - offset <= self.note and self.note <= self.F_3 - offset:
            return (self.note - (42 - offset), self.instru[0][instruIndex], self.volume)
        if self.F_3 - offset <= self.note and self.note <= self.F_5 - offset:
            return (self.note - (66 - offset), self.instru[1][instruIndex], self.volume)
        if self.F_5 - offset <= self.note and self.note <= self.F_7 - offset:
            return (self.note - (90 - offset), self.instru[2][instruIndex], self.volume)

        if(self.note + offset <= self.F_1):
            return (0,self.instru[0][instruIndex],self.volume)
        if(self.note + offset >= self.F_7):
            return (24,self.instru[2][instruIndex],self.volume)
        
        raise ValueError("Unexpected value of note : {0}({1} modified)".format(self.note, self.note + offset))

def CalcPrefixTime(tempoList, tpb):
    prefix = []
    for i in range(len(tempoList)):
        prefix.append(0)
    for index, tempo in enumerate(tempoList):
        if(index > 0):
            prefix[index] = prefix[index - 1]
            prefix[index] += mido.tick2second(tempo[1] - tempoList[index-1][1], tpb, tempoList[index-1][0])
    return prefix
        

def GetAccTime(tick, tempoList, tpb, prefixSum):
    ret = 0

    if(not hasattr(GetAccTime, "tickTable")):
        GetAccTime.tickTable = []
        for i in tempoList:
            GetAccTime.tickTable.append(i[1])
    
    index = bisect(GetAccTime.tickTable, tick)
    ret = prefixSum[index - 1] + mido.tick2second(tick - tempoList[index-1][1], tpb, tempoList[index-1][0])
    return ret

def finishNote(currentTime, dic, notes, tempoList, volume, track, tpb, prefixSum):
    nt = dic["note"]
    tim = GetAccTime(notes[nt][0], tempoList, tpb, prefixSum)
    result = note(nt, GetAccTime(currentTime, tempoList, tpb, prefixSum) - tim, tim, (notes[nt][1] / 127) * (volume / 127) * 100, track)
    notes[nt] = (0,0)
    return result
    

def LoadMidiFile(fileName):
    with mido.MidiFile(fileName) as midifile:  
        tempoList = []
        for tk in midifile.tracks:
            currentTime = 0
            for msg in tk:
                if "time" in msg.dict():
                    currentTime += msg.dict()["time"]
                if msg.is_meta:
                    if msg.dict()["type"] == "set_tempo":
                        dic = msg.dict()
                        tempoList.append((dic['tempo'], currentTime))
        if(len(tempoList) <= 0):
            raise ValueError("This MIDI file does not designate tempo")
                
        prefixSum = CalcPrefixTime(tempoList, midifile.ticks_per_beat)
        parsedNotes = []
        
        for trackcounter, track in enumerate(midifile.tracks):
            #print(track, ":", file = fp)
            percussion = False
            volume = 127
            currentTime = 0
            notes = []
            for i in range(128):
                notes.append((0,0))
                
            for msg in track:
                dic = msg.dict()
                if dic["type"] == "note_on" and dic["velocity"] > 0:
                    currentTime = currentTime + dic["time"]
                    if(notes[dic["note"]] != (0, 0)):
                        parsedNotes.append(finishNote(currentTime, dic, notes, tempoList, volume, trackcounter, midifile.ticks_per_beat, prefixSum))
                        notes[dic["note"]] = (0, 0)
                    notes[dic["note"]] = (currentTime, dic["velocity"])
                        
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
                        pass
        return parsedNotes

if __name__ == '__main__':
        LoadMidiFile("Only_my_Railgun_-_Animenz_Piano_Sheets.mid")
