  library(tidyverse)
  
  setwd("D:/IntroDataScienceProject/crema-d-mirror")
  
  getFset <- function(sets){
    df = read.csv("SubSetAudioWAV/transcriptions.csv")
  
    df <- df |>
      rowwise() |>
      mutate(
        ActorID = as.numeric(str_split_i(Filename, "_", 1)), #Since CSV has it as doubles
        SentType = str_split_i(Filename, "_", 2)
      )
    
    df <- df |> mutate(ActorID = as.numeric(ActorID))
    
    df <- df |> mutate(
      Gender = case_when(
        ActorID %in% c(1001, 1011, 1014, 1016, 1017, 1022, 1023, 1026, 1027, 1028, 1033, 1034, 1035, 1040, 1041, 1051, 1057, 1062, 1064, 1065, 1066, 1067, 1068, 1069, 1071, 1077, 1077, 1086, 1087, 1005, 1015, 1032, 1036, 1038, 1039, 1042, 1050, 1059, 1070, 1080, 1083, 1088, 1019, 1045, 1081, 1085, 1090, 1018, 1031, 1048) ~ "Male",
        ActorID %in% c(1002, 1003, 1004, 1006, 1008, 1009, 1010, 1012, 1020, 1021, 1024, 1025, 1037, 1052, 1053, 1054, 1055, 1058, 1075, 1076, 1078, 1082, 1084, 1089, 1007, 1029, 1030, 1060, 1061, 1063, 1073, 1074, 1056, 1072, 1091, 1013, 1043, 1046, 1049, 1079) ~ "Female",
      )
    )
    
    partSubset =  sets
    
    # Create a data frame to join on
    partSubset <- data.frame(ActorID = partSubset)
    
    
    gSet <- semi_join(df, partSubset, by = "ActorID")
    return(gSet)
    
  fold = 0
  
  accuracies <- data.frame(Acc = numeric())
  
  #New Folds
  setsList <- list(
    c(1001, 1022, 1033, 1044, 1065, 1071, 1003, 1010, 1025, 1055, 1082, 1091, 1061, 1013, 1005, 1039, 1080, 1081),
    c(1011, 1023, 1034, 1051, 1066, 1077, 1004, 1012, 1037, 1058, 1084, 1007, 1063, 1043, 1015, 1042, 1083, 1085),
    c(1014, 1026, 1035, 1057, 1067, 1086, 1006, 1020, 1052, 1075, 1089, 1029, 1073, 1046, 1032, 1050, 1088, 1090),
    c(1016, 1027, 1040, 1062, 1068, 1087, 1008, 1021, 1053, 1076, 1056, 1030, 1074, 1049, 1036, 1059, 1019, 1018),
    c(1017, 1028, 1041, 1064, 1069, 1002, 1009, 1024, 1054, 1078, 1072, 1060, 1048, 1079, 1038, 1070, 1045, 1031)
  )
  
  while(fold <= 4) {
    foldName = paste0("fold", fold, "_")
    gt <- readLines(paste0("D:/IntroDataScienceProject/crema-d-mirror/WhisperResults/",foldName,"pr.txt"))
    wt <- readLines(paste0("D:/IntroDataScienceProject/crema-d-mirror/WhisperResults/",foldName,"gt.txt"))
    
    gt <- data.frame(GroundTruth = gt)
    wt <- data.frame(WhisperTranscription = wt)
    fSet <- getFset(setsList[[fold+1]])
    Results <- cbind(fSet,gt,wt)
  
    Results <- Results |>
      filter(
        # Gender == "Female",
        Emotion == "NEU"
      )
  
    fileNum = nrow(Results)
    sameResults <- Results[Results$WhisperTranscription == Results$GroundTruth, ]
    sameNum = nrow(sameResults)
  
    # print(fileNum)
    # print(sameNum)
    # print(sameNum/fileNum)
    fold <- fold +1
    fold_accuracy <- sameNum/fileNum
    accuracies <- rbind(accuracies, data.frame(Fold = fold, Acc = fold_accuracy))
  }
  
  # Overall average accuracy
  # paste0("Average accuracy across all folds: ", signif(mean(accuracies$Acc),4), " (", signif(sd(accuracies$Acc),4), ")")
  
  paste0("Average accuracy across all folds: ", signif(mean(accuracies$Acc, na.rm = TRUE),4), " (", signif(sd(accuracies$Acc, na.rm = TRUE),4), ")")
  # cat("Standard deviation across all folds:", sd(accuracies$Acc), "\n")
  
