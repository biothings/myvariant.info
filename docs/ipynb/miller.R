library(myvariant)
library(mygene)
library(VariantAnnotation)
library(GO.db)

setwd("~/sulab/myvariant/vcf/recal")
vcf.files <- paste(getwd(), list.files(getwd()), sep="/")
options(warn=1)

getVars <- function(vcf.file){
  cat(paste("Processing ", vcf.file, "...\n", sep=" "))
  vcf <- readVcf(vcf.file, genome="hg19")
  vcf <- vcf[isSNV(vcf)]
  vars <- rowRanges(vcf)
  vars <- as(vars, "DataFrame")
  vars$query <- formatHgvs(vcf, "snp")
  annotations <- getVariants(vars$query, fields=c("dbnsfp.genename", "dbnsfp.1000gp1.af", 
                                                  "exac.af", "cadd.consequence", "cadd.phred"))
  annotations[c('DP', 'FS', 'QD')] <- info(vcf)[c('DP', 'FS', 'QD')]
  annotations <- replaceWith0(annotations)
  annotations
}

vars <- lapply(vcf.files, getVars)

filter1 <- lapply(vars, function(i) subset(i, DP > 8))
cat(paste(nrow(subset(data.frame(table(unlist(lapply(filter1, function(i) unique(i$dbnsfp.genename))))), 
                      Freq == 4)), "genes remain after filtering for coverage and strand bias"))

filter2 <- lapply(filter1, function(i) subset(i, cadd.consequence %in% c("NON_SYNONYMOUS", "STOP_GAINED", "STOP_LOST", 
                                                                         "CANONICAL_SPLICE", "SPLICE_SITE")))
cat(paste(nrow(subset(data.frame(table(unlist(lapply(filter2, function(i) unique(i$dbnsfp.genename))))), 
                      Freq == 4)), "genes remain after filtering for nonsynonymous and splice site variants"))

filter3 <- lapply(filter2, function(i) subset(i, exac.af < 0.01))
cat(paste(nrow(subset(data.frame(table(unlist(lapply(filter3, function(i) unique(i$dbnsfp.genename))))), 
                      Freq == 4)), "genes remain after filtering for allele frequency < 0.01 in the ExAC dataset"))

filter4 <- lapply(filter3, function(i) subset(i, sapply(dbnsfp.1000gp1.af, function(j) j < 0.01 )))

top.genes <- subset(data.frame(table(unlist(lapply(filter4, function(i) unique(i$dbnsfp.genename))))), Freq == 4)
top.genes <- subset(top.genes, !(Var1 %in% c("NULL", 0)))
cat(paste(nrow(top.genes), "genes remain after filtering for allele frequency < 0.01 in 1000 Genomes Project"))

top.genes$Var1
ranked <- rankByCaddScore(top.genes$Var1, filter4)
ranked
res <- data.frame(queryMany(ranked$gene, scopes="symbol", species="human", fields=c("go.BP", "name", "MIM", "uniprot")))
miller.bp <- lapply(res$go.BP, function(i) unlist(i$id))
bp.ancestor <- lapply(miller.bp, function(i) sapply(i, function(j) "GO:0008152" %in% unlist(GOBPANCESTOR[[j]])))
candidate.genes <- ranked$gene[sapply(bp.ancestor, function(i) TRUE %in% i)]
candidate.genes