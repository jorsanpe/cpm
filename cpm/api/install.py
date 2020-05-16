import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.install_service import PluginNotFound, InstallService
from cpm.domain.plugin_installer import PluginInstaller
from cpm.domain.plugin_loader import PluginLoader
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import ProjectLoader
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.infrastructure.cpm_user_configuration import CpmUserConfiguration
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.http_client import HttpConnectionError
from cpm.infrastructure.yaml_handler import YamlHandler


def install_plugin(install_service, name, version='latest'):
    try:
        install_service.install(name, version)
    except NotAChromosProject:
        return Result(FAIL, 'error: not a Chromos project')
    except PluginNotFound:
        return Result(FAIL, f'error: plugin {name} not found in CPM Hub')
    except HttpConnectionError as error:
        return Result(FAIL, f'error: failed to connect to CPM Hub at {error}')

    return Result(OK, f'Installed plugin "{name}"')


def install_project_plugins(install_service):
    try:
        install_service.install_project_plugins()
    except NotAChromosProject:
        return Result(FAIL, 'error: not a Chromos project')
    except PluginNotFound as e:
        return Result(FAIL, f'error: plugin {e} not found in CPM Hub')
    except HttpConnectionError as error:
        return Result(FAIL, f'error: failed to connect to CPM Hub at {error}')

    return Result(OK, f'Installed plugins')


def execute(argv):
    install_plugin_arg_parser = argparse.ArgumentParser(prog='cpm install', description='Chromos Package Manager', add_help=False)
    install_plugin_arg_parser.add_argument('plugin_name', nargs='?')
    args = install_plugin_arg_parser.parse_args(argv)

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    project_loader = ProjectLoader(yaml_handler, filesystem)
    plugin_loader = PluginLoader(yaml_handler, filesystem)
    plugin_installer = PluginInstaller(filesystem, plugin_loader)
    user_configuration = CpmUserConfiguration(yaml_handler, filesystem)
    user_configuration.load()
    cpm_hub_connector = CpmHubConnectorV1(filesystem, repository_url=f'{user_configuration["cpm_hub_url"]}/plugins')
    service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

    if not args.plugin_name:
        result = install_project_plugins(service)
    else:
        result = install_plugin(service, args.plugin_name)

    return result
