class Node(object):
    def __init__(self, name):
        self.children = []
        self.name = name

    def find(self, name):
        # Not a nested search
        for x in self.children:
            if x.name == name:
                return x

        return None

    def add(self, name, leaf=False):
        if self.find(name):
            raise Exception('Invalid') # FIXME

        if leaf:
            n = Leaf(name)
        else:
            n = Node(name)
        self.children.append(n)
        return n

    def repr(self):
        return 'Node(%s)' % name


class Leaf(object):
    def __init__(self, name):
        self.name = name

    def repr(self):
        return 'Leaf(%s)' % name

class FileTree(object):
    def __init__(self, files):
        """
        Files should be a list of lists. Each list contains a path with each
        item in the path as a new item.

        >>> [['a', 'e'], ['a', 'b', 'c', 'd']] (a/e, a/b/c/d)
        """
        self.root = self.build_tree(files)

    def build_tree(self, files):
        root = Node('Files')

        for x in files:
            last_node = root

            while len(x) > 1:
                y = x[0]
                n = last_node.find(y)
                if n:
                    last_node = n
                else:
                    n = last_node.add(y, leaf=False)
                    last_node = n
                x = x[1:]

            if len(x) == 1:
                last_node.add(x[0], leaf=True)

        return root
