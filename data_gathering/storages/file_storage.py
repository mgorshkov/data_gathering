import os

from storages.storage import Storage


class FileStorage(Storage):

    def __init__(self, file_name):
        self.file_name = file_name

    def exists(self):
        return os.path.exists(self.file_name)

    def read_data(self):
        if not self.exists():
            raise StopIteration

        with open(self.file_name, mode='r', encoding='utf-8') as f:
            for line in f:
                yield line.strip()

    def write_data(self, data):
        """
        :param data: string
        """
        with open(self.file_name, mode='w', encoding='utf-8') as f:
            if data.endswith('\n'):
                f.write(data)
            else:
                f.write(data + '\n')

    def append_data(self, data):
        """
        :param data: string
        """
        with open(self.file_name, mode='a', encoding='utf-8') as f:
            if data.endswith('\n'):
                f.write(data)
            else:
                f.write(data + '\n')
