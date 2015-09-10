#!/usr/bin/env python

import sys
import getopt
import utils
from project_structure import projects_log_dir, projects_conf_relpath, init_project
import logger
import tsv_config


def usage():
    print """
Usage:  ngspyeasy -c <config_file> -d <project_directory>

Options:
        -c  STRING  configuration file
        -d  STRING  project directory
        -v  NULL    verbose
        -h  NULL    show this message
"""

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hc:d:", ["help"])
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
        else:
            assert False, "unhandled option"

    (tsv_name, projects_home, errmsg) = utils.check_cmdline_options(tsv_config_file, ngs_projects_dir)
    if errmsg:
        utils.exit_with_error(errmsg)

    log = logger.create(projects_log_dir(projects_home), tsv_name, verbose)

    tsv_conf = tsv_config.parse(projects_conf_relpath(projects_home, tsv_name), log)
    if tsv_conf is None:
        utils.exit_with_error("Can't parse TSV config. see logs for details")

    ngspyeasy(tsv_conf, projects_home, log)


def ngspyeasy(tsv_conf, projects_home, log):
    init_project(tsv_conf, projects_home, log)
    #ngspyeasy_fastqc.ngspyeasy_fastqc(tsv_conf, projects_home, log)
    # ngspyeasy_trimmomatic.run_all(tsv_config, ngs_projects_dir)
    # ngspyeasy_alignment.run_all(tsv_config, ngs_projects_dir)
    # ngspyeasy_realign.run_all(tsv_config, ngs_projects_dir)
    # ngspyeasy_bsqr.run_all(tsv_config, ngs_projects_dir)
    # ngspyeasy_variant_calling.run_all(tsv_config, ngs_projects_dir)


if __name__ == '__main__':
    main(sys.argv[1:])
