import unittest

from mock import MagicMock
from mock import call

from cpm.domain.install_service import InstallService
from cpm.domain.install_service import PluginNotFound
from cpm.domain.plugin import Plugin
from cpm.domain.project import Project
from cpm.domain.project_loader import NotAChromosProject
from cpm.infrastructure.cpm_hub_connector_v1 import AuthenticationFailure


class TestInstallService(unittest.TestCase):
    def test_install_service_creation(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        InstallService(project_loader, plugin_installer, cpm_hub_connector)

    def test_install_service_fails_when_project_loader_fails_to_load_project(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

        self.assertRaises(NotAChromosProject, service.install, 'cest', 'latest')

        project_loader.load.assert_called_once()

    def test_install_service_fails_when_authentication_fails(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        cpm_hub_connector.download_plugin.side_effect = AuthenticationFailure
        service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

        self.assertRaises(AuthenticationFailure, service.install, 'cest', 'latest')

        cpm_hub_connector.download_plugin.assert_called_once_with('cest', 'latest')

    def test_install_service_fails_when_plugin_is_not_found_in_cpm_hub(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        cpm_hub_connector.download_plugin.side_effect = PluginNotFound
        service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

        self.assertRaises(PluginNotFound, service.install, 'cest', 'latest')

        cpm_hub_connector.download_plugin.assert_called_once_with('cest', 'latest')

    def test_install_service_downloads_plugin_then_installs_it_and_updates_the_project(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        plugin_download = MagicMock()
        plugin_installer.install.return_value = Plugin('cest')
        project = Project('Project')
        project_loader.load.return_value = project
        cpm_hub_connector.download_plugin.return_value = plugin_download
        service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

        service.install('cest', 'latest')

        cpm_hub_connector.download_plugin.assert_called_once_with('cest', 'latest')
        plugin_installer.install.assert_called_once_with(plugin_download)

    def test_it_installs_given_plugin_version(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        plugin_download = MagicMock()
        plugin_installer.install.return_value = Plugin('cest')
        project = Project('Project')
        project_loader.load.return_value = project
        cpm_hub_connector.download_plugin.return_value = plugin_download
        service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

        service.install('cest', '1.0')

        cpm_hub_connector.download_plugin.assert_called_once_with('cest', '1.0')
        plugin_installer.install.assert_called_once_with(plugin_download)

    def test_it_installs_all_plugins_declared_in_project(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        plugin_download = MagicMock()
        project = Project('Project')
        project.declared_plugins = {
            'cest': '1.0',
            'fakeit': '1.0',
        }
        project_loader.load.return_value = project
        cpm_hub_connector.download_plugin.return_value = plugin_download
        service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

        service.install_project_plugins()

        cpm_hub_connector.download_plugin.assert_has_calls([
            call('cest', '1.0'),
            call('fakeit', '1.0'),
        ])
        plugin_installer.install.assert_has_calls([
            call(plugin_download),
            call(plugin_download)
        ])
