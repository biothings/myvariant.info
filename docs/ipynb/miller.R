library(myvariant)
library(mygene)
library(VariantAnnotation)

setwd("~/sulab/myvariant/vcf/")
vcf.files <- paste(getwd(), list.files(getwd()), sep="/")

getVars <- function(vcf.file){
  vcf <- readVcf(vcf.file, genome="hg19")
  vcf <- vcf[isSNV(vcf)]
  vars <- rowRanges(vcf)
  vars <- as(vars, "DataFrame")
  vars$query <- formatHgvs(vcf, "snp")
  annotations <- getVariants(vars$query)
  annotations[c('DP', 'FS', 'QD')] <- info(vcf)[c('DP', 'FS', 'QD')]
  annotations <- replaceWith0(annotations)
  annotations
}

vars <- lapply(vcf.files, getVars)
snps <- lapply(vars, function(i) subset(i, DP > 15 & FS < 30 & QD > 2))
filtered.annotations <- lapply(snps, filterDf)

gene.counts <- data.frame(table(unlist(lapply(filtered.annotations, function(i) unique(i$dbnsfp.genename)))))
top.genes <- subset(gene.counts, Freq == 4)
top.genes

ranked <- rankByCaddScore(top.genes$Var1, filtered.annotations)
ranked
