from c_rule_enforcer import Rules, get_unique_rule_violations


def test_disallow_main():
    rules = Rules.from_dict({'disallow': ['main']})

    violating_cases = [
        b'''
int main() {
}
''',
    ]

    nonviolating_cases = [
        b'''
int hello() {
    return 32;
}
''',
        b'''
int main_MANGLED() {
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_assignment():
    rules = Rules.from_dict({'disallow': ['assignment']})

    violating_cases = [
        b'''
void f(int a) {
    a++;
}
''',
        b'''
void f(int a) {
    a--;
}
''',
        b'''
void f(int a) {
    a *= 2;
}
''',
        b'''
void f() {
    for (int i = 0; i < 10; i++) {
    }
}
''',
        b'''
void f() {
    if (1) {
        int a = 1;
    }
}
''',
        b'''
void f() {
    int a = 1;
}
''',
        b'''
void f(int a) {
    a = 1;
}
''',
        b'''
int x = 1;
''',
    ]

    nonviolating_cases = [
        b'''
void f(int a) {
    return a;
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_reassignment():
    rules = Rules.from_dict({'disallow': ['reassignment']})

    violating_cases = [
        b'''
void f(int a) {
    a++;
}
''',
        b'''
void f(int a) {
    a--;
}
''',
        b'''
void f(int a) {
    a *= 2;
}
''',
        b'''
void f() {
    for (int i = 0; i < 10; i++) {
    }
}
''',
        b'''
void f(int a) {
    if (1) {
        a = 1;
    }
}
''',
        b'''
void f(int a) {
    a = 1;
}
''',
        b'''
void f() {
    int a = 1;
    a = 2;
}
''',
        b'''
int x = 1;
x = 2;
''',
    ]

    nonviolating_cases = [
        b'''
void f() {
    for (int i = 0; i < 10; ) {
    }
}
''',
        b'''
void f() {
    if (1) {
        int a = 1;
    }
}
''',
        b'''
void f() {
    int a = 1;
}
''',
        b'''
void f(int a) {
    return a;
}
''',
        b'''
int x = 1;
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_loops():
    rules = Rules.from_dict({'disallow': ['loops']})

    violating_cases = [
        b'''
void f(int a) {
    while (1) {
    }
}
''',
        b'''
void f() {
    for (int i = 0; i < 10; i++) {
    }
}
''',
        b'''
    do {
    } while (1);
''',
        b'''
void f() {
    if (1) {
        for (int i = 0; i < 10; i++) {
        }
    }
}
''',
        b'''
void f() {
    if (0) {
    } else {
        for (int i = 0; i < 10; i++) {
        }
    }
}
''',
    ]

    nonviolating_cases = [
        b'''
void f() {
    if (1) {
    }
}
''',
        b'''
void f() {
    if (1) {
    } else {
    }
}
''',
        b'''
void f() {
    {
        if (1) {
        } else {
        }
    }
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_if_statements():
    rules = Rules.from_dict({'disallow': ['if_statements']})

    violating_cases = [
        b'''
void f(int a) {
    while (1) {
    }
}
''',
        b'''
void f() {
    for (int i = 0; i < 10; i++) {
    }
}
''',
        b'''
    do {
    } while (1);
''',
        b'''
void f() {
    if (1) {
        for (int i = 0; i < 10; i++) {
        }
    }
}
''',
        b'''
void f() {
    if (0) {
    } else {
        for (int i = 0; i < 10; i++) {
        }
    }
}
''',
        b'''
void f() {
    if (1) {
    }
}
''',
        b'''
void f() {
    if (1) {
    } else {
    }
}
''',
        b'''
void f() {
    {
        if (1) {
        } else {
        }
    }
}
''',
    ]

    nonviolating_cases: list[bytes] = []

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_helper_functions():
    rules = Rules.from_dict({'disallow': ['loops']})

    violating_cases = [
        b'''
void f(int a) {
    while (1) {
    }
}
''',
        b'''
void f() {
    for (int i = 0; i < 10; i++) {
    }
}
''',
        b'''
    do {
    } while (1);
''',
        b'''
void f() {
    if (1) {
        for (int i = 0; i < 10; i++) {
        }
    }
}
''',
        b'''
void f() {
    if (0) {
    } else {
        for (int i = 0; i < 10; i++) {
        }
    }
}
''',
    ]

    nonviolating_cases = [
        b'''
void f() {
    if (1) {
    }
}
''',
        b'''
void f() {
    if (1) {
    } else {
    }
}
''',
        b'''
void f() {
    {
        if (1) {
        } else {
        }
    }
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_valid_disallow_helper_functions():
    rules = Rules.from_dict({
        'require_functions': ['f', 'g'],
        'disallow': ['helper_functions'],
    })

    violating_cases = [

        b'''
void f() {
}

void g() {
}

void h() {
}
''',
    ]

    nonviolating_cases = [
        b'''
void f() {
}

void g() {
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_invalid_disallow_helper_functions():
    rules = Rules.from_dict({'disallow': ['helper_functions']})

    violating_cases = [
        b'''
void f() {
}

void g() {
}

void h() {
}
''',
        b'''
void f() {
}

void g() {
}
''',
    ]

    nonviolating_cases: list[bytes] = []

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_printing():
    rules = Rules.from_dict({'disallow': ['printing']})

    violating_cases = [
        b'''
void f1() {
    printf("1");
}
''',
        b'''
void f2(int dummy, ...) {
    va_list args;
    va_start(args, dummy);
    vprintf("2", args);
    va_end(args);
}
''',
        b'''
void f3() {
    fprintf(stdout, "3");
}
''',
        b'''
void f4(int dummy, ...) {
    va_list args;
    va_start(args, dummy);
    vfprintf(stdout, "%d", args);
    va_end(args);
}
''',
        b'''
void f5() {
    fputc('5', stdout);
}
''',
        b'''
void f6() {
    putc('6', stdout);
}
''',
    ]

    nonviolating_cases: list[bytes] = []

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_direct_recursion():
    rules = Rules.from_dict({'disallow': ['direct_recursion']})

    violating_cases = [
        b'''
void f() {
    f();
}
''',
        b'''
void f() {
    if (1) {
        f();
    }
}
''',
        b'''
void f() {
    if (1) {
        {
            f();
        }
    }
}
''',
    ]

    nonviolating_cases = [
        b'''
void f() {
    g();
}

void g() {
    f();
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_symbols():
    rules = Rules.from_dict({'disallow_symbols': ['malloc']})

    violating_cases = [
        b'''
void f() {
    int *p = malloc(sizeof(int));
}
''',
        b'''
void f() {
    int malloc = 1;
}
''',
        b'''
void malloc() {
}
''',
        b'''
#define malloc 1
''',
        b'''
int malloc = 1;
''',
        b'''
void f() {
    int x = 1 + malloc + 1;
}
''',
        b'''
void f() {
    exit(malloc);
}
''',
    ]

    nonviolating_cases: list[bytes] = []

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_limit_source_bytes():
    rules = Rules.from_dict({'limit_source_bytes': 5})

    violating_cases = [
        b'123456',
        b'''
void f() {
}
''',
    ]

    nonviolating_cases = [
        b'1234',
        b'12345',
        b'',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_limit_defined_functions():
    rules = Rules.from_dict({'limit_defined_functions': 2})

    violating_cases = [
        b'''
void f() {
}

void g() {
}

void h() {
}
''',
    ]

    nonviolating_cases = [
        b'''
void f() {
}
''',
        b'''
void f() {
}

void g() {
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_arrays():
    rules = Rules.from_dict({'disallow': ['arrays']})

    violating_cases = [
        b'''
struct st {
    int x[];
};
''',
        b'''
void f(int arr[]) {
}
''',
        b'''
void f() {
    int x[] = {1, 2, 3};
}
''',
        b'''
void f() {
    int x[5] = {};
}
''',
    ]

    nonviolating_cases = [
        b'''
struct st {
    int f
};

void f() {
    struct st s = {f: 1};
}
''',
        b'''
void f() {
    int n = 1;
    int *p = &n;
}
''',
        b'''
void f() {
    int *z = {1, 2};
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_nonnumeric_defines():
    rules = Rules.from_dict({'disallow': ['nonnumeric_defines']})

    violating_cases = [
        b'''
#define FE(i,L,R) for (int i = L; i <= R; i++)
''',
        b'''
#define LINR(i,l,r) (l<=i&&i<=r)
''',
        b'''
#define ull unsigned long long
''',
    ]

    nonviolating_cases = [
        b'''
#define N 10000
''',
        b'''
#define PI 3.1415926535897932384626
''',
        b'''
#define K -123
''',
        b'''
#define K -0.1
''',
        b'''
#define K +0.1
''',
        b'''
#define K +0
''',
        b'''
#define K -0
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_require_includes():
    rules = Rules.from_dict({'require_includes': ['abminusc.h', 'stdio.h']})

    violating_cases = [
        b'''
int main() {
}
''',
        b'''
#include <abminusc.h>
''',
        b'''
#include "abminusc.h"
''',
        b'''
#include <stdio.h>
''',
        b'''
#include "stdio.h"
''',
    ]

    nonviolating_cases = [
        b'''
#include <abminusc.h>
#include <stdio.h>
''',
        b'''
#include "abminusc.h"
#include <stdio.h>
''',
        b'''
#include <abminusc.h>
#include "stdio.h"
''',
        b'''
#include "abminusc.h"
#include "stdio.h"
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_allow_includes():
    rules = Rules.from_dict({'allow_includes': ['abminusc.h', 'stdio.h']})

    violating_cases = [
        b'''
#include <abminusc.h>
#include <stdio.h>
#include <stdlib.h>
''',
        b'''
#include "abminusc.h"
#include <stdio.h>
#include <stdlib.h>
''',
        b'''
#include <abminusc.h>
#include "stdio.h"
#include <stdlib.h>
''',
        b'''
#include "abminusc.h"
#include "stdio.h"
#include <stdlib.h>
''',
        b'''
#include <stdlib.h>

int main() {
}
''',
        b'''
#include <stdlib.h>
''',
        b'''
#include "stdlib.h"
''',
    ]

    nonviolating_cases = [
        b'''
#include <abminusc.h>
#include <stdio.h>
''',
        b'''
#include "abminusc.h"
#include <stdio.h>
''',
        b'''
#include <abminusc.h>
#include "stdio.h"
''',
        b'''
#include "abminusc.h"
#include "stdio.h"
''',
        b'''
int main() {
}
''',
        b'''
#include <abminusc.h>
''',
        b'''
#include "abminusc.h"
''',
        b'''
#include <stdio.h>
''',
        b'''
#include "stdio.h"
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_empty_allow_includes():
    rules = Rules.from_dict({'allow_includes': []})

    violating_cases = [
        b'''
#include <abminusc.h>
#include <stdio.h>
#include <stdlib.h>
''',
        b'''
#include "abminusc.h"
#include <stdio.h>
#include <stdlib.h>
''',
        b'''
#include <abminusc.h>
#include "stdio.h"
#include <stdlib.h>
''',
        b'''
#include "abminusc.h"
#include "stdio.h"
#include <stdlib.h>
''',
        b'''
#include <stdlib.h>

int main() {
}
''',
        b'''
#include <stdlib.h>
''',
        b'''
#include "stdlib.h"
''',
        b'''
#include <abminusc.h>
#include <stdio.h>
''',
        b'''
#include "abminusc.h"
#include <stdio.h>
''',
        b'''
#include <abminusc.h>
#include "stdio.h"
''',
        b'''
#include "abminusc.h"
#include "stdio.h"
''',
        b'''
#include <abminusc.h>
''',
        b'''
#include "abminusc.h"
''',
        b'''
#include <stdio.h>
''',
        b'''
#include "stdio.h"
''',
    ]

    nonviolating_cases = [
        b'''
int main() {
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_empty_allow_includes_with_required():
    rules = Rules.from_dict({
        'require_includes': ["abminusc.h"],
        'allow_includes': [],
    })

    violating_cases = [
        b'''
#include <abminusc.h>
#include <stdio.h>
#include <stdlib.h>
''',
        b'''
#include "abminusc.h"
#include <stdio.h>
#include <stdlib.h>
''',
        b'''
#include <abminusc.h>
#include "stdio.h"
#include <stdlib.h>
''',
        b'''
#include "abminusc.h"
#include "stdio.h"
#include <stdlib.h>
''',
        b'''
#include <stdlib.h>

int main() {
}
''',
        b'''
#include <stdlib.h>
''',
        b'''
#include "stdlib.h"
''',
        b'''
#include <abminusc.h>
#include <stdio.h>
''',
        b'''
#include "abminusc.h"
#include <stdio.h>
''',
        b'''
#include <abminusc.h>
#include "stdio.h"
''',
        b'''
#include "abminusc.h"
#include "stdio.h"
''',
        b'''
#include <stdio.h>
''',
        b'''
#include "stdio.h"
''',
        b'''
int main() {
}
''',
    ]

    nonviolating_cases = [
        b'''
#include <abminusc.h>
''',
        b'''
#include "abminusc.h"
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_limit_defined_functions_with_required():
    rules = Rules.from_dict({
        'require_functions': ['f'],
        'limit_defined_functions': 0,
    })

    src = b'''
void f() {
}
'''

    try:
        get_unique_rule_violations(src, rules)
    except AssertionError:
        pass
    else:
        assert False, f'Must raise AssertionError if `limit_defined_functions` and `require_functions` are inconsistent: {rules}'


def test_disallow_atypical_control_flow_goto():
    rules = Rules.from_dict({'disallow': ['atypical_control_flow']})

    violating_cases = [
        b'''
int main() {
my_label:
  goto my_label;
}
''',
        b'''
int main() {
  goto my_label;
}
''',
    ]

    nonviolating_cases = [
        b'''
int main() {
  int goto = 1;
}
''',
        b'''
void goto() {
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_atypical_control_flow_longjmp():
    rules = Rules.from_dict({'disallow': ['atypical_control_flow']})

    violating_cases = [
        b'''
void f() {
    longjmp(j, 1);
}
''',
        b'''
#include <stdio.h>
#include <setjmp.h>

jmp_buf j;

void my_goto() {
    printf("my_goto\n");
    longjmp(j, 1);  // Must not return 0
}

int main() {
    int i = 0;

    if (!setjmp(j)) {
        printf("setjmp 0 branch\n");
        my_goto();
    } else {
        printf("setjmp 1 branch: %d\n", i);
        i++;

        if (i < 10) {
            my_goto();
        }
    }
}
''',
    ]

    nonviolating_cases = [
        b'''
int main() {
  int longjmp = 1;
}
''',
        b'''
void longjmp() {
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_braceless_blocks_if_else():
    rules = Rules.from_dict({'disallow': ['braceless_blocks']})

    violating_cases = [
        b'''
void f() {
    if (1) printf("test\n");
}
''',
        b'''
void f() {
    if (1)
        printf("test\n");
}
''',
        b'''
void f() {
    if (1) {
        printf("test\n");
    } else
        printf("test\n");
}
''',
        b'''
void f() {
    if (1) {
        printf("test\n");
        if (1) printf("test\n");
    } else {
        printf("test\n");
    }
}
''',
        b'''
void f() {
    if (1) {
        printf("test\n");
    } else {
        printf("test\n");
        if (1) printf("test\n");
    }
}
''',
        b'''
void f() {
    if (1) {
        printf("test\n");
    } else {
        printf("test\n");
        if (1) {
            if (1) printf("test\n");
        }
    }
}
''',
        b'''
void f() {
    if (1) {
        printf("test\n");
    } else if (0) {
        printf("test\n");
    } else if (0)
        printf("test\n");
    else {
        printf("test\n");
    }
}
''',
        b'''
void f() {
    if (1) {
        printf("test\n");
    } else if (0)
        printf("test\n");
    else {
        printf("test\n");
    }
}
''',
    ]

    nonviolating_cases = [
        b'''
void f() {
    if (1) {
        printf("test\n");
    }
}
''',
        b'''
void f() {
    if (1) {
        printf("test\n");
    } else {
        printf("test\n");
    }
}
''',
        b'''
void f() {
    if (1) {
    }
}
''',
        b'''
void f() {
    if (1) {
    } else {
    }
}
''',
        b'''
void f() {
    if (1) {
        printf("test\n");
    } else if (0) {
        printf("test\n");
    } else {
        printf("test\n");
    }
}
''',
        b'''
void f() {
    if (1) {
        printf("test\n");
    } else if (0) {
        printf("test\n");
    } else if (0) {
        printf("test\n");
    } else {
        printf("test\n");
    }
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_braceless_blocks_while():
    rules = Rules.from_dict({'disallow': ['braceless_blocks']})

    violating_cases = [
        b'''
void f() {
    while (1)
        printf("\n");
}
''',
        b'''
void f() {
    if (1) {
        while (1)
            printf("\n");
    }
}
''',
    ]

    nonviolating_cases = [
        b'''
void f() {
    while (1) {
        printf("\n");
    }
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_braceless_blocks_do_while():
    rules = Rules.from_dict({'disallow': ['braceless_blocks']})

    violating_cases = [
        b'''
void f() {
    do
        printf("\n");
    while (1);
}
''',
        b'''
void f() {
    if (1) {
        do
            printf("\n");
        while (1);
    }
}
''',
    ]

    nonviolating_cases = [
        b'''
void f() {
    do {
        printf("\n");
    } while (1);
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_braceless_blocks_for():
    rules = Rules.from_dict({'disallow': ['braceless_blocks']})

    violating_cases = [
        b'''
void f() {
    for (int i = 0; i < 10; i++)
        printf("\n");
}
''',
        b'''
void f() {
    if (1) {
        for (int i = 0; i < 10; i++)
            printf("\n");
    }
}
''',
    ]

    nonviolating_cases = [
        b'''
void f() {
    for (int i = 0; i < 10; i++) {
        printf("\n");
    }
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_require_functions_single():
    rules = Rules.from_dict({'require_functions': ['g']})

    violating_cases = [
        b'''
int main() {
}
''',
    ]

    nonviolating_cases = [
        b'''
int g() {
    return 1;
}
''',
        b'''
int g() {
    return 1;
}

int main() {
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_require_functions_multiple():
    rules = Rules.from_dict({'require_functions': ['g', 'h']})

    violating_cases = [
        b'''
int main() {
}
''',
        b'''
int g() {
    return 1;
}

int main() {
}
''',
        b'''
int h() {
    return 1;
}

int main() {
}
''',
    ]

    nonviolating_cases = [
        b'''
int g() {
    return 1;
}

int h() {
    return 1;
}
''',
        b'''
int g() {
    return 1;
}

int h() {
    return 1;
}

int main() {
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)


def test_disallow_asm():
    rules = Rules.from_dict({'disallow': ['asm']})

    violating_cases = [
        b'''
int main() {
    asm ("syscall");
    __asm__ ("syscall");
}
''',
        b'''
int main() {
    asm ("syscall");
}
''',
        b'''
int main() {
    __asm__ ("syscall");
}
''',
    ]

    nonviolating_cases = [
        b'''
int asm() {
    return 1;
}
''',
    ]

    for src in violating_cases:
        assert get_unique_rule_violations(src, rules)

    for src in nonviolating_cases:
        assert not get_unique_rule_violations(src, rules)
