def puzzle01(mapLoader):
    puzzleNotes = ["C4","E4","C4","E4","G4","G4"]
    noteblockNames = ["Notepiece"+str(i+1) for i in range(6)]
    good = 0
    for i in range(len(noteblockNames)):
        if mapLoader.getObject(noteblockNames[i]).note == puzzleNotes[i]:
            good += 1
    if len(puzzleNotes) == good:
        return True
    return False
