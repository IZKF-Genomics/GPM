###########################################################
## Description
###########################################################

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

###########################################################
## RNAseq
###########################################################

add_DGEA <- function(description, tag, filtered_samples) {
  scripts  <- readLines("DGEA_template.Rmd")
  scripts  <- gsub(pattern = "TITLEDESCRIPTION", replace = description, x = scripts)
  scripts  <- gsub(pattern = "FILETAG", replace = tag, x = scripts)
  tmp_samplesheet <- paste0("DGEA_", tag, "_data.RData")
  save(filtered_samples, file = tmp_samplesheet)
  scripts  <- gsub(pattern = "SAMPLE_RData", replace = tmp_samplesheet, x = scripts)
  filename <- paste0("DGEA_",tag)
  writeLines(scripts, con=paste0(filename,".Rmd"))
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

###########################################################
## RNAseq figures
###########################################################
PCA_plotly <- function(scaled_ct, colors) {
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

RNAseq_PCA_plotly <- function(normalized_counts2, samples) {
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

RNAseq_volcano_plotly <- function(res_combined) {
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

RNAseq_maplot_plotly <- function(res_combined) {
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

RNAseq_maplot_plotly_ERCC <- function(res_combined_ERCC) {
  # res_combined <- deseq_output$deseq2res
  # res_combined_ERCC <- deseq_output$deseq2res_ERCC
  # res_df <- rbind(res_combined, res_combined_ERCC)
  pal <- c("red", "gray", "orange")
  pal <- setNames(pal, c("Sig. genes", "Non-sig.", "Spike in"))
  # res_combined$sig <- factor(res_combined$sig, level=c("Sig. genes", "Spike in", "Non-sig."))
  
  fig <- plot_ly(x = log2(res_combined_ERCC$baseMean),
              y = res_combined_ERCC$log2FoldChange,
              text = res_combined_ERCC$gene_name,
              hoverinfo = 'text',
              marker = list(opacity = 0.5),
              color = res_combined_ERCC$sig, colors = pal,
              showlegend = T) %>%
        layout(
          title = "MA plot of spike in",
          xaxis = list(title = "Mean Expression (log2)"),
          yaxis = list(title = "Fold Change (log2)")
        )
  fig
}

RNAseq_heatmap_plotly <- function(deseq2res) {
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

RNAseq_PCA_ggplot2 <- function(deseq_output, samples2) {
  t <- t(deseq_output$norm_count[, c(-1,-2)])
  prin_comp <- prcomp(t, rank. = 2)
  components <- prin_comp[["x"]]
  components <- data.frame(components)
  components <- cbind(components, rownames(t))
  labels <- samples2$sample
  labels_group <- samples2$group

  fig <- ggplot(components, aes(PC1, PC2, color=labels_group)) +
        geom_point(size=3) + theme_bw() + scale_color_brewer(palette = "Set1") + 
        labs(color = "Groups") + ggtitle("PCA") +
        theme(plot.title = element_text(hjust = 0.5))
  fig
}

RNAseq_volcano_ggplot2 <- function(deseq_output) {
  pal <- c("red", "royalblue")
  pal <- setNames(pal, c("Sig. genes", "Non-sig."))
  xmax <- max(abs(deseq_output$deseq2res$log2FoldChange)) * 1.1
  ymax <- max(-log10(deseq_output$deseq2res$padj)[is.finite(-log10(deseq_output$deseq2res$padj))]) * 1.1
  fig <- ggplot(deseq_output$deseq2res, aes(log2FoldChange, -log10(padj), color=sig)) +
        geom_point(size=1, alpha=0.2) + theme_bw() + scale_color_manual(values=pal) + 
        labs(color = "Groups") + ggtitle("Volcano plot") +
        xlab("Fold Change (log2)") + ylab("adjusted p-value (-log10)") +
        theme(plot.title = element_text(hjust = 0.5)) +
        xlim(-xmax, xmax) + ylim(0, ymax)
  fig
}

RNAseq_maplot_ggplot2 <- function(deseq_output) {
  pal <- c("red", "royalblue")
  pal <- setNames(pal, c("Sig. genes", "Non-sig."))
  ymax <- max(abs(deseq_output$deseq2res$log2FoldChange)) * 1.01

  fig <- ggplot(deseq_output$deseq2res, aes(log2(baseMean), log2FoldChange, color=sig)) +
        geom_point(size=1, alpha=0.2) + theme_bw() + scale_color_manual(values=pal) + 
        labs(color = "Groups") + ggtitle("MA plot") +
        xlab("Expresion Mean (log2)") + ylab("Fold Change (log2)") +
        theme(plot.title = element_text(hjust = 0.5)) +
        ylim(-ymax, ymax)
  fig
}

RNAseq_heatmap_ggplot2 <- function(deseq_output) {
  margin_spacer <- function(x) {
    # where x is the column in your dataset
    left_length <- nchar(levels(factor(x)))[1]
    if (left_length > 8) {
      return((left_length - 8) * 4)
    }
    else
      return(0)
  }
  top1000 <- deseq_output$deseq2res[order(deseq_output$deseq2res$padj, decreasing = FALSE), ]
  top1000 <- top1000[1:1000,]
  samples_names <- colnames(top1000)[9:(dim(top1000)[2]-1)]
  heatmap_t <- scale(log10(top1000[,9:(dim(top1000)[2]-1)]+1))
  ord <- hclust( dist(heatmap_t, method = "euclidean"), method = "ward.D" )$order

  heatmap_t <- cbind(top1000$gene_id, as.data.frame(heatmap_t))
  colnames(heatmap_t)[1] <- "gene_id"
  heatmap_t <- pivot_longer(heatmap_t, cols=2:(dim(heatmap_t)[2]), names_to="sample", values_to="Expression")
  heatmap_t$gene_id <- factor( heatmap_t$gene_id, levels = top1000$gene_id[ord])
  heatmap_t$sample <- factor( heatmap_t$sample, levels = samples_names)

  fig <- ggplot(heatmap_t, aes(sample, gene_id, fill=Expression)) + 
        geom_tile() + ggtitle("Heatmap of top 1000 genes ranked by padj") +
        ylab("Genes") + xlab("Samples") + scale_fill_viridis() + 
        theme(plot.title = element_text(hjust = 0.5),
              axis.ticks.y = element_blank(),
              axis.text.y = element_blank(),
              axis.text.x = element_text(angle = 45, vjust = 1, hjust=1),
              plot.margin = margin(l = 0 + margin_spacer(heatmap_t$sample)))
  fig
}
###########################################################
## Output tables
###########################################################

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

table_sig_genes <- function(res_sig, rowname=F) {
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
             rownames = rowname) %>% formatRound(c(-1, -2), 2)
}

###########################################################
## miRNAseq
###########################################################

miRNAseq_deseq2 <- function(FILE_counts_mature, FILE_counts_hairpin, samples2) {
  df_counts1 <- t(read.csv(FILE_counts_mature, row.names = 1, header=T, sep=","))[, samples2$sample]
  df_counts2 <- t(read.csv(FILE_counts_hairpin, row.names = 1, header=T, sep=","))[, samples2$sample]
  # df_counts <- df_counts1
  df_counts <- rbind(df_counts1, df_counts2)
  dds <- DESeqDataSetFromMatrix(countData = df_counts, colData = samples2, design = ~group)
  # ERCC normalization #####################
  # if (spikein==TRUE) {
  #   dds <- estimateSizeFactors_ERCC(dds)
  # }
  ##########################################
  dds <- DESeq(dds)
  res <- as.data.frame(results(dds))
  res <- cbind(data.frame(gene_name=rownames(res)), res)
  res$sig <- "Non-sig."
  res$sig[res$padj < CUTOFF_ADJP] <- "Sig."
  norm_counts <- counts(dds, normalized=TRUE)
  res_combined <- merge(res, norm_counts, by.x= "row.names", by.y="row.names", all.y=T)
  colnames(res_combined)[1] <- "gene_name"
  res_sig <- res[res$padj < CUTOFF_ADJP,]
  res_sig <- res_sig[complete.cases(res_sig), ]
  output <- list(res=res,
                 norm_counts=norm_counts,
                 res_combined=res_combined,
                 res_sig=res_sig)
  return(output)
}

miRNAseq_PCA_plotly <- function(normalized_counts, samples) {
  t <- t(normalized_counts)
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

miRNAseq_volcano_plotly <- function(res_combined) {
  pal <- c("red", "royalblue")
  pal <- setNames(pal, c("Sig.", "Non-sig."))
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

miRNAseq_maplot_plotly <- function(res_combined) {
  pal <- c("red", "royalblue")
  pal <- setNames(pal, c("Sig.", "Non-sig."))
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

miRNAseq_heatmap_plotly <- function(res_combined) {
  res_reorder <- res_combined[order(res_combined$padj, decreasing = FALSE), ]
  res_reorder <- res_reorder[1:500,]
  heatmap_t <- log10(res_reorder[,9:(dim(res_reorder)[2])]+1)
  rownames(heatmap_t) <- c()
  # heatmaply(heatmap_t, main = "Heatmap of miRNAs ranked by adj. p-value",
  #           method = "plotly")
  heatmaply(heatmap_t, main = "Heatmap of top 500 miRNAs ranked by adj. p-value",
            method = "plotly", #labRow=res_reorder$gene_name,
            xlab = "Samples", ylab = "miRNA", width = Fig_width, height = Fig_height+200,
            showticklabels = c(TRUE, FALSE), show_dendrogram = c(FALSE, TRUE),
            key.title = "Scaled\nexpression\nin log10 scale",
            label_names = c("gene_name", "sample", "Expression"),
            k_col = 3)
}

miRNAseq_PCA_ggplot2 <- function(res_miRNA, samples2){
  t <- t(res_miRNA$norm_counts)
  prin_comp <- prcomp(t, rank. = 2)
  components <- prin_comp[["x"]]
  components <- data.frame(components)
  components <- cbind(components, rownames(t))
  labels <- samples2$sample
  labels_group <- samples2$group

  fig <- ggplot(components, aes(PC1, PC2, color=labels_group)) +
        geom_point(size=3) + theme_bw() + scale_color_brewer(palette = "Set1") +
        labs(color = "Groups") + ggtitle("PCA") +
        theme(plot.title = element_text(hjust = 0.5))
  fig
}

miRNAseq_volcano_ggplot2 <- function(res_miRNA){
  pal <- c("red", "royalblue")
  pal <- setNames(pal, c("Sig.", "Non-sig."))
  xmax <- max(abs(res_miRNA$res$log2FoldChange)) * 1.1
  ymax <- max(-log10(res_miRNA$res$padj)[is.finite(-log10(res_miRNA$res$padj))]) * 1.1
  fig <- ggplot(res_miRNA$res, aes(log2FoldChange, -log10(padj), color=sig)) +
        geom_point(size=1, alpha=0.2) + theme_bw() + scale_color_manual(values=pal) +
        labs(color = "Groups") + ggtitle("Volcano plot") +
        xlab("Fold Change (log2)") + ylab("adjusted p-value (-log10)") +
        theme(plot.title = element_text(hjust = 0.5)) +
        xlim(-xmax, xmax) + ylim(0, ymax)
  fig
}

miRNAseq_maplot_ggplot2 <- function(res_miRNA){
  pal <- c("red", "royalblue")
  pal <- setNames(pal, c("Sig.", "Non-sig."))
  ymax <- max(abs(res_miRNA$res$log2FoldChange)) * 1.01

  fig <- ggplot(res_miRNA$res, aes(log2(baseMean), log2FoldChange, color=sig)) +
        geom_point(size=1, alpha=0.2) + theme_bw() + scale_color_manual(values=pal) +
        labs(color = "Groups") + ggtitle("MA plot") +
        xlab("Expresion Mean (log2)") + ylab("Fold Change (log2)") +
        theme(plot.title = element_text(hjust = 0.5)) +
        ylim(-ymax, ymax)
  fig
}

miRNAseq_heatmap_ggplot2 <- function(res_miRNA){
  margin_spacer <- function(x) {
    # where x is the column in your dataset
    left_length <- nchar(levels(factor(x)))[1]
    if (left_length > 8) {
      return((left_length - 8) * 4)
    }
    else
      return(0)
  }

  res_reorder <- res_miRNA$res_combined[order(res_miRNA$res_combined$padj, decreasing = FALSE), ]
  res_reorder <- res_reorder[1:500,]
  samples_names <- colnames(res_reorder)[9:(dim(res_reorder)[2])]
  heatmap_t <- scale(log10(res_reorder[,9:(dim(res_reorder)[2])]+1))
  ord <- hclust( dist(heatmap_t, method = "euclidean"), method = "ward.D" )$order

  heatmap_t <- cbind(res_reorder$gene_name, as.data.frame(heatmap_t))
  colnames(heatmap_t)[1] <- "gene_name"
  heatmap_t <- pivot_longer(heatmap_t, cols=2:(dim(heatmap_t)[2]), names_to="sample", values_to="Expression")
  heatmap_t$gene_name <- factor( heatmap_t$gene_name, levels = res_reorder$gene_name[ord])
  heatmap_t$sample <- factor( heatmap_t$sample, levels = samples_names)

  fig <- ggplot(heatmap_t, aes(sample, gene_name, fill=Expression)) +
        geom_tile() + ggtitle("Heatmap of top 500 genes ranked by padj") +
        ylab("Genes") + xlab("Samples") + scale_fill_viridis() +
        theme(plot.title = element_text(hjust = 0.5),
              axis.ticks.y = element_blank(),
              axis.text.y = element_blank(),
              axis.text.x = element_text(angle = 45, vjust = 1, hjust=1),
              plot.margin = margin(l = 0 + margin_spacer(heatmap_t$sample)))
  fig
}