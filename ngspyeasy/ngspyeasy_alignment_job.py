#!/usr/bin/env python
import argparse
import datetime
from signal import signal, SIGPIPE, SIG_DFL
import subprocess
import sys
from ngspyeasy import cmdargs

from shutils import script_from_template, run_command
import os
import sample_data
import projects_dir
import tsv_config
from logger import init_logger, get_logger

LOGGER_NAME = "alignment_job"


def main(argv):
    parser = argparse.ArgumentParser(description="Alignment Job")
    parser.add_argument("-c", "--config", dest="config", required=True, type=cmdargs.path_basename,
                        help="TSV configuration file name")
    parser.add_argument("-d", "--projects-dir", dest="projects_dir", required=True, type=cmdargs.existed_directory_path,
                        help="ngs_projects directory path")
    parser.add_argument("-i", "--sample_id", dest="sample_id", help="sample_id to run trimmomatic on")
    parser.add_argument("-t", "--task", dest="task", required=True,
                        help="stampy task: [bwa | stampy | picard_cleansam | picard_addorreplacereadgroups]")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="turn ON verbose mode")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1", help="print software version")

    args = parser.parse_args(argv)

    projects_home = projects_dir.ProjectsDir(args.projects_dir)
    log_file = projects_home.sample_log_file(args.config, args.sample_id)
    print "Opening log file: %s" % log_file

    logger = init_logger(log_file, args.verbose, LOGGER_NAME)
    logger.info("Starting...")
    logger.debug("Command line arguments: %s" % args)

    tsv_config_path = projects_home.config_path(args.config)
    logger.info("Reading TSV config: %s" % tsv_config_path)
    try:
        tsv_conf = tsv_config.parse(tsv_config_path)
    except (IOError, ValueError) as e:
        logger.error(e)
        sys.exit(1)

    try:
        ngspyeasy_alignment_job(tsv_conf, projects_home, args.sample_id, args.task)
    except Exception as ex:
        logger.error(ex)
        sys.exit(1)


def log_info(msg):
    get_logger(LOGGER_NAME).info(msg)


def log_debug(msg):
    get_logger(LOGGER_NAME).debug(msg)


def ngspyeasy_alignment_job(tsv_conf, projects_home, sample_id, task=None):
    rows2run = tsv_conf.all_rows()
    if sample_id is not None:
        rows2run = filter(lambda x: x.sample_id() == sample_id, rows2run)

    for row in rows2run:
        run_alignment(row, projects_home, task)


