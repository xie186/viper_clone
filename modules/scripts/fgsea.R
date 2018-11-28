#Script to run enricher fn on most significantly diffexp genes

#based on this website
#ref: https://stephenturner.github.io/deseq-to-fgsea/

suppressMessages(library(fgsea))
suppressMessages(library(magrittr))
suppressMessages(library(dplyr))
suppressMessages(library(tibble))
suppressMessages(library(ggplot2))
suppressMessages(library(data.table))

fgsea_fn <- function(deseqTable, gsea_db, comp_title, out_path) {
   #Constant used to determine how many of the top hits to use
   N <- 10
   gmt <- gmtPathways(gsea_db)
    
   #get set of significant diffexp genes--threshold 0.05
   genes <- deseqTable[deseqTable$padj < 0.05,]
   #genes<-deseqTable
   #sort by log2FC (decreasing! **I think this is the key!)
   genes <- genes[order(genes$log2FoldChange, decreasing=T),]
    
   #get list of gene names
   gene_list<- rownames(genes)

   #WRITE this as out_gene_list
   write(gene_list, file=paste0(out_path, ".gene_list.txt"), ncolumns=1)

   #GENERATE ranks list
   ranks <- data.frame("ID"=gene_list, "log2FC"=genes$log2FoldChange)
   ranks <- setNames(ranks$log2FC, ranks$ID)

   #fgseaRes <- fgsea(gmt, ranks, minsize=15, maxSize=500,  nperm=1000)
   fgseaRes <- fgsea(gmt, ranks, maxSize=500,  nperm=1000)
    
   fgseaResTidy <- fgseaRes %>%
      as_tibble() %>%
      arrange(desc(NES))

   fwrite(fgseaRes, file=paste0(out_path, ".gene_set.enrichment.txt"), sep=",")
    
   #Take top and bottom 10
   fgseaTop <- top_n(fgseaResTidy, N, NES)
   fgseaBottom <- top_n(fgseaResTidy, -N, NES)
   fgseaTopAndBottom <- bind_rows(fgseaTop,fgseaBottom)

   png(paste0(out_path, ".gene_set.enrichment.dotplot.png"), width = 8, height = 8, unit="in",res=300)
   plot <- ggplot(fgseaTopAndBottom, aes(reorder(pathway, NES), NES)) +
       geom_col(aes(fill=padj<0.05)) +
       coord_flip() +
       labs(x="Pathway", y="Normalized Enrichment Score",
            title=comp_title) + 
       theme_minimal()
   print(plot)
   junk <- dev.off()   
}

## Read in arguments
args <- commandArgs( trailingOnly = TRUE )
deseqFile=args[1]
gsea_db=args[2]
title=args[3]
out_path=args[4]

deseqTable <- read.csv(deseqFile, header=T, check.names=F, row.names=1, stringsAsFactors=FALSE, dec='.', colClasses=c('character','numeric','numeric','numeric','numeric','numeric','numeric'))
fgsea_fn(deseqTable, gsea_db, title, out_path) 
