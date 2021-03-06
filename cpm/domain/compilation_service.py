class CompilationService(object):
    def __init__(self, project_loader, cmakelists_builder, project_commands):
        self.project_loader = project_loader
        self.cmakelists_builder = cmakelists_builder
        self.project_commands = project_commands

    def build(self, target_name='default'):
        project = self.project_loader.load('.', target_name)
        self.cmakelists_builder.build(project)
        self.project_commands.build(project)

    def update(self, target_name='default'):
        project = self.project_loader.load('.', target_name)
        self.cmakelists_builder.build(project)

    def clean(self):
        project = self.project_loader.load('.')
        self.project_commands.clean(project)



