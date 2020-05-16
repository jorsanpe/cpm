class InstallService(object):
    def __init__(self, project_loader, plugin_installer, cpm_hub_connector):
        self.cpm_hub_connector = cpm_hub_connector
        self.project_loader = project_loader
        self.plugin_installer = plugin_installer

    def install(self, name, version):
        self.project_loader.load()
        print(f'installing {name}:{version}')
        plugin_download = self.cpm_hub_connector.download_plugin(name, version)
        return self.plugin_installer.install(plugin_download)

    def install_project_plugins(self):
        project = self.project_loader.load()
        for plugin_name, version in project.declared_plugins.items():
            self.install(plugin_name, version)


class PluginNotFound(RuntimeError):
    pass
