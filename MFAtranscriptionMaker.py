#This script was to create a folder with input in a way that is acceptable for MFA: (wav, transcription) tuple
import os
import sys

originalDataSet = r"D:\IntroDataScienceProject\crema-d-mirror\SubSetAudioWAVMFAInput"

for file in os.listdir(originalDataSet):
    textfileName = os.path.splitext(file)[0] + ".txt"
    textfilePath = os.path.join(originalDataSet, textfileName)
    #Check for sentence type
    sentType = file.split('_')[1]
    print(sentType)
    text = ""
    if sentType == "DFA":
        text = "Don't forget a jacket"
    elif sentType == "IOM":
        text = "I'm on my way to the meeting"
    elif sentType == "ITH":
        text = "I think I have a doctor's appointment"
    elif sentType == "ITS":
        text = "I think I've seen this before"
    elif sentType == "IWL":
        text = "I would like a new alarm clock"
    elif sentType == "IWW":
        text = "I wonder what this is about"
    elif sentType == "MTI":
        text = "Maybe tomorrow it will be cold"
    elif sentType == "TAI":
        text = "The airplane is almost full"
    elif sentType == "TIE":
        text = "That is exactly what happened"
    elif sentType == "TSI":
        text = "The surface is slick"
    elif sentType == "WSI":
        text = "We'll stop in a couple of minutes"
    else:
        print("FAILURE")
    
    with open(textfilePath, "w") as t:
        t.write(text)
        
print("MFA file transcirption prep completed")