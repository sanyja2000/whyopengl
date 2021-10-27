def puzzle01(mapLoader):
    puzzleNotes = ["C4","C#4","D4","D#4","E4"]
    noteblockNames = ["Noteblock"+str(i+1) for i in range(5)]
    good = 0
    for i in range(len(puzzleNotes)):
        if mapLoader.getObject(noteblockNames[i]).note == puzzleNotes[i]:
            good += 1
    if len(puzzleNotes) == good:
        return True
    return False
