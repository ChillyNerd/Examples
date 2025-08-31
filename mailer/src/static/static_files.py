import os


class StaticFile:
    def __init__(self, path):
        self.path = path

    def get_file(self):
        return os.path.join(os.getcwd(), self.path)

    def get_file_from_static(self):
        return os.path.join(os.getcwd(), "src/static/", f"{self.path}.png")


class Files:
    signature = StaticFile("src/static/signature.png")
