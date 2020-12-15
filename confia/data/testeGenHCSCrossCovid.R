
#####Pegar dataset completo#########

pnewsuserTot <- read.csv(file.choose(), sep=";", header = T)
pnewsTot <- read.csv(file.choose(), sep=";", header = T)
usersGeral <- read.csv(file.choose(), sep=";", header = T)

View(pnewsTot)
View(usersGeral)
View(pnewsuserTot)

library(dplyr)




#####Carregando os 10 conjuntos de treino e teste#########

pnewsTreino1 <- read.csv(file="treinoGen1.csv", sep=";", header = T)
pnewsTeste1 <- read.csv(file="testeGen1.csv", sep=";", header = T)
pnewsTreino2 <- read.csv(file="treinoGen2.csv", sep=";", header = T)
pnewsTeste2 <- read.csv(file="testeGen2.csv", sep=";", header = T)
pnewsTreino3 <- read.csv(file="treinoGen3.csv", sep=";", header = T)
pnewsTeste3 <- read.csv(file="testeGen3.csv", sep=";", header = T)
pnewsTreino4 <- read.csv(file="treinoGen4.csv", sep=";", header = T)
pnewsTeste4 <- read.csv(file="testeGen4.csv", sep=";", header = T)
pnewsTreino5 <- read.csv(file="treinoGen5.csv", sep=";", header = T)
pnewsTeste5 <- read.csv(file="testeGen5.csv", sep=";", header = T)
pnewsTreino6 <- read.csv(file="treinoGen6.csv", sep=";", header = T)
pnewsTeste6 <- read.csv(file="testeGen6.csv", sep=";", header = T)
pnewsTreino7 <- read.csv(file="treinoGen7.csv", sep=";", header = T)
pnewsTeste7 <- read.csv(file="testeGen7.csv", sep=";", header = T)
pnewsTreino8 <- read.csv(file="treinoGen8.csv", sep=";", header = T)
pnewsTeste8 <- read.csv(file="testeGen8.csv", sep=";", header = T)
pnewsTreino9 <- read.csv(file="treinoGen9.csv", sep=";", header = T)
pnewsTeste9 <- read.csv(file="testeGen9.csv", sep=";", header = T)
pnewsTreino10 <- read.csv(file="treinoGen10.csv", sep=";", header = T)
pnewsTeste10 <- read.csv(file="testeGen10.csv", sep=";", header = T)

nrow(pnewsTeste10)

##### Caso as maquinas devolvam um arquivo unico com as opinioes (Maq1)
pnewsTotMaq1 <- read.csv(file="ResulttesteGenMaq1.csv", sep=";", header = T)

pnewsTreino1Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTreino1$id,]
pnewsTeste1Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTeste1$id,]
pnewsTreino2Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTreino2$id,]
pnewsTeste2Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTeste2$id,]
pnewsTreino3Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTreino3$id,]
pnewsTeste3Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTeste3$id,]
pnewsTreino4Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTreino4$id,]
pnewsTeste4Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTeste4$id,]
pnewsTreino5Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTreino5$id,]
pnewsTeste5Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTeste5$id,]
pnewsTreino6Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTreino6$id,]
pnewsTeste6Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTeste6$id,]
pnewsTreino7Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTreino7$id,]
pnewsTeste7Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTeste7$id,]
pnewsTreino8Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTreino8$id,]
pnewsTeste8Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTeste8$id,]
pnewsTreino9Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTreino9$id,]
pnewsTeste9Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTeste9$id,]
pnewsTreino10Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTreino10$id,]
pnewsTeste10Maq1 <- pnewsTotMaq1[pnewsTotMaq1$id %in% pnewsTeste10$id,]

nrow(pnewsTeste10Maq1)
###############################################


##### Caso as maquinas devolvam um arquivo unico com as opinioes (Maq2)
pnewsTotMaq2 <- read.csv(file="ResulttesteGenMaq2.csv", sep=";", header = T)

pnewsTreino1Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTreino1$id,]
pnewsTeste1Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTeste1$id,]
pnewsTreino2Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTreino2$id,]
pnewsTeste2Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTeste2$id,]
pnewsTreino3Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTreino3$id,]
pnewsTeste3Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTeste3$id,]
pnewsTreino4Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTreino4$id,]
pnewsTeste4Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTeste4$id,]
pnewsTreino5Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTreino5$id,]
pnewsTeste5Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTeste5$id,]
pnewsTreino6Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTreino6$id,]
pnewsTeste6Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTeste6$id,]
pnewsTreino7Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTreino7$id,]
pnewsTeste7Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTeste7$id,]
pnewsTreino8Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTreino8$id,]
pnewsTeste8Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTeste8$id,]
pnewsTreino9Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTreino9$id,]
pnewsTeste9Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTeste9$id,]
pnewsTreino10Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTreino10$id,]
pnewsTeste10Maq2 <- pnewsTotMaq2[pnewsTotMaq2$id %in% pnewsTeste10$id,]

