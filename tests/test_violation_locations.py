import pytest

from c_rule_enforcer import (
    RuleViolation,
    Rules,
    get_rule_violations,
    get_rule_violations_str,
    get_unique_rule_violations,
)


def test_repeated_messages_collect_sorted_unique_one_based_lines():
    src = b'void f(){\n__bad(); __bad();\n' + b'\n' * 7 + b'__bad();\n}\n'
    # Both the default dunder rule and explicit ban report the same identifiers.
    rules = Rules.from_dict({'disallow_symbols': ['__bad']})
    feedback = get_rule_violations_str(src, rules)
    assert feedback.count('* `__bad` is disallowed.') == 1
    assert '(lines 2, 10)' in feedback


def test_single_location_with_unicode_comment_and_crlf():
    src = '// é\r\nvoid f(){ banned(); }\r\n'.encode()
    feedback = get_rule_violations_str(src, Rules.from_dict({'disallow_symbols': ['banned']}))
    assert '* `banned` is disallowed. (line 2)' in feedback
    assert '(lines ' not in feedback


def test_recursion_reports_call_location():
    src = b'int f(){\n\nreturn f();\n}\n'
    feedback = get_rule_violations_str(src, Rules.from_dict({'disallow': ['direct_recursion']}))
    assert '* Direct recursion is not allowed. (line 3)' in feedback


def test_global_and_missing_requirement_messages_have_no_location():
    src = b'void f(){ banned(); }\n'
    rules = Rules.from_dict(
        {
            'require_functions': ['answer'],
            'require_includes': ['stdio.h'],
            'limit_source_bytes': 1,
            'limit_defined_functions': 1,
            'disallow_symbols': ['banned'],
        }
    )
    feedback = get_rule_violations_str(src, rules)
    bullets = [line for line in feedback.splitlines() if line.startswith('* ')]
    assert len(bullets) == 4
    assert bullets == sorted(bullets)
    for bullet in bullets:
        if '`banned`' in bullet:
            assert '(line 1)' in bullet
        else:
            assert '(line' not in bullet


def test_function_count_remains_a_source_wide_diagnostic():
    feedback = get_rule_violations_str(b'void f(){}\nvoid g(){}\n', Rules.from_dict({'limit_defined_functions': 1}))
    assert '* Too many defined functions; at most 1 function can be defined.' in feedback
    assert '(line' not in feedback


def test_string_helper_apis_remain_compatible():
    src = b'void f(){ banned(); }\n'
    rules = Rules.from_dict({'disallow_symbols': ['banned']})
    violations = list(get_rule_violations(src, rules))
    assert violations == ['`banned` is disallowed.']
    assert isinstance(violations[0], str)
    assert isinstance(violations[0], RuleViolation)
    assert violations[0].lineno == 1
    assert get_unique_rule_violations(src, rules) == {'`banned` is disallowed.'}


def test_no_violations_returns_none():
    assert get_rule_violations_str(b'void f(){}', Rules.from_dict({})) is None


@pytest.mark.parametrize(
    'code,config',
    [
        ('int main(){}', {'disallow': ['main']}),
        ('void f(){ int x = 1; }', {'disallow': ['assignment']}),
        ('void f(){ x++; }', {'disallow': ['reassignment']}),
        ('void f(){ while(1){} }', {'disallow': ['loops']}),
        ('void f(){ if(1){} }', {'disallow': ['if_statements']}),
        ('void helper(){}', {'disallow': ['helper_functions']}),
        ('void f(){ printf("hello"); }', {'disallow': ['printing']}),
        ('int arr[3];', {'disallow': ['arrays']}),
        ('#define NAME foo', {'disallow': ['nonnumeric_defines']}),
        ('#define NAME(x) x', {'disallow': ['nonnumeric_defines']}),
        ('void f(){ goto done; done: return; }', {'disallow': ['atypical_control_flow']}),
        ('void f(){ longjmp(env, 1); }', {'disallow': ['atypical_control_flow']}),
        ('void f(){ if(1) return; }', {'disallow': ['braceless_blocks']}),
        ('void f(){ if(1){} else return; }', {'disallow': ['braceless_blocks']}),
        ('void f(){ asm("nop"); }', {'disallow': ['asm']}),
        ('#include <stdio.h>', {'allow_includes': []}),
        ('#include "my.h"', {'allow_includes': []}),
    ],
)
def test_node_rule_families_report_locations(code, config):
    feedback = get_rule_violations_str(('\n' + code + '\n').encode(), Rules.from_dict(config))
    assert '(line 2)' in feedback
