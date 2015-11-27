#!/usr/bin/env python

import unittest
import itertools
import os

from ngspyeasy import pipeline_tools
from ngspyeasy import sh_template
from ngspyeasy import pipeline_env


class TemplateVarsTests(unittest.TestCase):
    def test_vars(self):
        env = (pipeline_env.as_test_dict())
        print env
        for r, n in zip(pipeline_tools.tool_dirs(), itertools.count()):
            print "[%s]" % str(n), r
            tmpls = pipeline_tools.find(r)
            for t in tmpls:
                self.validate(t, env)

    def validate(self, t, env):
        tmpl = sh_template.load(os.path.join("tools", t.dir(), t.template()))
        tmpl.validate(**env)
