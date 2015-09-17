#!/usr/bin/env python

USER = "pipeman"

HOME = "/home/" + USER

NGS_PROJECTS = HOME + "/ngs_projects"

NGS_RESOURCES = NGS_PROJECTS + "/ngseasy_resources"

DOCKER_OPTS = "-t"


def docker_cmd(name, image, cmd, projects_home, resources_home, pipeman=True):
    docker_run = ["docker", "run", "-P", "-w", HOME, "-e", "HOME=" + HOME]
    if pipeman:
        docker_run.extend(["-e", "USER=" + USER, "--user", USER])

    docker_run.extend(["--name", name])
    docker_run.extend(["-v", projects_home + ":" + NGS_PROJECTS])
    docker_run.extend(["-v", resources_home + ":" + NGS_RESOURCES])
    docker_run.append(DOCKER_OPTS)
    docker_run.append(image)
    docker_run.append(cmd)
    return " ".join(docker_run)
