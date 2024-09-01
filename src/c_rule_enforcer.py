import re
from typing import Any, Generator
from dataclasses import dataclass

import tree_sitter_c as tsc
from tree_sitter import Language, Parser, Tree, Node


@dataclass
class Rules:
    require_includes: list[str] | None
    """
    allow_includes = None: All includes allowed
    allow_includes = []: No includes allowed (except required_includes)
    """
    allow_includes: list[str] | None
    require_functions: list[str] | None
    """
    disallow:
    - main
    - assignment (includes ++ and --)
    - reassignment (includes ++ and --)
    - loops
    - if_statements (includes loops)
    - helper_functions
    - printing
    - direct_recursion
    - arrays (excludes int *arr = {1, 2, 3})
    - nonnumeric_defines
    - function_pointers
    """
    disallow: list[str] | None
    disallow_symbols: list[str] | None
    limit_source_bytes: int | None
    # Must be at least size of `require_functions`
    limit_defined_functions: int | None

    @classmethod
    def from_dict(cls, d: dict[str, Any]):
        def list_or_none(value: Any):
            return list(value) if value is not None else None

        return cls(
            require_includes=list_or_none(d.get('require_includes', None)),
            allow_includes=list_or_none(d.get('allow_includes', None)),
            require_functions=list_or_none(d.get('require_functions', None)),
            disallow=list_or_none(d.get('disallow', None)),
            disallow_symbols=list_or_none(d.get('disallow_symbols', None)),
            limit_source_bytes=d.get('limit_source_bytes', None),
            limit_defined_functions=d.get('limit_defined_functions', None),
        )


ENFORCER_ERROR_TEMPLATE = """
Your submission was rejected because of the following:

{errors}

Please try again.
"""


def get_rule_violations_str(src: bytes, rules: Rules) -> str | None:
    if violations := sorted(get_unique_rule_violations(src, rules)):
        return ENFORCER_ERROR_TEMPLATE.format(
            errors="\n".join(f'* {violation}' for violation in violations))


def get_rule_violations(src: bytes, rules: Rules) -> Generator[str, None, None]:
    C_LANGUAGE = Language(tsc.language())
    parser = Parser(C_LANGUAGE)
    tree = parser.parse(src)

    if rules.disallow:
        yield from handle_disallow(src, tree, rules.disallow, rules.require_functions)

    if rules.disallow_symbols:
        yield from handle_disallow_symbols(tree, src, rules.disallow_symbols)

    # Must do handling for falsy 0
    if rules.limit_source_bytes is not None:
        yield from handle_limit_source_bytes(src, rules.limit_source_bytes)

    # Must do handling for falsy 0
    if rules.limit_defined_functions is not None:
        if rules.require_functions is not None:
            assert rules.limit_defined_functions >= len(
                rules.require_functions), \
                f'Setup error: `limit_defined_functions` ({rules.limit_defined_functions}) must be greater than or equal to `len(rules.require_functions)` ({len(rules.require_functions)})'

        yield from handle_limit_defined_functions(tree, rules.limit_defined_functions)

    if rules.require_includes:
        yield from handle_require_includes(tree, src, rules.require_includes)

    # None means allow all; [] means allow none
    if rules.allow_includes is not None:
        yield from handle_allow_includes(tree, src, rules.allow_includes, rules.require_includes or [])


def get_unique_rule_violations(src: bytes, rules: Rules) -> set[str]:
    return {*get_rule_violations(src, rules)}


def handle_disallow(src: bytes, tree: Tree, disallowed: list[str],
                    required_functions: list[str] | None) -> Generator[str, None, None]:
    if 'main' in disallowed:
        yield from handle_disallow_main(tree, src)

    if 'assignment' in disallowed:
        yield from handle_disallow_assignment(tree)

    if 'reassignment' in disallowed:
        yield from handle_disallow_reassignment(tree)

    if 'loops' in disallowed:
        yield from handle_disallow_loops(tree)

    if 'if_statements' in disallowed:
        yield from handle_disallow_if_statements(tree)

    if 'helper_functions' in disallowed:
        yield from handle_disallow_helper_functions(tree, src, required_functions)

    if 'printing' in disallowed:
        yield from handle_disallow_printing(tree, src)

    if 'direct_recursion' in disallowed:
        yield from handle_disallow_direct_recursion(tree, src)

    if 'arrays' in disallowed:
        yield from handle_disallow_arrays(tree)

    if 'nonnumeric_defines' in disallowed:
        yield from handle_disallow_nonnumeric_defines(tree, src)

    # TODO
    if 'function_pointers' in disallowed:
        ...


