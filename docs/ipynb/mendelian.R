#library(myvariant)
#library(mygene)
library(magrittr)
library(S4Vectors)
library(VariantAnnotation)
library(plyr)

replaceWith0 <- function(df){
  d <- data.frame(df)
  d[is.na(d)] <- 0
  DataFrame(d)
}

## apply filters to dataframe
filterDf <- function(df){
  df <- subset(df, DP > 15 & FS < 30 & QD > 2)
  df <- subset(df, cadd.consequence %in% c("NON_SYNONYMOUS", "STOP_GAINED", "STOP_LOST", "CANONICAL_SPLICE", "SPLICE_SITE"))
  df <- subset(df, exac.af < 0.01)
  #df <- subset(df, dbsnp.dbsnp_build > 128 )
  df <- subset(df, sapply(dbnsfp.1000gp1.af, function(i) i < 0.01 ))
  df
}

## get specific gene's rows of data.frame
geneInDf <- function(df, gene){
  gene.df <- subset(df, sapply(df$dbnsfp.genename, function(i) gene %in% i))
  gene.df
}

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

rankByCaddScore <- function(gene.list, df.list){
  y <- do.call(rbind, lapply(gene.list, function(i) geneDf(df.list, i)))
  df <- data.frame(gene=unlist(y[,1]), cadd.phred=unlist(y[,2]))
  ranked <- arrange(df, -cadd.phred)
  data.frame(subset(ranked, gene != c("NULL", 0)), row.names=NULL)
}

