#!/usr/bin/env python
import getopt
import subprocess
import sys
import sample_data

import projects_dir
import tsv_config
from cmdline_options import check_cmdline_options
from logger import init_logger, log_error, log_set_current_step, log_info


def usage():
    print """
Usage:  ngspyeasy_alignment_job -c <config_file> -d <project_directory> -i <sample_id> -t <task>

Options:
        -c  STRING  configuration file
        -d  STRING  project directory
        -v  NULL    verbose
        -h  NULL    show this message
        -i  STRING sample id
        -t  STRING task name (e.g. for stampy alignment tasks are: ['stampy_bwa', 'stampy_stampy', 'stampy_picard1', 'stampy_picard2'])
"""


def exit_with_error(msg):
    print >> sys.stderr, "ERROR:" + msg
    sys.exit(1)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hvc:d:i:p:", ["help"])
        if len(opts) == 0:
            usage()
            sys.exit(1)

    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    tsv_config_file = None
    ngs_projects_dir = None
    verbose = False
    sample_id = None
    task = None
    for opt, val in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt == "-c":
            tsv_config_file = val
        elif opt == "-d":
            ngs_projects_dir = val
        elif opt == "-v":
            verbose = True
        elif opt == "-i":
            sample_id = val
        elif opt == "-t":
            task = val
        else:
            assert False, "unhandled option"

    log_info("Command line arguments: (-c, '%s') (-d, '%s') (-i, '%s') (-t, '%s') (-v, '%s')" % (
    tsv_config_file, ngs_projects_dir, sample_id, task, str(verbose)))

    (tsv_name, projects_home, errmsg) = check_cmdline_options(tsv_config_file, ngs_projects_dir)
    if errmsg:
        exit_with_error(errmsg)

    init_logger(projects_dir.sample_log_file(projects_home, tsv_name, sample_id), verbose)
    log_set_current_step("ngspyeasy_fastqc_job")

    tsv_conf = tsv_config.parse(projects_dir.config_full_path(projects_home, tsv_name))
    if tsv_conf is None:
        exit_with_error("Invalid TSV config. See logs for details...")

    try:
        ngspyeasy_alignment_job(tsv_conf, projects_home, sample_id, task)
    except Exception as ex:
        log_error(ex)
        sys.exit(1)


def ngspyeasy_alignment_job(tsv_conf, projects_home, sample_id, task=None):
    rows2run = tsv_conf.all_rows()
    if sample_id is not None:
        rows2run = filter(lambda x: x.sample_id() == sample_id, rows2run)

    for row in rows2run:
        run_alignment(row, projects_home, task)


def run_alignment(row, projects_home, task):
    log_info("Running alignmnent job (SAMPLE_ID='%s', ALIGNMENT='%s', GENOMEBUILD='%s')" % (
        row.sample_id(), row.alignment(), row.genomebuild()))

    sample = sample_data.create(row, projects_home)

    platform_unit = subprocess.check_output(
        "zcat %s | head -1 | sed 's/:/\t/' - | cut -f 1 | sed 's/@//g' - " % sample.fastq_files()[0])

    log_info("platform_unit='%s'" % platform_unit)