nrow(pnewsTeste10Maq2)
###############################################


##### Caso as maquinas devolvam um arquivo unico com as opinioes (Maq3)
pnewsTotMaq3 <- read.csv(file="ResulttesteGenMaq3.csv", sep=";", header = T)

pnewsTreino1Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTreino1$id,]
pnewsTeste1Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTeste1$id,]
pnewsTreino2Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTreino2$id,]
pnewsTeste2Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTeste2$id,]
pnewsTreino3Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTreino3$id,]
pnewsTeste3Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTeste3$id,]
pnewsTreino4Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTreino4$id,]
pnewsTeste4Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTeste4$id,]
pnewsTreino5Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTreino5$id,]
pnewsTeste5Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTeste5$id,]
pnewsTreino6Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTreino6$id,]
pnewsTeste6Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTeste6$id,]
pnewsTreino7Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTreino7$id,]
pnewsTeste7Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTeste7$id,]
pnewsTreino8Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTreino8$id,]
pnewsTeste8Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTeste8$id,]
pnewsTreino9Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTreino9$id,]
pnewsTeste9Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTeste9$id,]
pnewsTreino10Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTreino10$id,]
pnewsTeste10Maq3 <- pnewsTotMaq3[pnewsTotMaq3$id %in% pnewsTeste10$id,]

nrow(pnewsTeste10Maq3)
###############################################

##### Caso as maquinas devolvam um arquivo unico com as opinioes (Maq4)
pnewsTotMaq4 <- read.csv(file="ResulttesteGenMaq4-FNE.csv", sep=";", header = T)

pnewsTreino1Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTreino1$id,]
pnewsTeste1Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTeste1$id,]
pnewsTreino2Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTreino2$id,]
pnewsTeste2Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTeste2$id,]
pnewsTreino3Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTreino3$id,]
pnewsTeste3Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTeste3$id,]
pnewsTreino4Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTreino4$id,]
pnewsTeste4Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTeste4$id,]
pnewsTreino5Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTreino5$id,]
pnewsTeste5Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTeste5$id,]
pnewsTreino6Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTreino6$id,]
pnewsTeste6Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTeste6$id,]
pnewsTreino7Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTreino7$id,]
pnewsTeste7Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTeste7$id,]
pnewsTreino8Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTreino8$id,]
pnewsTeste8Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTeste8$id,]
pnewsTreino9Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTreino9$id,]
pnewsTeste9Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTeste9$id,]
pnewsTreino10Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTreino10$id,]
pnewsTeste10Maq4 <- pnewsTotMaq4[pnewsTotMaq4$id %in% pnewsTeste10$id,]

nrow(pnewsTeste10Maq4)

###############################################

###############################################

##### Caso as maquinas devolvam um arquivo unico com as opinioes (Maq5)
pnewsTotMaq5 <- read.csv(file="ResulttesteGenMaq5-JON.csv", sep=";", header = T)

pnewsTreino1Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTreino1$id,]
pnewsTeste1Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTeste1$id,]
pnewsTreino2Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTreino2$id,]
pnewsTeste2Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTeste2$id,]
pnewsTreino3Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTreino3$id,]
pnewsTeste3Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTeste3$id,]
pnewsTreino4Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTreino4$id,]
pnewsTeste4Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTeste4$id,]
pnewsTreino5Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTreino5$id,]
pnewsTeste5Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTeste5$id,]
pnewsTreino6Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTreino6$id,]
pnewsTeste6Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTeste6$id,]
pnewsTreino7Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTreino7$id,]
pnewsTeste7Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTeste7$id,]
pnewsTreino8Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTreino8$id,]
pnewsTeste8Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTeste8$id,]
pnewsTreino9Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTreino9$id,]
pnewsTeste9Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTeste9$id,]
pnewsTreino10Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTreino10$id,]
pnewsTeste10Maq5 <- pnewsTotMaq5[pnewsTotMaq5$id %in% pnewsTeste10$id,]

nrow(pnewsTeste10Maq5)

###############################################


######### Iniciando a execucao ##########
#########################################


contconj = 1

