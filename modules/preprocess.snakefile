#!/usr/bin/env python
# vim: syntax=python tabstop=4 expandtab

#---------------------------------
# @author: Mahesh Vangala
# @email: vangalamaheshh@gmail.com
# @date: July, 15, 2013
#---------------------------------

from scripts.utils import _getCuffCounts

rule filter_cuff_matrix:
    input:
        rpkmFile = _getCuffCounts(config)[1],
        annotFile=config['metasheet'],
        force_run_upon_config_change = config['config_file']
    output:
        filtered_rpkm = "analysis/" + config["token"] + "/cufflinks/Cuff_Gene_Counts.filtered.csv"
    params:
        sample_names = " ".join(config["ordered_sample_list"]),
        min_num_samples_expressing_at_threshold=config['min_num_samples_expressing_at_threshold'],
        RPKM_threshold=config['RPKM_threshold'],
        filter_mirna=config['filter_mirna'],
        numgenes_plots=config['numgenes_plots'],
    message: "Generating Pre-processed Cuff RPKM matrix file"
    benchmark:
        "benchmarks/" + config["token"] + "/filter_cuff_matrix.txt"
    shell:
        "Rscript viper/modules/scripts/filter_cuff_matrix.R "
        "--rpkm_file {input.rpkmFile} "
        "--min_samples {params.min_num_samples_expressing_at_threshold} "
        "--RPKM_cutoff {params.RPKM_threshold} "
        "--filter_miRNA {params.filter_mirna} "
        "--numgenes {params.numgenes_plots} "
        "--out_file {output.filtered_rpkm} "
        "--sample_names {params.sample_names} "


