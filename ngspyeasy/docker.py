#!/usr/bin/env python

###
# Copyright 2015, EMBL-EBI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

import os

USER = "pipeman"

HOME = "/home/" + USER

NGS_PROJECTS = HOME + "/ngs_projects"

NGS_RESOURCES = NGS_PROJECTS + "/ngseasy_resources"

DOCKER_OPTS = ""


def docker_options(ngs_projects_path, ngs_resources_path, pipeman=False):
    options = ["--rm", "-P", "-w", HOME, "-e", "HOME=" + HOME]
    if pipeman:
        options.extend(["-e", "USER=" + USER, "--user", USER])

    ngspyeasy_home = os.path.dirname(os.path.realpath(__file__))
    options.extend(["-v", ngs_projects_path + ":" + NGS_PROJECTS])
    options.extend(["-v", ngs_resources_path + ":" + NGS_RESOURCES])
    options.extend(["-v", ngspyeasy_home + ":/ngspyeasy:ro"])
    options.append(DOCKER_OPTS)
    return options


def wrap(name, image, cmd, projects_home):
    docker_run = ["docker", "run"] + docker_options(projects_home.root(), projects_home.resources_dir())
    docker_run.append("--name %s" % name)
    docker_run.append(image)
    docker_run.append(cmd)
    return " ".join(docker_run)


def wrap_lsf(name, image, cmd, projects_home, dependencies):
    lsf_dep_expression = ""
    if len(dependencies) > 0:
        lsf_dep_expression = "-w \"%s\"" % " && ".join(["ended(%s)" % x for x in dependencies])

    docker_image = "LSB_DOCKER_IMAGE=\"%s\"" % image
    docker_opts = "LSB_DOCKER_OPTIONS=\"%s\"" % " ".join(
        docker_options(projects_home.root(), projects_home.resources_dir()))
    outlog = projects_home.log_path(name + "_out.log")
    errorlog = projects_home.log_path(name + "_error.log")
    bsub_cmd = "bsub -q docker_queue -J %s %s -o %s -e %s %s" % (name, lsf_dep_expression, outlog, errorlog, cmd)
    return " ".join([docker_image, docker_opts, bsub_cmd])


class JobCommand(object):
    def __init__(self, executable, config_name, sample_id, **kwargs):
        self.executable = executable
        self.sample_id = sample_id
        self.config_name = config_name
        self.verbose = kwargs.get("verbose", False)
        self.task = kwargs.get("task", None)

    def add_task(self, task):
        return JobCommand(self.executable, self.config_name, self.sample_id, verbose=self.verbose, task=task)

    def as_string(self):
        cmd = ["python /ngspyeasy/%s" % self.executable, "-v" if self.verbose else "", "-c", self.config_name, "-d",
               NGS_PROJECTS, "-i", self.sample_id, "-u", str(os.getuid()), "-g", str(os.getgid())]

        if self.task:
            cmd += ["-t", self.task]
        return " ".join(cmd)
