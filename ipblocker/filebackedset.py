class FileBackedSet:
    def __init__(self, filename):
        self.filename = filename
        self.make_set()

    def make_set(self):
        self.mtime = os.stat(self.filename).st_mtime
        self.set = set(self.make_keys())

    def make_keys(self):
        return open(self.filename).read().split()

    def __contains__(self, key):
        if os.stat(self.filename).st_mtime != self.mtime:
            self.make_set()
        return key in self.set

