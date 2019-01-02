#!/usr/bin/env python

# vim: syntax=python tabstop=4 expandtab

#-------------------------------
# @author: Mahesh Vangala
# @email: vangalamaheshh@gmail.com
# @date: Aug, 1, 2015
#-------------------------------

import os
import glob
import subprocess
from scripts.csv_to_sphinx_table import get_sphinx_table 
from snakemake.report import data_uri

def viper_data_uri(path):
    """Wrapper fn to help accomodate changes in data_uri starting in 
    snakemake v5.1.1, where the return is a tuple (uri, mime) rather than 
    just uri. 
    This fn will return the URI
    """
    tmp=data_uri(path)
    if type(tmp) is tuple:
        return tmp[0]
    else:
        return tmp
    
def get_sphinx_report(config):
    comps = config["comparisons"]
    git_commit_string = subprocess.check_output('git --git-dir="viper/.git" rev-parse --short HEAD',shell=True).decode('utf-8').strip()
    git_link = 'https://bitbucket.org/cfce/viper/commits/' + git_commit_string
    file_dict = {
        'align_report': "analysis/" + config["token"] + "/STAR/STAR_Align_Report.png",
        'rRNA_report': "analysis/" + config["token"] + "/STAR_rRNA/STAR_rRNA_Align_Report.png",
        'read_distrib': "analysis/" + config["token"] + "/RSeQC/read_distrib/read_distrib.png",
        'gb_cov_heatmap': "analysis/" + config["token"] + "/RSeQC/gene_body_cvg/geneBodyCoverage.heatMap.png",
        'gb_cov_curves': "analysis/" + config["token"] + "/RSeQC/gene_body_cvg/geneBodyCoverage.curves.png",
        #OBSOLETE
        #'heatmapSF_plot': "analysis/" + config["token"] + "/plots/images/heatmapSF_plot.png",
        'heatmapSS_plot': "analysis/" + config["token"] + "/plots/images/heatmapSS_plot.png",
        'heatmapSS_cluster': "analysis/" + config["token"] + "/plots/images/heatmapSS_cluster.png",
        'DEsummary_plot': "analysis/" + config["token"] + "/diffexp/de_summary.png",
        'SNP_chr6' : "analysis/" + config["token"] + "/plots/sampleSNPcorr_plot.chr6.png",
        'SNP_HLA': "analysis/" + config["token"] + "/plots/sampleSNPcorr_plot.hla.png",
        'SNP_genome' : "analysis/" + config["token"] + "/plots/sampleSNPcorr_plot.genome.png",
        'FUSION_OUT': "analysis/" + config["token"] + "/STAR_Fusion/STAR_Fusion_Report.png"
    }
    #ENCODE images
    copy_file_dict = {}
    for (key, fpath) in file_dict.items():
        if os.path.isfile(fpath):
            copy_file_dict[key] = viper_data_uri(fpath)
    file_dict = copy_file_dict
    
    pca_png_list = []
    volcano_list = []
    SF_png_list = []
    gsea_list = []
    fgsea_list = []
    virusseq_out = "analysis/" + config["token"] + "/virusseq/virusseq_summary.csv"
    cdr_cpk_plot = "analysis/cdr3/CPK.png"

    for pca_plot in sorted(glob.glob("./analysis/" + config["token"] + "/plots/images/pca_plot*.png")):
        if "pca_plot_scree.png" not in pca_plot:
            pca_png_list.append(viper_data_uri(pca_plot))

    if(os.path.isfile("./analysis/" + config["token"] + "/plots/images/pca_plot_scree.png")):
        pca_png_list.append(viper_data_uri("./analysis/" + config["token"] + "/plots/images/pca_plot_scree.png"))    

    for volcano_plot in glob.glob("./analysis/" + config["token"] + "/plots/images/*_volcano.png"):
        volcano_list.append(viper_data_uri(volcano_plot))

    for SF_plot in sorted(glob.glob("./analysis/" + config["token"] + "/plots/images/heatmapSF_*_plot.png")):
        SF_png_list.append(viper_data_uri(SF_plot))

    for comp in comps:
        tmp_f = "./analysis/%s/gsea/%s/%s.gene_set.enrichment.dotplot.png" % (config["token"], comp, comp)
        if (os.path.isfile(tmp_f)):
            gsea_list.append(viper_data_uri(tmp_f))
            
        fgsea_f = "./analysis/%s/fgsea/%s/%s.gene_set.enrichment.dotplot.png" % (config["token"], comp, comp)
        if (os.path.isfile(fgsea_f)):
            fgsea_list.append(viper_data_uri(fgsea_f))
        

    if pca_png_list:
        file_dict['pca_png_list'] = pca_png_list
    if volcano_list:
        file_dict['volcano_png_list'] = volcano_list
    if SF_png_list:
        file_dict['sf_png_list'] = SF_png_list
    if gsea_list:
        file_dict['gsea_png_list'] = gsea_list
    if fgsea_list:
        file_dict['fgsea_png_list'] = fgsea_list
    report = """
==========================================================================================
VIPER: Visualization Pipeline for RNAseq - {sub_analysis_token}
==========================================================================================


Alignment Summary
=================
    Raw reads were mapped or aligned to the reference organism using `STAR software`_.

    .. _STAR software: https://github.com/alexdobin/STAR


    The **uniquely mapped read counts** and the **total read counts** for all the samples are summarized in the following image. In most cases, more than 70% of the reads should uniquely map to the reference genome.
    Contamination, low quality sequencing data, or poor library contruction may result in <60% uniquely aligned reads.

""".format(sub_analysis_token = config["token"])
    if 'align_report' in file_dict:
        report += "\n\t.. image:: " + file_dict['align_report'] + "\n";

    report += "\n"

    report += """
Library Prep Quality Metrics
=============================
Read Distribution QC
^^^^^^^^^^^^^^^^^^^^^^^^^^
    This graph displays the disibution of reads mapped to **features** across the genome for each sample. Distribution profiles should be similar across samples.
    A sample with a siginficantly different distribution profile may indicate that it was initially a poor sample or that there was a problem during library preparation.
    **mRNAseq libraries will typically contain less than 20% intronic mapped reads** whereas **totalRNAseq libraries may have greater than 40% intronic mapped reads**.
"""

    if 'read_distrib' in file_dict:
        report += "\n\t.. image:: " + file_dict['read_distrib'] + "\n";

    report += "\n"
    report += """
rRNA removal QC
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    This graph displays the percentage of reads mapping to ribosomal RNA reference sequences. Most RNAseq library prep methods are designed to avoid sampling ribosomal RNAs which typically represent greater than 80% of total RNA. If rRNA removal was effective, less than 5% of the reads should map to rRNA sequences and for mRNA libraries fewer than 1%.
"""

    if 'rRNA_report' in file_dict:
        report += "\n\t.. image:: " + file_dict['rRNA_report'] + "\n";

    report += "\n"
    report += """
Genebody Coverage
^^^^^^^^^^^^^^^^^
    For accurate gene expression quantification, mapped reads should be evenly distributed across genebodies.
    Significantly skewed profiles (5' or 3') may introduce quantification bias and/or represent poor quality library preparation.\n
    For example, mRNAseq library preps typically use oligo-dT beads to capture mature transcripts and can be prone to 3' bias in genebody coverage if degraded RNA \(RIN < 7\) is used as input. This may result in inaccurate gene quantification and the following graphs will help diagnose.
    There are other prep methods that may result in 5' bias too. Ideally, coverage should be uniform across the genebody. The line plots should look like this: "∩"

    Figures generated using `RSeQC software`_.

    .. _RSeQC software: http://rseqc.sourceforge.net

    **Line Plot**
"""

    if 'gb_cov_curves' in file_dict:
        report += "\n\t.. image:: " + file_dict['gb_cov_curves'] + "\n";

    report += "\n"
    report += """
    **Heatmap**\n
    This graphic may facilitate identification of biased samples.\n
    Scale: Blue = 0 Pink =1

"""

    if 'gb_cov_heatmap' in file_dict:
        report += "\n\t.. image:: " + file_dict['gb_cov_heatmap'] + "\n";

    report += "\n"
    report += """
Experimental Quality Control
===============================

Principle Component Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    High dimensional expression data are mathmatically reduced to principle
    components that can be used to describe variation across samples in fewer dimensions to allow human interpretation.
    Principle component 1 \(PC1\) accounts for the most amount of variation across samples, PC2 the second most, and so on. These PC1 vs PC2 plots
    are colored by sample annotation to demontrate how samples cluster together \(or not\) in reduced dimensional space.
    For more detailed description of Princilple Component Analysis, start with `wikipedia`_.

    .. _wikipedia: https://en.wikipedia.org/wiki/Principal_component_analysis

"""

    if 'pca_png_list' in file_dict:
        if len(file_dict['pca_png_list']) > 1:
            report += "\n\t.. image:: " + "\n\t.. image:: ".join(file_dict['pca_png_list'][:-1]) + "\n"
            report += "\n\t" + 'This plot indicates how much of the overall variance is described by the principle components in descending order.' + "\n\n\t.. image:: " + file_dict['pca_png_list'][-1] + "\n"
        else:
            report += "\n\n\t.. image:: " + file_dict['pca_png_list'][0] + "\n"
            report += "\n\t" + "This plot indicates how much of the overall variance is described by the principle components in descending order.\n"
    report += "\n"
    report += """
Sample-to-Sample Correlation Heatmap
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    This heatmap displays hierarchical clustering of spearman rank correlations across samples.
    Highly correlated samples will cluster together and be represented in red. Samples that do not correlate will be represented in blue.

"""

    if 'heatmapSS_plot' in file_dict:
        report += "\n\n\t.. image:: " + file_dict['heatmapSS_plot'] + "\n\n\t" + 'Sample-to-Sample data matrix is /analysis/plots/heatmapSS.txt' + "\n"

    report += "\n"
    report += """
Sample-Feature Correlation Heatmap
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    This heatmap illustrates hierarchical clustering of samples based on the top 5 percent or roughly 1000 most variable genes or "features."
    The top colomn color annotations are presented to help identify how sample types, groups, or treatments are clustering together \(or not\).

"""
    #OBSOLETE?
    #if 'heatmapSF_plot' in file_dict:
    #    report += "\n\n\t.. image:: " + file_dict['heatmapSF_plot'] + "\n";

    if 'sf_png_list' in file_dict:
        report += "\n\t.. image:: " + "\n\t.. image:: ".join(file_dict['sf_png_list'][:]) + "\n"

    report += "\n\n\t" + 'What are *these* genes?' + "\n\n\t" + 'Data used to generate this sample-feature graphic are in /analysis/plots/heatmapSF.txt' + "\n"

    report += "\n"

    if 'FUSION_OUT' in file_dict:
        report += """
Fusion Summary
==============
"""
        report += "\n\t.. image:: " + file_dict['FUSION_OUT'] + "\n";

    report += "\n"
 
    report += """                
Differential Gene expression
============================
    Differential gene expression analysis was performed using both `limma`_ and `DESeq2`_.\n
    Full analysis output tables are are available in /analysis/diffexp/comparison_of_interest

    .. _limma: https://www.bioconductor.org/packages/3.3/bioc/vignettes/limma/inst/doc/usersguide.pdf

    .. _DESeq2: http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4302049/

    This summary image shows the number of genes that are up regulated and down regulated across each comparison at different adjusted P-value cut-offs.

"""

    if 'DEsummary_plot' in file_dict:
        report += "\n\n\t.. image:: " + file_dict['DEsummary_plot'] + "\n"

    report += "\n"
    report += """
Volcano Plots
^^^^^^^^^^^^^^
    Volcano plots are commonly used graphical representations of differentially expressed genes and statistical significance.
    These scatter plots show log2 fold change versus P-value for all genes detected. Each data point represents a gene. Genes are colored red if the log2 fold change is greater than one \(log2fc > 1\). Genes are colored blue if the log2 fold change is less than negative one \(log2fc < -1\).
    The plot title indicates the direction of the comparison.
    For example, "treatment_vs_control" indicates that genes colored red are up-regulated in the treatment condition compared to the control condition with a statistically significant P-value.

"""

    if 'volcano_png_list' in file_dict:
        report += "\n\n\t.. image:: " + "\n\n\t.. image:: ".join(file_dict['volcano_png_list'][:]) + "\n"

    report += "\n"
    report += """
SNP Plots
==========
    
"""
    if 'SNP_chr6' in file_dict:
        report += "\n"
        report += """
SNP - Chr6
^^^^^^^^^^^
"""  
        report += "\n\n\t.. image:: " + file_dict['SNP_chr6'] + "\n"

    if 'SNP_HLA' in file_dict:
        report += "\n"
        report += """
SNP - HLA
^^^^^^^^^^^
"""
        report += "\n\n\t.. image:: " + file_dict['SNP_HLA'] + "\n"


    if 'SNP_genome' in file_dict:
        report += "\n" 
        report += """
SNP - Genome-wide
^^^^^^^^^^^^^^^^^^
"""
        report += "\n\n\t.. image:: " + file_dict['SNP_genome'] + "\n"

    report += """
Pathway-Analysis
================

Gene-Ontology Annotation
========================
"""
    for comp in comps:
        report += "\n" + comp + "\n"
        report += "^" * len(comp) + "\n"
        go_png = "analysis/" + config["token"] + "/plots/images/" + comp + "_goterm.up.png"
        if os.path.isfile(go_png):
            report += "\n\n\t.. image:: " + viper_data_uri(go_png) + "\n"
        else:
            report += "\nInsufficient data\n"

    report += """
KEGG-Pathway Analysis
=====================
"""
    for comp in comps:
        report += "\n" + comp + "\n"
        report += "^" * len(comp) + "\n"
        cur_path = "analysis/" + config["token"] + "/diffexp/" + comp + "/kegg_pathways/"
        path_list =  glob.glob(cur_path + "*.png")
        if not path_list:
            report += "\nInsufficient data\n"
        else:
            report += "\n\n\t.. image:: " + viper_data_uri(path_list[0]) + "\n"
            token = ",".join([os.path.basename(file_path) for file_path in path_list[1:]]).replace(".png","")
            if token:
                report += "\n" + "More pathway plots such as, " + token + " - can be found at " + cur_path + ".\n"    

