from os.path import basename

import sublime
import sublime_plugin

__all__ = [
    "AliasFolderCommand"
]


def project_folders(project):
    return (project or {}).get('folders', [])


def project_folder(project, path):
    for folder in project_folders(project):
        if folder['path'] == path:
            return folder
    return None


def is_project_folder(project, path):
    return bool(project_folder(project, path))


def display_name(folder):
    return folder.get('name') or basename(folder['path'])


class PathsInputHandler(sublime_plugin.ListInputHandler):
    __slots__ = ('folders')

    def __init__(self, folders):
        super().__init__()
        self.folders = folders

    def name(self):
        return "paths"

    def placeholder(self):
        return "Path"

    def list_items(self):
        return [[f"{display_name(folder)}\t{folder['path']}", folder]
                for folder in self.folders]

    def next_input(self, args):
        return AliasInputHandler(args['paths'])


class AliasInputHandler(sublime_plugin.TextInputHandler):
    __slots__ = ('alias', 'path')

    def __init__(self, folder):
        super().__init__()
        self.alias = display_name(folder)
        self.path = folder['path']

    def name(self):
        return "alias"

    def placeholder(self):
        return "Display Name"

    def initial_text(self):
        return self.alias

    def preview(self, new_alias):
        if not new_alias:
            new_alias = basename(self.path)

        if new_alias != self.alias:
            hint = f"Change display name from <u>{self.alias}</u> to <u>{new_alias}</u>"
        else:
            hint = f"Display name is <u>{self.alias}</u>"

        return sublime.Html(f"{hint}<br><br><i>{self.path}</i>")


class AliasFolderCommand(sublime_plugin.WindowCommand):

    def is_enabled(self, paths=None):
        project = self.window.project_data()
        if not project:
            return False
        if not isinstance(paths, list):
            return True
        return len(paths) == 1 and is_project_folder(project, paths[0])

    def is_visible(self, paths=None):
        return self.is_enabled(paths)

    def input(self, args):
        if not args.get('paths'):
            folders = project_folders(self.window.project_data())
            if folders:
                return PathsInputHandler(folders)
        elif 'alias' not in args:
            folder = project_folder(self.window.project_data(), args['paths'][0])
            if folder:
                return AliasInputHandler(folder)
        return None

    def input_description(self):
        return "Alias:"

    def run(self, alias, paths=[]):
        # The PathsInputHandler returns the folder object from the project
        # (e.g.: {'name': 'foo', 'path': '/mnt/c/path'})
        if isinstance(paths, dict):
            path = paths['path']
        else:
            path = paths[0]
        project = self.window.project_data()
        folder = project_folder(project, path)
        if folder:
            if alias in ('', basename(path)):
                folder.pop('name', None)
            else:
                folder['name'] = alias
            self.window.set_project_data(project)
