import tempfile


def temp_filename(dir=None, extension=None):

    if not extension.startswith("."):
        extension = "."+extension

    file = tempfile.NamedTemporaryFile(suffix=extension, dir=dir, delete=True)
    filename = file.name
    file.close()
    return filename


def temp_directory():

    return tempfile.mkdtemp()