def handle_disallow_main(tree: Tree, src: bytes) -> Generator[str, None, None]:
    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        if node.type == 'function_declarator':
            for child in node.children:
                if child.type == 'identifier':
                    identifier = src[child.start_byte:child.end_byte]

                    # Sourced checked is unmangled version; main has no UUID suffix
                    if identifier == b'main':
                        yield 'Including a `main` function is disallowed.'
                        break
        else:
            for child in node.children:
                yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def handle_disallow_assignment(tree: Tree) -> Generator[str, None, None]:
    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        if node.type in {'init_declarator', 'assignment_expression', '++', '--'}:
            yield 'Assignment statements, incrementing, and decrementing are disallowed.'

        for child in node.children:
            yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def handle_disallow_reassignment(tree: Tree) -> Generator[str, None, None]:
    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        if node.type in {'assignment_expression', '++', '--'}:
            yield 'Reassignment, incrementing, and decrementing are disallowed.'

        for child in node.children:
            yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def handle_disallow_loops(tree: Tree) -> Generator[str, None, None]:
    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        if node.type in {'for_statement', 'while_statement', 'do_statement'}:
            yield 'Loops are disallowed.'

        for child in node.children:
            yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def handle_disallow_if_statements(tree: Tree) -> Generator[str, None, None]:
    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        if node.type in {'if_statement', 'for_statement', 'while_statement', 'do_statement'}:
            yield '`if` statements and loops are disallowed.'

        for child in node.children:
            yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def handle_disallow_helper_functions(tree: Tree,
                                     src: bytes,
                                     required_functions: list[str] | None) -> Generator[str, None, None]:
    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        if node.type == 'function_declarator':
            for child in node.children:
                if child.type == 'identifier':
                    identifier = src[child.start_byte:child.end_byte]

                    if required_functions is None or identifier.decode('utf8') not in required_functions:
                        yield 'Helper functions are disallowed.'
                        break
        else:
            for child in node.children:
                yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def handle_disallow_printing(tree: Tree, src: bytes) -> Generator[str, None, None]:
    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        if node.type == 'call_expression':
            for child in node.children:
                if child.type == 'identifier':
                    identifier = src[child.start_byte:child.end_byte]

                    if identifier in {
                            b'printf',
                            b'vprintf',
                            b'fprintf',
                            b'vfprintf',
                            b'fputc',
                            b'putc',
                    }:
                        yield 'Printing is disallowed.'
                        break
        else:
            for child in node.children:
                yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def handle_disallow_direct_recursion(tree: Tree, src: bytes) -> Generator[str, None, None]:
    def recurse_on_node(node: Node,
                        inside_function: bytes | None) -> Generator[str, None, None]:
        # `function_definition` node also contains body
        if node.type == 'function_definition':
            for child in node.children:
                if child.type == 'function_declarator':
                    for grandchild in child.children:
                        if grandchild.type == 'identifier':
                            inside_function = src[grandchild.start_byte:grandchild.end_byte]

        elif node.type == 'call_expression':
            for child in node.children:
                if child.type == 'identifier':
                    called_function = src[child.start_byte:child.end_byte]

                    if called_function == inside_function:
                        yield 'Direct recursion is not allowed.'

        for child in node.children:
            yield from recurse_on_node(child, inside_function)

    yield from recurse_on_node(tree.root_node, None)


def handle_disallow_symbols(tree: Tree, src: bytes,
                            disallowed_symbols: list[str]) -> Generator[str, None, None]:
    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        if node.type == 'identifier':
            symbol = src[node.start_byte:node.end_byte]

            if (s := symbol.decode('utf8')) in disallowed_symbols:
                yield f'`{s}` is disallowed.'

        for child in node.children:
            yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def handle_limit_source_bytes(src: bytes, limit: int):
    if len(src) > limit:
        yield f'Source code is too long; must be at most {limit} bytes.'


