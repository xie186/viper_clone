#!/usr/bin/env python

# vim: syntax=python tabstop=4 expandtab
# coding: utf-8

#NOTE: this file was copied from gsea.snakefile

#relying on these being in gsea.snakefile which imported before this one!

# def gseaInputFn(wildcards):
#     """We need to handle whether this is a mouse run--if so, convert
#     the mouse genes to human genes in prep for GSEA analysis"""
#     if 'assembly' in config and config['assembly'].startswith("mm"):
#         return ["analysis/" + config["token"] + "/diffexp/%s/%s.deseq.converted.csv" % (wildcards.comparison, wildcards.comparison)]
#     else:
#         return ["analysis/" + config["token"] + "/diffexp/%s/%s.deseq.csv" % (wildcards.comparison, wildcards.comparison)]

# rule convertMouseToHuman:
#     """A rule to convert mouse to human"""
#     input:
#         deseq = "analysis/" + config["token"] + "/diffexp/{comparison}/{comparison}.deseq.csv"
#     params:
#         map_f = "viper/static/gsea/mmToHsGeneMap.csv"
#     message: "FGSEA: converting mouse genes to human genes"
#     output:
#         "analysis/" + config["token"] + "/diffexp/{comparison}/{comparison}.deseq.converted.csv"
#     shell:
#         "viper/modules/scripts/mmGeneToHs.py -m {params.map_f} -i {input} -o {output}"

rule fgsea:
    input:
        gseaInputFn
    output:
        gene_list = "analysis/" + config["token"] + "/fgsea/{comparison}/{comparison}.gene_list.txt",
        gsea = "analysis/" + config["token"] + "/fgsea/{comparison}/{comparison}.gene_set.enrichment.txt",
        dotplot = "analysis/" + config["token"] + "/fgsea/{comparison}/{comparison}.gene_set.enrichment.dotplot.png",
    params:
        db = config["fgsea_db"],
        out_path = "analysis/" + config["token"] + "/fgsea/{comparison}/{comparison}",
        title = "{comparison}"
    message: "Running FGSEA Analysis on {wildcards.comparison}"
    shell:
        "Rscript viper/modules/scripts/fgsea.R {input} {params.db} \"{params.title}\" {params.out_path}"


