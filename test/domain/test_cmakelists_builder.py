import unittest

import io
from cpm.domain.cmake.cmakelists_builder import CMakeListsBuilder
from cpm.domain.project.project import Project, Target


def a_project(name):
    return TestProjectBuilder(name)


class TestCmakelistsBuilder(unittest.TestCase):
    def test_build_cmakelists_from_project(self):
        cmakelists_builder = CMakeListsBuilder()
        project = a_project('Project') \
            .with_target('default') \
            .with_include_directories('default') \
            .project

        cmakelists_content = cmakelists_builder.build_contents(project, 'default')

        assert 'cmake_minimum_required (VERSION 3.7)' in cmakelists_content
        assert 'project(Project)' in cmakelists_content
        assert 'add_executable(Project main.cpp)' in cmakelists_content
        assert 'add_executable(Project main.cpp)' in cmakelists_content
        # assert 'include_directories(cpm-hub)' in cmakelists_content


class TestProjectBuilder:
    def __init__(self, name):
        self.target_name = ''
        self.project = Project(name)

    def with_target(self, target_name):
        self.target_name = target_name
        target = Target(target_name)
        self.project.targets[target_name] = target
        return self

    def with_include_directories(self, directories):
        target = None
        return self