def handle_limit_defined_functions(tree: Tree, limit: int) -> Generator[str, None, None]:
    total = 0

    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        nonlocal total

        if node.type == 'function_definition':
            total += 1

            if total > limit:
                yield f'Too many defined functions; at most {limit} function{"" if limit == 1 else "s"} can be defined.'

        for child in node.children:
            yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def handle_disallow_arrays(tree: Tree) -> Generator[str, None, None]:
    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        if node.type == 'array_declarator':
            yield 'Arrays are disallowed.'

        for child in node.children:
            yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def handle_disallow_nonnumeric_defines(tree: Tree, src: bytes) -> Generator[str, None, None]:
    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        if node.type == 'preproc_function_def':
            yield '`define` preprocessor directives for nonnumeric values are disallowed.'

        elif node.type == 'preproc_arg':
            value = src[node.start_byte:node.end_byte]

            if not re.match(r'(\+|-)?\d+(\.\d*)?', value.decode('utf8')):
                yield '`define` preprocessor directives for nonnumeric values are disallowed.'

        for child in node.children:
            yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def handle_require_includes(tree: Tree, src: bytes,
                            required_includes: list[str]) -> Generator[str, None, None]:
    includes_left = set(required_includes)

    def recurse_on_node(node: Node):
        nonlocal includes_left

        if node.type == 'system_lib_string':
            identifier = src[node.start_byte:node.end_byte].replace(
                b"<", b"").replace(b">", b"")

            if (s := identifier.decode('utf8')) in includes_left:
                includes_left.remove(s)

        elif node.type == 'preproc_include':
            for child in node.children:
                if child.type == 'string_literal':
                    for grandchild in child.children:
                        if grandchild.type == 'string_content':
                            identifier = src[grandchild.start_byte:grandchild.end_byte]

                            if (s := identifier.decode('utf8')) in includes_left:
                                includes_left.remove(s)

        for child in node.children:
            recurse_on_node(child)

    recurse_on_node(tree.root_node)

    if includes_left:
        yield f'Must include: {", ".join(includes_left)}'


def handle_allow_includes(tree: Tree, src: bytes, allowed_includes: list[str],
                          required_includes: list[str]) -> Generator[str, None, None]:
    def recurse_on_node(node: Node) -> Generator[str, None, None]:
        if node.type == 'system_lib_string':
            identifier = src[node.start_byte:node.end_byte].replace(
                b"<", b"").replace(b">", b"")

            s = identifier.decode('utf8')
            if s not in allowed_includes and s not in required_includes:
                yield f'Including {s} is disallowed.'

        elif node.type == 'preproc_include':
            for child in node.children:
                if child.type == 'string_literal':
                    for grandchild in child.children:
                        if grandchild.type == 'string_content':
                            identifier = src[grandchild.start_byte:grandchild.end_byte]

                            s = identifier.decode('utf8')
                            if s not in allowed_includes and s not in required_includes:
                                yield f'Including {s} is disallowed.'

        for child in node.children:
            yield from recurse_on_node(child)

    yield from recurse_on_node(tree.root_node)


def main():
    with open('test.c', 'rb') as f:
        src = f.read()

    rules = Rules.from_dict({})

    if msg := get_rule_violations_str(src, rules):
        print(msg)
        # raise CompileError(msg)


def main_explore() -> Generator[str, None, None]:
    C_LANGUAGE = Language(tsc.language())
    parser = Parser(C_LANGUAGE)

    # with open('test.c', 'rb') as f:
    # src = f.read()

    src = b'''
#include <stdio.h>
#include "hello.h"
'''

    tree = parser.parse(src)

    def recurse_on_node(node: Node, level: int) -> Generator[str, None, None]:
        print(f'{"-" * (level * 2)}{node.type}')

        for child in node.children:
            yield from recurse_on_node(child, level + 1)

    yield from recurse_on_node(tree.root_node, 0)


if __name__ == '__main__':
    print(*main_explore())
    # main()
