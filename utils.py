import os


def create_file_if_not_exists(path):
    if not os.path.exists(path):
        with open(path, "w+") as file:
            file.write("")
