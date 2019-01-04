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
from string import Template

_ReportTemplate = Template(open("viper/modules/scripts/viper_report.txt").read())

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
    else:
        file_dict['pca_png_list'] = ""
    if volcano_list:
        file_dict['volcano_png_list'] = volcano_list
    else:
        file_dict['volcano_png_list'] = ""
    if SF_png_list:
        file_dict['sf_png_list'] = SF_png_list
    else:
        file_dict['sf_png_list'] = ""
    if gsea_list:
        file_dict['fgsea_png_list'] = fgsea_list
    else:
        file_dict['fgsea_png_list'] = ""

    report = _ReportTemplate.safe_substitute(align_report=file_dict["align_report"], read_distrib=file_dict["read_distrib"], rRNA_report=file_dict["rRNA_report"], 
        gb_cov_curves=file_dict["gb_cov_curves"], gb_cov_heatmap=file_dict["gb_cov_heatmap"], pca_png_list="\n".join(file_dict["pca_png_list"]), heatmapSS_plot=file_dict["heatmapSS_plot"],
        sf_png_list="\n".join(file_dict["sf_png_list"]), fgsea_list="\n".join(file_dict["fgsea_png_list"]), DEsummary_plot = file_dict["DEsummary_plot"],
        volcano_png_list="\n".join(file_dict["volcano_png_list"]))
        #, FUSION_OUT = file_dict["FUSION_OUT"], 
        #  SNP_chr6=file_dict["SNP_chr6"], SNP_genome=file_dict["SNP_genome"]
        #heatmapSF_plot=file_dict["heatmapSF_plot"],
    return report