while (contconj <= 10)  {
    

    ##### Separando o conjunto pnewsuser #####
  
  if (contconj == 1){
    pnewsTreino <- pnewsTreino1
    pnewsTeste <- pnewsTeste1
    # pnewsTreinoMaq1 <- pnewsTreino1Maq1
    # pnewsTesteMaq1 <- pnewsTeste1Maq1
    # pnewsTreinoMaq2 <- pnewsTreino1Maq2
    # pnewsTesteMaq2 <- pnewsTeste1Maq2
    # pnewsTreinoMaq3 <- pnewsTreino1Maq3
    # pnewsTesteMaq3 <- pnewsTeste1Maq3
    # pnewsTreinoMaq4 <- pnewsTreino1Maq4
    # pnewsTesteMaq4 <- pnewsTeste1Maq4
    # pnewsTreinoMaq5 <- pnewsTreino1Maq5
    # pnewsTesteMaq5 <- pnewsTeste1Maq5
  }else{
    if (contconj == 2){
      pnewsTreino <- pnewsTreino2
      pnewsTeste <- pnewsTeste2
      # pnewsTreinoMaq1 <- pnewsTreino2Maq1
      # pnewsTesteMaq1 <- pnewsTeste2Maq1
      # pnewsTreinoMaq2 <- pnewsTreino2Maq2
      # pnewsTesteMaq2 <- pnewsTeste2Maq2
      # pnewsTreinoMaq3 <- pnewsTreino2Maq3
      # pnewsTesteMaq3 <- pnewsTeste2Maq3
      # pnewsTreinoMaq4 <- pnewsTreino2Maq4
      # pnewsTesteMaq4 <- pnewsTeste2Maq4
      # pnewsTreinoMaq5 <- pnewsTreino2Maq5
      # pnewsTesteMaq5 <- pnewsTeste2Maq5
    }else{
      if (contconj == 3){
        pnewsTreino <- pnewsTreino3
        pnewsTeste <- pnewsTeste3
        # pnewsTreinoMaq1 <- pnewsTreino3Maq1
        # pnewsTesteMaq1 <- pnewsTeste3Maq1
        # pnewsTreinoMaq2 <- pnewsTreino3Maq2
        # pnewsTesteMaq2 <- pnewsTeste3Maq2
        # pnewsTreinoMaq3 <- pnewsTreino3Maq3
        # pnewsTesteMaq3 <- pnewsTeste3Maq3
        # pnewsTreinoMaq4 <- pnewsTreino3Maq4
        # pnewsTesteMaq4 <- pnewsTeste3Maq4
        # pnewsTreinoMaq5 <- pnewsTreino3Maq5
        # pnewsTesteMaq5 <- pnewsTeste3Maq5
      }else{
        if (contconj == 4){
          pnewsTreino <- pnewsTreino4
          pnewsTeste <- pnewsTeste4
          # pnewsTreinoMaq1 <- pnewsTreino4Maq1
          # pnewsTesteMaq1 <- pnewsTeste4Maq1
          # pnewsTreinoMaq2 <- pnewsTreino4Maq2
          # pnewsTesteMaq2 <- pnewsTeste4Maq2
          # pnewsTreinoMaq3 <- pnewsTreino4Maq3
          # pnewsTesteMaq3 <- pnewsTeste4Maq3
          # pnewsTreinoMaq4 <- pnewsTreino4Maq4
          # pnewsTesteMaq4 <- pnewsTeste4Maq4
          # pnewsTreinoMaq5 <- pnewsTreino4Maq5
          # pnewsTesteMaq5 <- pnewsTeste4Maq5
        }else{
          if (contconj == 5){
            pnewsTreino <- pnewsTreino5
            pnewsTeste <- pnewsTeste5
            # pnewsTreinoMaq1 <- pnewsTreino5Maq1
            # pnewsTesteMaq1 <- pnewsTeste5Maq1
            # pnewsTreinoMaq2 <- pnewsTreino5Maq2
            # pnewsTesteMaq2 <- pnewsTeste5Maq2
            # pnewsTreinoMaq3 <- pnewsTreino5Maq3
            # pnewsTesteMaq3 <- pnewsTeste5Maq3
            # pnewsTreinoMaq4 <- pnewsTreino5Maq4
            # pnewsTesteMaq4 <- pnewsTeste5Maq4
            # pnewsTreinoMaq5 <- pnewsTreino5Maq5
            # pnewsTesteMaq5 <- pnewsTeste5Maq5
          }else{
            if (contconj == 6){
              pnewsTreino <- pnewsTreino6
              pnewsTeste <- pnewsTeste6
              # pnewsTreinoMaq1 <- pnewsTreino6Maq1
              # pnewsTesteMaq1 <- pnewsTeste6Maq1
              # pnewsTreinoMaq2 <- pnewsTreino6Maq2
              # pnewsTesteMaq2 <- pnewsTeste6Maq2
              # pnewsTreinoMaq3 <- pnewsTreino6Maq3
              # pnewsTesteMaq3 <- pnewsTeste6Maq3
              # pnewsTreinoMaq4 <- pnewsTreino6Maq4
              # pnewsTesteMaq4 <- pnewsTeste6Maq4
              # pnewsTreinoMaq5 <- pnewsTreino6Maq5
              # pnewsTesteMaq5 <- pnewsTeste6Maq5
            }else{
              if (contconj == 7){
                pnewsTreino <- pnewsTreino7
                pnewsTeste <- pnewsTeste7
                # pnewsTreinoMaq1 <- pnewsTreino7Maq1
                # pnewsTesteMaq1 <- pnewsTeste7Maq1
                # pnewsTreinoMaq2 <- pnewsTreino7Maq2
                # pnewsTesteMaq2 <- pnewsTeste7Maq2
                # pnewsTreinoMaq3 <- pnewsTreino7Maq3
                # pnewsTesteMaq3 <- pnewsTeste7Maq3
                # pnewsTreinoMaq4 <- pnewsTreino7Maq4
                # pnewsTesteMaq4 <- pnewsTeste7Maq4
                # pnewsTreinoMaq5 <- pnewsTreino7Maq5
                # pnewsTesteMaq5 <- pnewsTeste7Maq5
              }else{
                if (contconj == 8){
                  pnewsTreino <- pnewsTreino8
                  pnewsTeste <- pnewsTeste8
                  # pnewsTreinoMaq1 <- pnewsTreino8Maq1
                  # pnewsTesteMaq1 <- pnewsTeste8Maq1
                  # pnewsTreinoMaq2 <- pnewsTreino8Maq2
                  # pnewsTesteMaq2 <- pnewsTeste8Maq2
                  # pnewsTreinoMaq3 <- pnewsTreino8Maq3
                  # pnewsTesteMaq3 <- pnewsTeste8Maq3
                  # pnewsTreinoMaq4 <- pnewsTreino8Maq4
                  # pnewsTesteMaq4 <- pnewsTeste8Maq4
                  # pnewsTreinoMaq5 <- pnewsTreino8Maq5
                  # pnewsTesteMaq5 <- pnewsTeste8Maq5
                }else{
                  if (contconj == 9){
                    pnewsTreino <- pnewsTreino9
                    pnewsTeste <- pnewsTeste9
                    # pnewsTreinoMaq1 <- pnewsTreino9Maq1
                    # pnewsTesteMaq1 <- pnewsTeste9Maq1
                    # pnewsTreinoMaq2 <- pnewsTreino9Maq2
                    # pnewsTesteMaq2 <- pnewsTeste9Maq2
                    # pnewsTreinoMaq3 <- pnewsTreino9Maq3
                    # pnewsTesteMaq3 <- pnewsTeste9Maq3
                    # pnewsTreinoMaq4 <- pnewsTreino9Maq4
                    # pnewsTesteMaq4 <- pnewsTeste9Maq4
                    # pnewsTreinoMaq5 <- pnewsTreino9Maq5
                    # pnewsTesteMaq5 <- pnewsTeste9Maq5
                  }else{
                    if (contconj == 10){
                      pnewsTreino <- pnewsTreino10
                      pnewsTeste <- pnewsTeste10
                      # pnewsTreinoMaq1 <- pnewsTreino10Maq1
                      # pnewsTesteMaq1 <- pnewsTeste10Maq1
                      # pnewsTreinoMaq2 <- pnewsTreino10Maq2
                      # pnewsTesteMaq2 <- pnewsTeste10Maq2
                      # pnewsTreinoMaq3 <- pnewsTreino10Maq3
                      # pnewsTesteMaq3 <- pnewsTeste10Maq3
                      # pnewsTreinoMaq4 <- pnewsTreino10Maq4
                      # pnewsTesteMaq4 <- pnewsTeste10Maq4
                      # pnewsTreinoMaq5 <- pnewsTreino10Maq5
                      # pnewsTesteMaq5 <- pnewsTeste10Maq5
                    }
                  }
                }
              }
            }
          }
        }
      }
    }  
  }
  

    contnews = 1
    contnewstot = nrow(pnewsTreino)
    contnewsF = 0
    contnewsV = 0
    
    
    
    while (contnews <= contnewstot)  {
      
      if (pnewsTreino[contnews,1] > 300){
        contnewsF = contnewsF + 1 
      }else{
        contnewsV = contnewsV + 1
      }
      
      if (contnews ==1){
        pnewsuserTreino <- pnewsuserTot[pnewsuserTot$new==pnewsTreino[contnews,1],]
      }else{
        pnewsuserTreino <- rbind(pnewsuserTreino,pnewsuserTot[pnewsuserTot$new==pnewsTreino[contnews,1],])
      }
      
      contnews <- contnews + 1
      
    }
    
    
    contnews = 1
    contnewstot = nrow(pnewsTeste)
    
    while (contnews <= contnewstot)  {
      
      if (contnews ==1){
        pnewsuserTeste <- pnewsuserTot[pnewsuserTot$new==pnewsTeste[contnews,1],]
      }else{
        pnewsuserTeste <- rbind(pnewsuserTeste,pnewsuserTot[pnewsuserTot$new==pnewsTeste[contnews,1],])
      }
      
      contnews <- contnews + 1
      
    }

    ptemp = pnewsuserTreino[pnewsuserTreino$user %in% pnewsuserTeste$user,]
    pnewsuserTreino <- ptemp[order(ptemp$user, decreasing=FALSE),]
    

    ### Teste##########

    pnewsuser <- pnewsuserTeste 
    pnews <- pnewsTeste

    ### Calculo dos parâmetros do usuário

    contnews = 1
    contnewstot = nrow(pnewsuserTreino)
    uAnterior <- 0
    uAtual <- pnewsuserTreino[contnews,2]
    
    totR <- 0
    totF <- 0
    vx = ((totF+0.01) / (contnewsF+0.01)) * (contnewsV+0.01)
    vy = (vx * (totR+0.01)) / (totF+0.01)
    usersGeral$alfaN <- totR+0.01
    usersGeral$betaN <- vy
    usersGeral$umAlfaN <- vx
    usersGeral$umBetaN <- totF+0.01
    
    while (contnews <= contnewstot)  {
      
      if (uAnterior != uAtual){
        if (uAnterior != 0){
          
          vx = ((totF+0.01) / (contnewsF+0.01)) * (contnewsV+0.01)
          vy = (vx * (totR+0.01)) / (totF+0.01)
          
          usersGeral$alfaN[usersGeral$id==uAnterior] <- totR+0.01
          usersGeral$betaN[usersGeral$id==uAnterior] <- vy
          usersGeral$umAlfaN[usersGeral$id==uAnterior] <- vx
          usersGeral$umBetaN[usersGeral$id==uAnterior] <- totF+0.01
          
        }  
        totR <- 0
        totF <- 0
        uAnterior <- pnewsuserTreino[contnews,2]
      }
      
      
      if (pnewsuserTreino[contnews,1] < 301){
        totR <- totR + 1
      }else{
        totF <- totF + 1  
      }
       
      
      
      contnews <- contnews + 1
      uAtual <- pnewsuserTreino[contnews,2]
      
    }
    vx = ((totF+0.01) / (contnewsF+0.01)) * (contnewsV+0.01)
    vy = (vx * (totR+0.01)) / (totF+0.01)
    
    usersGeral$alfaN[usersGeral$id==uAnterior] <- totR+0.01
    usersGeral$betaN[usersGeral$id==uAnterior] <- vy
    usersGeral$umAlfaN[usersGeral$id==uAnterior] <- vx
    usersGeral$umBetaN[usersGeral$id==uAnterior] <- totF+0.01
    
    usersGeral$probAlfaN <- ((usersGeral$alfaN) / (usersGeral$alfaN + usersGeral$umAlfaN))
    usersGeral$probumAlfaN <- (1 - usersGeral$probAlfaN)
    usersGeral$probBetaN <- ((usersGeral$betaN) / (usersGeral$betaN + usersGeral$umBetaN))
    usersGeral$probumBetaN <- (1 - usersGeral$probBetaN)
    

    
    ### Calculo dos parâmetros das maquinas
    
    
    ### Calculo dos parâmetros da Maq1
    
    # contnews = 1
    # contnewstot = nrow(pnewsTreinoMaq1)
    # 
    # totR <- 0
    # totF <- 0
    # vx <- 0
    # vy <- 0
    # 
    # while (contnews <= contnewstot)  {
    # 
    #   if (pnewsTreinoMaq1[contnews,1] < 301){
    #     if (pnewsTreinoMaq1[contnews,3] == "real"){
    #         totR <- totR + 1
    #     }else{
    #         vx <- vx + 1
    #     }
    #   }else{
    #     if (pnewsTreinoMaq1[contnews,3] == "real"){
    #         totF <- totF + 1
    #     }else{
    #         vy <- vy + 1
    #     }
    #   }
    # 
    #   contnews <- contnews + 1
    # 
    # }
    # 
    # totR <- totR + 0.01
    # totF <- totF + 0.01
    # vx <- vx + 0.01
    # vy <- vy + 0.01
    # 
    # 
    # probAlfaNMaq1 <- totR / (totR + vx)
    # probumAlfaNMaq1 <- (1 - probAlfaNMaq1)
    # probBetaNMaq1 <- vy / (vy + totF)
    # probumBetaNMaq1 <- (1 - probBetaNMaq1)
    # 
    # 
    # ### Calculo dos parâmetros da Maq2
    # 
    # contnews = 1
    # contnewstot = nrow(pnewsTreinoMaq2)
    # 
    # totR <- 0
    # totF <- 0
    # vx <- 0
    # vy <- 0
    # 
    # while (contnews <= contnewstot)  {
    #   
    #   if (pnewsTreinoMaq2[contnews,1] < 301){
    #     if (pnewsTreinoMaq2[contnews,3] == "real"){
    #       totR <- totR + 1
    #     }else{
    #       vx <- vx + 1
    #     }
    #   }else{
    #     if (pnewsTreinoMaq2[contnews,3] == "real"){
    #       totF <- totF + 1
    #     }else{
    #       vy <- vy + 1
    #     }
    #   }
    #   
    #   contnews <- contnews + 1
    #   
    # }
    # 
    # totR <- totR + 0.01
    # totF <- totF + 0.01
    # vx <- vx + 0.01
    # vy <- vy + 0.01
    # 
    # 
    # probAlfaNMaq2 <- totR / (totR + vx)
    # probumAlfaNMaq2 <- (1 - probAlfaNMaq2)
    # probBetaNMaq2 <- vy / (vy + totF)
    # probumBetaNMaq2 <- (1 - probBetaNMaq2)
    # 
    # 
    # ### Calculo dos parâmetros da Maq3
    # 
    # contnews = 1
    # contnewstot = nrow(pnewsTreinoMaq3)
    # 
    # totR <- 0
    # totF <- 0
    # vx <- 0
    # vy <- 0
    # 
    # while (contnews <= contnewstot)  {
    # 
    #   if (pnewsTreinoMaq3[contnews,1] < 301){
    #     if (pnewsTreinoMaq3[contnews,3] == "real"){
    #       totR <- totR + 1
    #     }else{
    #       vx <- vx + 1
    #     }
    #   }else{
    #     if (pnewsTreinoMaq3[contnews,3] == "real"){
    #       totF <- totF + 1
    #     }else{
    #       vy <- vy + 1
    #     }
    #   }
    # 
    #   contnews <- contnews + 1
    # 
    # }
    # 
    # totR <- totR + 0.01
    # totF <- totF + 0.01
    # vx <- vx + 0.01
    # vy <- vy + 0.01
    # 
    # 
    # probAlfaNMaq3 <- totR / (totR + vx)
    # probumAlfaNMaq3 <- (1 - probAlfaNMaq3)
    # probBetaNMaq3 <- vy / (vy + totF)
    # probumBetaNMaq3 <- (1 - probBetaNMaq3)
    # 
    # 
    # ### Calculo dos parâmetros da Maq4
    #  
    # contnews = 1
    # contnewstot = nrow(pnewsTreinoMaq4)
    # 
    # totR <- 0
    # totF <- 0
    # vx <- 0
    # vy <- 0
    # 
    # while (contnews <= contnewstot)  {
    # 
    #   if (pnewsTreinoMaq4[contnews,1] < 301){
    #     if (pnewsTreinoMaq4[contnews,3] == "real"){
    #       totR <- totR + 1
    #     }else{
    #       vx <- vx + 1
    #     }
    #   }else{
    #     if (pnewsTreinoMaq4[contnews,3] == "real"){
    #       totF <- totF + 1
    #     }else{
    #       vy <- vy + 1
    #     }
    #   }
    # 
    #   contnews <- contnews + 1
    # 
    # }
    # 
    # totR <- totR + 0.01
    # totF <- totF + 0.01
    # vx <- vx + 0.01
    # vy <- vy + 0.01
    # 
    # 
    # probAlfaNMaq4 <- totR / (totR + vx)
    # probumAlfaNMaq4 <- (1 - probAlfaNMaq4)
    # probBetaNMaq4 <- vy / (vy + totF)
    # probumBetaNMaq4 <- (1 - probBetaNMaq4)
    # 
    # 
    # 
    # ### Calculo dos parâmetros da Maq5
    # 
    # contnews = 1
    # contnewstot = nrow(pnewsTreinoMaq5)
    # 
    # totR <- 0
    # totF <- 0
    # vx <- 0
    # vy <- 0
    # 
    # while (contnews <= contnewstot)  {
    #   
    #   if (pnewsTreinoMaq5[contnews,1] < 301){
    #     if (pnewsTreinoMaq5[contnews,3] == "real"){
    #       totR <- totR + 1
    #     }else{
    #       vx <- vx + 1
    #     }
    #   }else{
    #     if (pnewsTreinoMaq5[contnews,3] == "real"){
    #       totF <- totF + 1
    #     }else{
    #       vy <- vy + 1
    #     }
    #   }
    #   
    #   contnews <- contnews + 1
    #   
    # }
    # 
    # totR <- totR + 0.01
    # totF <- totF + 0.01
    # vx <- vx + 0.01
    # vy <- vy + 0.01
    # 
    # 
    # probAlfaNMaq5 <- totR / (totR + vx)
    # probumAlfaNMaq5 <- (1 - probAlfaNMaq5)
    # probBetaNMaq5 <- vy / (vy + totF)
    # probumBetaNMaq5 <- (1 - probBetaNMaq5)
    # 
    # 
            
        #### Avaliando a noticia
    
    contnews = 1
    contnewstot = nrow(pnews)
    omega = 0.5
    
    ### Opiniao dos usuarios
    
    while (contnews <= contnewstot)  {
      
      usersNoticia <- pnewsuser[pnewsuser$new==pnews[contnews,1],]
      
      produtorioAlfaN = 1
      produtorioumAlfaN = 1
      produtorioBetaN = 1
      produtorioumBetaN = 1
      
      contusertot = nrow(usersNoticia)
      contuser=1
      
      
      opiniao = TRUE
      while (contuser<=contusertot){
        
        if (opiniao){

          produtorioAlfaN = produtorioAlfaN * usersGeral$probAlfaN[usersNoticia$user[contuser]]
          produtorioumBetaN = produtorioumBetaN * usersGeral$probumBetaN[usersNoticia$user[contuser]]
        }else {

          produtorioumAlfaN = produtorioumAlfaN * usersGeral$probumAlfaN[usersNoticia$user[contuser]]
          produtorioBetaN = produtorioBetaN * usersGeral$probBetaN[usersNoticia$user[contuser]]
        }
        
        contuser=contuser+1
      }
      
      
      
      ### Opiniao das maquinas
      
        
      #   ### Caso não tenha usuarios ###
      #      # produtorioAlfaN = 1
      #      # produtorioumAlfaN = 1
      #      # produtorioBetaN = 1
      #      # produtorioumBetaN = 1
      # 
      # 
      # ### Opiniao da Maq1
      #     
      #     op <- pnewsTesteMaq1[pnewsTesteMaq1$id==pnews[contnews,1],3]
      # 
      #     if (op == "real"){
      #       opiniao = TRUE
      #     }else{
      #       opiniao = FALSE
      #     }
      # 
      # 
      #     if (opiniao){
      #       produtorioAlfaN = produtorioAlfaN * probAlfaNMaq1
      #       produtorioumBetaN = produtorioumBetaN * probumBetaNMaq1
      #     }else {
      #       produtorioumAlfaN = produtorioumAlfaN * probumAlfaNMaq1
      #       produtorioBetaN = produtorioBetaN * probBetaNMaq1
      #     }
      #     
      #   
      #     ### Opiniao da Maq2
      #     
      #     
      #     op <- pnewsTesteMaq2[pnewsTesteMaq2$id==pnews[contnews,1],3]
      #     
      #     if (op == "real"){
      #       opiniao = TRUE
      #     }else{
      #       opiniao = FALSE  
      #     }
      #     
      #     
      #     
      #     if (opiniao){
      #       produtorioAlfaN = produtorioAlfaN * probAlfaNMaq2
      #       produtorioumBetaN = produtorioumBetaN * probumBetaNMaq2
      #     }else {
      #       produtorioumAlfaN = produtorioumAlfaN * probumAlfaNMaq2
      #       produtorioBetaN = produtorioBetaN * probBetaNMaq2
      #     }
      #     
      # 
      #     ### Opiniao da Maq3
      #     
      #     
      #     op <- pnewsTesteMaq3[pnewsTesteMaq3$id==pnews[contnews,1],3]
      # 
      #     if (op == "real"){
      #       opiniao = TRUE
      #     }else{
      #       opiniao = FALSE
      #     }
      # 
      # 
      # 
      #     if (opiniao){
      #       produtorioAlfaN = produtorioAlfaN * probAlfaNMaq3
      #       produtorioumBetaN = produtorioumBetaN * probumBetaNMaq3
      #     }else {
      #       produtorioumAlfaN = produtorioumAlfaN * probumAlfaNMaq3
      #       produtorioBetaN = produtorioBetaN * probBetaNMaq3
      #     }
      #     
      # 
      #     ### Opiniao da Maq4
      #     
      #     
      #     op <- pnewsTesteMaq4[pnewsTesteMaq4$id==pnews[contnews,1],3]
      # 
      #     if (op == "real"){
      #       opiniao = TRUE
      #     }else{
      #       opiniao = FALSE
      #     }
      # 
      # 
      # 
      #     if (opiniao){
      #       produtorioAlfaN = produtorioAlfaN * probAlfaNMaq4
      #       produtorioumBetaN = produtorioumBetaN * probumBetaNMaq4
      #     }else {
      #       produtorioumAlfaN = produtorioumAlfaN * probumAlfaNMaq4
      #       produtorioBetaN = produtorioBetaN * probBetaNMaq4
      #     }
      #     
      # 
      # 
      # 
      #     ### Opiniao da Maq5
      #     
      #     
      #     op <- pnewsTesteMaq5[pnewsTesteMaq5$id==pnews[contnews,1],3]
      #     
      #     if (op == "real"){
      #       opiniao = TRUE
      #     }else{
      #       opiniao = FALSE
      #     }
      #     
      #     
      #     
      #     if (opiniao){
      #       produtorioAlfaN = produtorioAlfaN * probAlfaNMaq5
      #       produtorioumBetaN = produtorioumBetaN * probumBetaNMaq5
      #     }else {
      #       produtorioumAlfaN = produtorioumAlfaN * probumAlfaNMaq5
      #       produtorioBetaN = produtorioBetaN * probBetaNMaq5
      #     }
      #     
          

        
          
      #### Inferencia Bayesiana ####
        
      reputacaonewsVN = (omega * produtorioAlfaN * produtorioumAlfaN)
      #reputacaonewsVN = (log10(omega) + log10(produtorioAlfaN) + log10(produtorioumAlfaN))
              
      reputacaonewsVN = reputacaonewsVN * 100
      #reputacaonewsV = round(reputacaonewsV, 9)
      pnews$reputacaoOptVN[contnews] <- reputacaonewsVN
      
      reputacaonewsFN = ((1-omega) * produtorioBetaN * produtorioumBetaN)
      #reputacaonewsFN = (log10((1-omega)) + log10(produtorioBetaN) + log10(produtorioumBetaN))
      
      reputacaonewsFN = reputacaonewsFN * 100
      #reputacaonewsF = round(reputacaonewsF, 9)
      pnews$reputacaoOptFN[contnews] <- reputacaonewsFN
      
      contnews=contnews+1
      
      
    }

    ##### Avaliando resultado

    print(contconj)
    print("VV")
    vv=nrow(pnews%>%filter(id<301,reputacaoOptVN>=reputacaoOptFN))
    print(vv)
    print("VF")
    vf=nrow(pnews%>%filter(id>300,reputacaoOptVN>=reputacaoOptFN))
    print(vf)
    print("FV")
    fv=nrow(pnews%>%filter(id<301,reputacaoOptVN<reputacaoOptFN))
    print(fv)
    print("FF")
    ff=nrow(pnews%>%filter(id>300,reputacaoOptVN<reputacaoOptFN))
    print(ff)
    
    ac=((vv+ff)/(vv+ff+fv+vf))
    print("Acuracia")
    print(ac)
    
    #print("Usuarios sem Reputacao")
    #nrow(usersGeral%>%filter(alfa==0,umAlfa==0))

    contconj = contconj + 1
    
}




