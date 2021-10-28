PCA_all_samples <- function(scaled_ct) {
  t <- t(scaled_ct[, c(-1,-2)])
  prin_comp <- prcomp(t, rank. = 2)
  components <- prin_comp[["x"]]
  components <- data.frame(components)
  components <- cbind(components, rownames(t))
  components$PC2 <- -components$PC2
  
  fig <- plot_ly(components, x = ~PC1, y = ~PC2, color = cells, width = Fig_width, height = Fig_height,
                 type = 'scatter', mode = 'markers', text = components$`rownames(t)`)
  fig
}
run_deseq_salmon <- function(samplesheet) {
  files <- file.path(DIR_salmon, samplesheet$sample, "quant.sf")
  names(files) <- samplesheet$sample
  tx2gene <- read_csv(FILE_tx2gene)
  
  txi <- tximport(files, type="salmon", tx2gene=tx2gene)
  
  ddsTxi <- DESeqDataSetFromTximport(txi,
                                     colData = samplesheet,
                                     design = ~ group)
  
  dds <- DESeq(ddsTxi)
  normalized_counts <- counts(dds, normalized=TRUE)
  normalized_counts2 <- merge(scaled_ct[,1:2], normalized_counts, by.x="gene_id", by.y="row.names")
  
  res <- results(dds)
  res_combined <- merge(res, normalized_counts, by="row.names", all.x=T, all.y=F)
  res_combined <- res_combined[complete.cases(res_combined), ]
  res_combined <- merge(scaled_ct[,1:2], res_combined, by.x="gene_id", by.y="Row.names")
  res_combined <- res_combined[complete.cases(res_combined), ]
  
  res_combined_sig <- res_combined[res_combined$padj < CUTOFF_ADJP,]
  res_combined$sig <- "Non-sig."
  res_combined$sig[res_combined$padj < CUTOFF_ADJP] <- "Sig. genes"
  output <- list(norm_count=normalized_counts2, 
                 deseq2res=res_combined,
                 deseq2res_sig=res_combined_sig
  )
  return(output)
}

PCA_after_deseq2 <- function(normalized_counts2, samples) {
  t <- t(normalized_counts2[, c(-1,-2)])
  prin_comp <- prcomp(t, rank. = 2)
  components <- prin_comp[["x"]]
  components <- data.frame(components)
  components <- cbind(components, rownames(t))
  # components$PC2 <- -components$PC2
  
  labels <- samples$sample
  labels_group <- samples$group
  fig <- plot_ly(components, x = ~PC1, y = ~PC2, color = labels_group, text = labels, 
                 width = Fig_width, height = Fig_height,
                 type = 'scatter', mode = 'markers')
  fig
}

volcano_plot <- function(res_combined) {
  pal <- c("red", "royalblue")
  pal <- setNames(pal, c("Sig. genes", "Non-sig."))
  fig <- plot_ly(x = res_combined$log2FoldChange, 
                 y = -log10(res_combined$padj),
                 text = res_combined$gene_name,
                 hoverinfo = 'text',
                 marker = list(opacity = 0.2),
                 color = res_combined$sig, colors = pal, 
                 showlegend = T)  %>%
    layout(
      title = "Volcano plot",
      xaxis = list(title = "Fold Change (log2)"),
      yaxis = list(title = "adjusted p-value (-log10)")
    )
  fig
}


heatmap_expression <- function(deseq2res) {
  top1000 <- deseq2res[order(deseq2res$padj, decreasing = FALSE), ]
  top1000 <- top1000[1:1000,]
  
  heatmap_t <- log10(top1000[,9:(dim(top1000)[2]-1)]+1)
  heatmaply(heatmap_t, main = "Heatmap of top 1000 genes ranked by adj. p-value",method = "plotly",
            xlab = "Samples", ylab = "Genes", width = Fig_width, height = Fig_height+200,
            showticklabels = c(TRUE, FALSE), show_dendrogram = c(FALSE, TRUE),
            key.title = "Scaled\nexpression\nin log10 scale",
            k_col = 3)
}



table_all_normalized_quantified_values <- function(normalized_counts) {
  
  datatable( normalized_counts ,
             extensions = c("Buttons" , "FixedColumns"),
             filter = 'top',
             options = list( autoWidth = TRUE , 
                             dom = 'Blftip',
                             pageLength = 10,
                             searchHighlight = FALSE,
                             buttons = c('copy', 'csv', 'print'),
                             scrollX = TRUE,
                             fixedColumns = list(leftColumns = 1)),
             class = c('compact cell-border stripe hover') ,
             rownames = FALSE) %>% formatRound(columns = c(-1,-2),digits=2) 
}

table_diffexp_statistics <- function(deseq2res) {
  datatable( deseq2res ,
             extensions = c("Buttons" , "FixedColumns"),
             filter = 'top',
             options = list( autoWidth = TRUE , 
                             dom = 'Blftip',
                             pageLength = 10,
                             searchHighlight = FALSE,
                             buttons = c('copy', 'csv', 'print'),
                             scrollX = TRUE,
                             fixedColumns = list(leftColumns = 2)),
             class = c('compact cell-border stripe hover') ,
             rownames = FALSE) %>% formatRound(c(-1, -2), 2) 
}

table_sig_genes <- function(res_sig) {
  datatable( res_sig ,
             extensions = c("Buttons" , "FixedColumns"),
             filter = 'top',
             options = list( autoWidth = TRUE , 
                             dom = 'Blftip',
                             pageLength = 10,
                             searchHighlight = FALSE,
                             buttons = c('copy', 'csv', 'print'),
                             scrollX = TRUE,
                             fixedColumns = list(leftColumns = 2)),
             class = c('compact cell-border stripe hover') ,
             rownames = FALSE) %>% formatRound(c(-1, -2), 2) 
}