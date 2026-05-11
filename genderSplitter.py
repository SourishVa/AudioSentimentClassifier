import os
import sys
import shutil

originalDataSet = r"D:\IntroDataScienceProject\crema-d-mirror\SubSetAudioWAVMFAInput"
genderDataSet = r"D:\IntroDataScienceProject\crema-d-mirror\MFA\Women"

for file in os.listdir(originalDataSet):
    filePath = os.path.join(originalDataSet, file)
    newFilePath = os.path.join(genderDataSet, file)
    fileNum =  (int)(file.split('_')[0])
    if fileNum in [1002, 1003, 1004, 1006, 1008, 1009, 1010, 1012, 1020, 1021, 1024, 1025, 1037, 1052, 1053, 1054, 1055, 1058, 1075, 1076, 1078, 1082, 1084, 1089, 1007, 1029, 1030, 1060, 1061, 1063, 1073, 1074, 1056, 1072, 1091, 1013, 1043, 1046, 1049, 1079]:
        shutil.copy(filePath, newFilePath)


#Men: [1001, 1011, 1014, 1016, 1017, 1022, 1023, 1026, 1027, 1028, 1033, 1034, 1035, 1040, 1041, 1051, 1057, 1062, 1064, 1065, 1066, 1067, 1068, 1069, 1071, 1077, 1077, 1086, 1087, 1005, 1015, 1032, 1036, 1038, 1039, 1042, 1050, 1059, 1070, 1080, 1083, 1088, 1019, 1045, 1081, 1085, 1090, 1018, 1031, 1048]
#Women: [1002, 1003, 1004, 1006, 1008, 1009, 1010, 1012, 1020, 1021, 1024, 1025, 1037, 1052, 1053, 1054, 1055, 1058, 1075, 1076, 1078, 1082, 1084, 1089, 1007, 1029, 1030, 1060, 1061, 1063, 1073, 1074, 1056, 1072, 1091, 1013, 1043, 1046, 1049, 1079]: