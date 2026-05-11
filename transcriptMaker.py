import os
import csv

folder_path = r"D:\IntroDataScienceProject\crema-d-mirror\SubSetAudioWAV" 

filenames = os.listdir(folder_path)

data = []

for file in filenames:
    parts = file.split("_")
    data.append([file,parts[2]])

outputPath = f"{folder_path}/transcriptions.csv"

with open(outputPath, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Filename', 'Emotion'])
    writer.writerows(data)

print(f"CSV saved as {outputPath}")
