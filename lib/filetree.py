"""
File tree representation of torrent.

The classes in this file can be used to convert a list of
file paths in a torrent to a tree representation.
"""

class Leaf(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def get_path(self):
        return self.path

    def get_path_no_root(self):
        """
        Remove preceding /
        """
        return self.path[1:]

    def get_name(self):
        return self.name

    def repr(self):
        return 'Leaf(%s, path)' % (self.name, self.path)

class Node(Leaf):
    def __init__(self, name, path):
        Leaf.__init__(self, name, path)
        self.children = []

    def find(self, name):
        # Not a nested search
        for x in self.children:
            if x.name == name:
                return x

        return None

    def add(self, name, path, leaf=False):
        if self.find(name):
            raise Exception('Invalid') # FIXME

        if leaf:
            n = Leaf(name, path)
        else:
            n = Node(name, path)
        self.children.append(n)
        return n

    def repr(self):
        return 'Node(%s, %s)' % (self.name, self.path)

class FileTree(object):
    def __init__(self, files):
        """
        Files should be a list of lists. Each list contains a path with each
        item in the path as a new item.

        >>> [['a', 'e'], ['a', 'b', 'c', 'd']] (a/e, a/b/c/d)
        """
        self.root = self.build_tree(files)

    def build_tree(self, files):
        root = Node('Files', '/')

        for x in files:
            last_node = root
            path = ''

            # Traverse directories
            while len(x) > 1:
                y = x[0]
                n = last_node.find(y)
                if n:
                    last_node = n
                    path = n.get_path()
                else:
                    n = last_node.add(y, path, leaf=False)
                    path += '/' + y
                    last_node = n
                x = x[1:]

            # Add file
            if not len(path):
                path = '/'
            path += x[0]
            last_node.add(x[0], path, leaf=True)

        return root

