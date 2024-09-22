import sys
from typing import Generator

import tree_sitter_c as tsc
from tree_sitter import Language, Parser, Node


def explore(path: str) -> Generator[str, None, None]:
    C_LANGUAGE = Language(tsc.language())
    parser = Parser(C_LANGUAGE)

    with open(path, 'rb') as f:
        src = f.read()

    tree = parser.parse(src)

    def recurse_on_node(node: Node, level: int) -> Generator[str, None, None]:
        print(f'{"-" * (level * 2)}{node.type}')

        for child in node.children:
            yield from recurse_on_node(child, level + 1)

    yield from recurse_on_node(tree.root_node, 0)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 explorer.py <path_to_c_file>')
        exit(-1)

    print(*explore(sys.argv[1]))
