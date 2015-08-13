#library(myvariant)
#library(mygene)
library(magrittr)
library(S4Vectors)
library(VariantAnnotation)
library(plyr)

## replace all NA values in the data.frame with 0
replaceWith0 <- function(df){
  d <- data.frame(df)
  d[is.na(d)] <- 0
  DataFrame(d)
}

## rank genes by scaled CADD score
rankByCaddScore <- function(gene.list, df.list){
  y <- do.call(rbind, lapply(gene.list, function(i) geneDf(df.list, i)))
  df <- data.frame(gene=unlist(y[,1]), cadd.phred=unlist(y[,2]))
  ranked <- arrange(df, -cadd.phred)
  data.frame(subset(ranked, gene != c("NULL", 0)), row.names=NULL)
}

## get specific gene's rows of data.frame
geneInDf <- function(df, gene){
  gene.df <- subset(df, sapply(df$dbnsfp.genename, function(i) gene %in% i))
  gene.df
}

## extract median CADD scores of variants from each gene
cadd.df <- function(df){
    return(data.frame(subset(df, cadd.phred == median(df$cadd.phred))))
}

## create unique dataframes by gene, check pathogenicity
geneDf <- function(vars.list, gene){
  patho <- lapply(vars.list, function(i) geneInDf(i, gene))
  patho <- patho[sapply(patho, function(i) nrow(i) > 0)]
  common <- do.call(rbind.fill, lapply(patho, cadd.df))
  df <- list("gene"=as.character(gene),
             "cadd.phred"=mean(common$cadd.phred))
  df
}