def run_alignment(row, projects_home, task):
    if task is None:
        task = row.aligner()

    log_info("Running alignmnent job (SAMPLE_ID='%s', ALIGNER='%s', TASK='%s', GENOMEBUILD='%s')" % (
        row.sample_id(), row.aligner(), task, row.genomebuild()))

    if row.aligner() == "no-align":
        log_info("[%s] Skipping alignment" % row.aligner())
        return

    if row.aligner() not in ["bwa", "novoalign", "stampy", "bowtie2", "snap"]:
        raise ValueError("Unknown aligner value: '%s'" % row.aligner())

    ngs_resources = projects_home.resources_dir()

    if row.genomebuild() == "b37":
        refdir = os.path.join(ngs_resources, "reference_genomes_b37")
        genome_index = os.path.join(refdir, "human_g1k_v37")
    elif row.genomebuild() == "hg19":
        refdir = os.path.join(ngs_resources, "reference_genomes_hg19")
        genome_index = os.path.join(refdir, "ucsc.hg19")
    elif row.genomebuild() == "hs37d5":
        refdir = os.path.join(ngs_resources, "reference_genomes_hs37d5")
        genome_index = os.path.join(refdir, "hs37d5")
    elif row.genomebuild() == "hs38DH":
        refdir = os.path.join(ngs_resources, "/reference_genomes_hs38DH")
        genome_index = os.path.join(refdir, "hs38DH")
    else:
        raise ValueError("No genome selected. Exiting. Choose one of [b37] or [hg19]")

    log_info("Genome build index: %s" % genome_index)
    log_info("Genome build dir: %s " % refdir)

    sample = sample_data.create(row, projects_home)

    if row.trim() == "no-trim":
        fastq = sample.fastq_files()
        log_info("TRIM set to '%s'. Using raw FastQ data: %s" % (row.trim(), fastq))
    elif row.trim in ["atrim", "btrim"]:
        fastq = sample.trimmomatic_paired_results()
        not_exist = [x for x in fastq if not os.path.isfile(x)]
        if len(not_exist) > 0:
            raise ValueError("Trimmed FastQC Data does not exist: %s" % not_exist)
        log_info("TRIM set to '%s'. Using trimmed FastQ data: %s" % (row.trim(), fastq))
    else:
        raise ValueError("Unknown TRIM value: '%s'" % row.trim())

    base_dir = os.path.dirname(__file__)
    template_path = os.path.join(base_dir, "resources", "alignment", row.aligner(), task + ".tmpl.sh")

    log_info("Using template file: %s" % template_path)

    script = script_from_template(template_path)

    log_info("Script template to run: %s" % script.source())

    bam_prefix = sample.bam_prefix()
    platform_unit = find_platform_unit(fastq[0])

    script.add_variables(
        NCPU=str(row.ncpu()),
        BAM_PREFIX=bam_prefix,
        PLATFORM_UNIT=platform_unit,
        NGS_PLATFORM=row.ngs_platform(),
        DNA_PREP_LIBRARY_ID=row.dna_prep_library_id(),
        RUNDATE=datetime.datetime.now().strftime("%d%m%y%H%M%S"),
        FQ1=fastq[0],
        FQ2=fastq[1],
        GENOMEINDEX=genome_index,
        DISCORDANT_SAM=sample.alignments_path(bam_prefix + ".discordant.sam"),
        DISCORDANT_BAM=sample.alignments_path(bam_prefix + ".discordant.bam"),
        SPLITREAD_SAM=sample.alignments_path(bam_prefix + ".splitread.sam"),
        SPLITREAD_BAM=sample.alignments_path(bam_prefix + ".splitread.bam"),
        UNMAPPED_FASTQ=sample.alignments_path(bam_prefix + ".unmapped.fastq"),
        DUPEMK_BAM=sample.alignments_path(bam_prefix + ".dupemk.bam"),
        DUPEMK_FLAGSTAT_REPORT=sample.reports_path(bam_prefix + ".dupemk.bam.flagstat"),
        DUPEMK_BED_REPORT=sample.reports_path(bam_prefix + ".dupemk.bed"),
        TMP_DIR=sample.tmp_dir(),
        ALIGNNMENTS_DIR=sample.alignments_dir()
    )

    if row.aligner() == "novoalign":
        script.add_variables(K_STATS=sample.alignments_path(bam_prefix + ".K.stats"))

    if row.aligner() == "stampy":
        tmp_bam = sample.alignments_path(bam_prefix + ".tmp.bam")
        script.add_variables(
            TMP_BAM=tmp_bam,
            TMP_BAM_BAI=sample.alignments_path(bam_prefix + ".tmp.bam.bai"),
            DUPEMARK_TMP_BAM=sample.alignments_path(bam_prefix + ".dupemk.tmp.bam"),
            DUPEMARK_TMP_BAM_BAI=sample.alignments_path(bam_prefix + ".dupemk.tmp.bam.bai"),
            DUPEMARK_CLEANSAM_BAM=sample.alignments_path(bam_prefix + ".dupemk.tmpcleansam.bam"),
            DUPEMARK_CLEANSAM_BAM_BAI=sample.alignments_path(bam_prefix + ".dupemk.tmpcleansam.bam.bai"),
            STAMPY_VERSION="stampy-1.0.27",
            PICARD_VERSION="picard-tools-1.128"
        )

        if task not in ["bwa", "stampy", "picard_cleansam", "picard_addorreplacereadgroups"]:
            raise ValueError("Unknown stampy task: '%s'" % task)

        if task == "stampy":
            if not os.path.isfile(tmp_bam):
                raise IOError("Tmp BAM file not found: %s" % tmp_bam)

    if row.aligner() == "bowtie2":
        script.add_variables(
            FAST="--end-to-end --sensitive",
            SLOW="--local --sensitive-local"
        )

    if row.aligner() == "snap":
        script.add_variables(REFDIR=refdir)

    log_debug("Script template variables:\n %s" % "\n".join(script.variable_assignments()))

    run_command(script.to_temporary_file(), get_logger(LOGGER_NAME))


def find_platform_unit(fastq_file):
    cmd = "zcat %s | head -1 | sed 's/:/\\t/' - | cut -f 1 | sed 's/@//g' - " % fastq_file
    log_debug("platform_info=[%s]" % cmd)
    out = subprocess.check_output(cmd, shell=True, preexec_fn=lambda: signal(SIGPIPE, SIG_DFL))
    return out.strip()


if __name__ == '__main__':
    main(sys.argv[1:])
