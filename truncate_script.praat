## Takes sound and textgrid pairs and cuts out unlabeled parts of the sound file if any, 
## and concatenates those parts into a single clean cut sound file. Keeps the original names.

form Clean-up beginnings and ends of sound files
	sentence Directory D:/IntroDataScienceProject/crema-d-mirror/MFA/MFAOutput
	sentence output_directory D:/IntroDataScienceProject/crema-d-mirror/MFA/MFAAblated
	comment If you want to analyze all the files, leave this blank
	word Base_file_name
	comment The name of result file
endform

Create Strings as file list... wavlist 'directory$'/'base_file_name$'*.wav
Create Strings as file list... gridlist 'directory$'/'base_file_name$'*.TextGrid
n = Get number of strings

for i to n

	select Strings wavlist
	filename$ = Get string... i
	Read from file... 'directory$'/'filename$'
	soundname$ = selected$ ("Sound")

	select Strings gridlist
	gridname$ = Get string... i
	Read from file... 'directory$'/'gridname$'
	plusObject: "Sound 'soundname$'" 

	Extract non-empty intervals: 1, 2
	Concatenate recoverably

	selectObject: "Sound chain"
	Rename: "'soundname$'"
	selectObject: "TextGrid chain"
	Rename: "'soundname$'"

	selectObject: "Sound 'soundname$'"
	Save as WAV file: "'output_directory$'/'soundname$'.wav"
	removeObject: "Sound 'soundname$'"

	selectObject: "TextGrid 'soundname$'"
	Save as text file: "'output_directory$'/'soundname$'.TextGrid"
	removeObject: "TextGrid 'soundname$'"

endfor