#------------------------------------------------------------------------------
# GSEA section
#------------------------------------------------------------------------------
    report += """
GSEA
====
    Gene Set Enrichment Analysis (using GSEA) was performed on the significant differentially expressed genes using the clusterProfiler R package
"""
    if 'gsea_png_list' in file_dict:
        report += "\n\n\t.. image:: " + "\n\n\t.. image:: ".join(file_dict['gsea_png_list'][:]) + "\n"
    report += "\n"

#------------------------------------------------------------------------------
# FGSEA section
#------------------------------------------------------------------------------
    report += """
FGSEA
=====
    Gene Set Enrichment Analysis (using fgsea) was performed on the significant differentially expressed genes using the clusterProfiler R package
"""
    if 'fgsea_png_list' in file_dict:
        report += "\n\n\t.. image:: " + "\n\n\t.. image:: ".join(file_dict['fgsea_png_list'][:]) + "\n"
    report += "\n"

#------------------------------------------------------------------------------
# Virusseq section
#------------------------------------------------------------------------------
    if os.path.isfile(virusseq_out):
        report += """
Virus-Seq Module Output
=======================
"""
        report += "\n" + get_sphinx_table(virusseq_out) + "\n"

    if os.path.isfile(cdr_cpk_plot):
        report += """
CDR3 analysis (using trust v2.4.1)
==================================
"""
        report += "\n\n\t.. image:: " + viper_data_uri(cdr_cpk_plot) +"\n"

    report += "\n\n**This report is generated using VIPER version** [ `" + git_commit_string + "`_ ].\n"
    report += "\t.. _" + git_commit_string + ': ' + git_link + "\n\n"
    report += "\n\n**To cite VIPER:\nCornwell M, Vangala M, Taing L, Herbert Z, Köster J, Li B, Sun H, Li T, Zhang J, Qiu X, Pun M, Jeselsohn R, Brown M, Liu XS, Long HW. VIPER: Visualization Pipeline for RNA-seq, a Snakemake workflow for efficient and complete RNA-seq analysis. BMC Bioinformatics. 2018 Apr 12; 19(1):135.**\n\n"
    return report + "\n"


