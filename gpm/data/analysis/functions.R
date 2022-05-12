organism2method_des <- function(organism) {
  if (organism == "hsapiens") {
    method_des <- "human genome (GRCh38.p13)"
  } else if (organism == "mmusculus") {
    method_des <- "mouse genome (GRCm39)"
  }
  return(method_des)
}

spikein_ERCC2method <- function(spikein_ERCC) {
  if (spikein_ERCC==TRUE) {
    spikein_method <- "Reads were mapped to a composite genome made by concatenating the reference genome and 92 ERCC ExFold RNA Spike-In Mixes sequences (ThermoFisher)." 
    } else {
    spikein_method <- ""
    }
  return(spikein_method)
}

PCA_all_samples <- function(scaled_ct, colors) {
  t <- t(scaled_ct[, c(-1)])
  prin_comp <- prcomp(t, rank. = 2)
  components <- prin_comp[["x"]]
  components <- data.frame(components)
  components <- cbind(components, rownames(t))
  components$PC2 <- -components$PC2

  fig <- plot_ly(components, x = ~PC1, y = ~PC2, color = colors, 
                 width = Fig_width, height = Fig_height,
                 type = 'scatter', mode = 'markers', text = components$`rownames(t)`)
  fig
}

process_dds_res <- function(tx2gene, dds) {
  ensembl_genes <- data.frame(gene_id=tx2gene$gene_id, gene_name=tx2gene$gene_name)
  ensembl_genes <- ensembl_genes[!duplicated(ensembl_genes), ]

  normalized_counts <- counts(dds, normalized=TRUE)
  normalized_counts <- merge(ensembl_genes, normalized_counts, by.x="gene_id", by.y="row.names")

  res <- results(dds)
  res_combined <- merge(ensembl_genes, as.data.frame(res), by.x= "gene_id", by.y="row.names", all.x=F, all.y=T)
  res_combined <- merge(res_combined, normalized_counts, by=c("gene_id", "gene_name"), all.x=T, all.y=F)
  res_combined <- res_combined[complete.cases(res_combined), ]
  res_combined$sig <- "Non-sig."
  res_combined$sig[res_combined$padj < CUTOFF_ADJP] <- "Sig. genes"
  sel_ERCC <- str_detect(res_combined$gene_id, "^ERCC-*gene")
  res_combined$sig[sel_ERCC] <- "Spike in"
  res_combined <- res_combined[!sel_ERCC,]
  
  res_combined_sig <- res_combined[res_combined$padj < CUTOFF_ADJP,]

  output <- list(norm_count=normalized_counts,
                 deseq2res=res_combined,
                 deseq2res_sig=res_combined_sig
  )
  return(output)
}

run_deseq_salmon <- function(samplesheet, spikein=FALSE) {
  files <- file.path(DIR_salmon, samplesheet$sample, "quant.sf")
  names(files) <- samplesheet$sample
  tx2gene <- fread(FILE_tx2gene, col.names = c("transcript_id", "gene_id", "gene_name"))
  txi <- tximport(files, type="salmon", tx2gene=tx2gene[,c(1,2)])

  ddsTxi <- DESeqDataSetFromTximport(txi,
                                     colData = samplesheet,
                                     design = ~ group)
  # ERCC normalization #####################
  if (spikein==TRUE) {
    ddsTxi <- estimateSizeFactors_ERCC(ddsTxi)
  }
  ##########################################
  dds <- DESeq(ddsTxi)
  output <- process_dds_res(tx2gene, dds)
  return(output)
}

run_deseq_salmon_batch <- function(samplesheet, spikein=FALSE) {
  files <- file.path(DIR_salmon, samplesheet$sample, "quant.sf")
  names(files) <- samplesheet$sample
  tx2gene <- fread(FILE_tx2gene, col.names = c("transcript_id", "gene_id", "gene_name"))

  txi <- tximport(files, type="salmon", tx2gene=tx2gene[,c(1,2)])

  ddsTxi <- DESeqDataSetFromTximport(txi,
                                     colData = samplesheet,
                                     design = ~batch + group)
  # ERCC normalization #####################
  if (spikein==TRUE) {
    ddsTxi <- estimateSizeFactors_ERCC(ddsTxi)
  }
  ##########################################
  dds <- DESeq(ddsTxi)
  output <- process_dds_res(tx2gene, dds)
  return(output)
}

estimateSizeFactors_ERCC <- function(ddsTxi) {
  sel_ERCC <- str_detect(rownames(ddsTxi), "^ERCC-*")
  # ddsTxi <- estimateSizeFactors(ddsTxi, controlGenes=str_detect(rownames(ddsTxi), "^ERCC-*"))
  sizeFactors(ddsTxi) <- estimateSizeFactorsForMatrix(counts(ddsTxi)[sel_ERCC,])
  # sizeFactors(ddsTxi)
  return(ddsTxi)
}

PCA_after_deseq2 <- function(normalized_counts2, samples) {
  t <- t(normalized_counts2[, c(-1,-2)])
  prin_comp <- prcomp(t, rank. = 2)
  components <- prin_comp[["x"]]
  components <- data.frame(components)
  components <- cbind(components, rownames(t))
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
                 type = 'scatter', mode = 'markers',
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

MA_plot <- function(res_combined) {
  pal <- c("red", "gray")
  pal <- setNames(pal, c("Sig. genes", "Non-sig."))
  fig <- plot_ly(x = log2(res_combined$baseMean),
                 y = res_combined$log2FoldChange,
                 text = res_combined$gene_name,
                 hoverinfo = 'text',
                 type = 'scatter', mode = 'markers',
                 marker = list(opacity = 0.2),
                 color = res_combined$sig, colors = pal,
                 showlegend = T)  %>%
    layout(
      title = "MA plot",
      xaxis = list(title = "Mean Expression (log2)"),
      yaxis = list(title = "Fold Change (log2)")
    )
  fig
}

heatmap_expression <- function(deseq2res) {
  top1000 <- deseq2res[order(deseq2res$padj, decreasing = FALSE), ]
  top1000 <- top1000[1:1000,]
  
  heatmap_t <- log10(top1000[,9:(dim(top1000)[2]-1)]+1)
  rownames(heatmap_t) <- c()
  heatmaply(heatmap_t, main = "Heatmap of top 1000 genes ranked by adj. p-value",
            method = "plotly",labRow=top1000$gene_name,
            xlab = "Samples", ylab = "Genes", width = Fig_width, height = Fig_height+200,
            showticklabels = c(TRUE, FALSE), show_dendrogram = c(FALSE, TRUE),
            key.title = "Scaled\nexpression\nin log10 scale",
            label_names = c("Gene", "Sample", "Expression"),
            k_col = 2)
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
  res <- subset(res_sig, select = -c(sig) )
  datatable( res ,
             extensions = c("FixedColumns"),
             filter = 'top',
             options = list( autoWidth = TRUE ,
                             dom = 'Blftip',
                             pageLength = 10,
                             searchHighlight = FALSE,
                            #  buttons = c('copy', 'csv', 'print'),
                             scrollX = TRUE,
                             fixedColumns = list(leftColumns = 2)),
             class = c('compact cell-border stripe hover') ,
             rownames = FALSE) %>% formatRound(c(-1, -2), 2)
}
