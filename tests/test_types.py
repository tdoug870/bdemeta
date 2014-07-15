from collections import defaultdict
from unittest    import TestCase
import os

from bdemeta.types import Unit, Package, Group

def dict_resolver(resolutions):
    return lambda name: resolutions[name]

class TestUnit(TestCase):
    def test_equality(self):
        a1 = Unit(None, 'a', None, None)
        a2 = Unit(None, 'a', None, None)
        b1 = Unit(None, 'b', None, None)
        b2 = Unit(None, 'b', None, None)

        assert(a1 == a2)
        assert(not a1 != a2)
        assert(a1 != b1)
        assert(a1 != b2)

        assert(a2 != b1)
        assert(a2 != b2)
        assert(a2 == a1)
        assert(not a2 != a1)

        assert(b1 == b2)
        assert(not b1 != b2)
        assert(b1 != a1)
        assert(b1 != a2)

        assert(b2 != a1)
        assert(b2 != a2)
        assert(b2 == b1)
        assert(not b2 != b1)

    def test_hash(self):
        a1 = Unit(None, 'a', None, None)
        a2 = Unit(None, 'a', None, None)
        b1 = Unit(None, 'b', None, None)
        b2 = Unit(None, 'b', None, None)

        assert(hash(a1) == hash(a2))
        assert(hash(a1) != hash(b1))
        assert(hash(a1) != hash(b2))

        assert(hash(a2) != hash(b1))
        assert(hash(a2) != hash(b2))
        assert(hash(a2) == hash(a1))

        assert(hash(b1) == hash(b2))
        assert(hash(b1) != hash(a1))
        assert(hash(b1) != hash(a2))

        assert(hash(b2) != hash(a1))
        assert(hash(b2) != hash(a2))
        assert(hash(b2) == hash(b1))

    def test_name(self):
        u = Unit(None, 'a', None, None)
        assert(u.name() == 'a')

    def test_flags(self):
        u = Unit(None, None, None, { 'a': 5 })
        assert(u.flags('a') == 5)

    def test_dependencies(self):
        resolver = dict_resolver({ 'b': 5 })
        u = Unit(resolver, None, ('b'), None)
        dependencies = u.dependencies()
        assert(len(dependencies) == 1)
        assert(5 in dependencies)

    def test_components(self):
        u = Unit(None, None, None, { 'a': 5 })
        assert(u.components() == {})

    def test_result_type(self):
        u = Unit(None, None, None, { 'a': 5 })
        assert(u.result_type() == None)

class TestPackage(TestCase):
    def test_name(self):
        path = os.path.join('foo', 'bar')
        p = Package(None, path, None, None, None)
        assert(p.name() == 'bar')

    def test_path(self):
        path = os.path.join('foo', 'bar')
        p = Package(None, path, None, None, None)
        assert(p.path() == path)

    def test_components(self):
        path = os.path.join('foo', 'bar')
        p = Package(None, path, None, None, None)
        assert(p.components() == {})

    def test_result_type(self):
        path = os.path.join('foo', 'bar')
        p = Package(None, path, None, None, None)
        assert(p.result_type() == None)

    def test_user_flag(self):
        path = os.path.join('foo', 'bar')
        p = Package(None, path, None, None, { 'a': ['foo'] })
        assert(p.flags('a') == 'foo')

    def test_default_cflag(self):
        path = os.path.join('foo', 'bar')
        p = Package(None, path, None, None, defaultdict(list))
        assert(p.flags('c') == '-I{}'.format(path))

    def test_default_and_user_cflag(self):
        path = os.path.join('foo', 'bar')
        p = Package(None, path, None, None, { 'c': ['foo'] })
        # note that user flags come before the default flags
        assert(p.flags('c') == 'foo -I{}'.format(path))

    def test_normal_package_members(self):
        path    = os.path.join('foo', 'bar')
        members = ['a', 'b']
        p = Package(None, path, members, None, None)
        assert(p.members() == members)

    def test_special_package_members(self):
        path    = os.path.join('foo', 'b+ar')
        members = ['a.c', 'b.cpp', 'c.txt']
        p = Package(None, path, members, None, None)
        assert(p.members() == members[:2])

class TestGroup(TestCase):
    def test_name(self):
        path = os.path.join('foo', 'bar')
        g = Group(None, path, None, None, None)
        assert(g.name() == 'bar')

    def test_result_type(self):
        path = os.path.join('foo', 'bar')
        g = Group(None, path, None, None, None)
        assert(g.result_type() == 'library')

    def test_user_flags(self):
        g = Group(None, 'gr1', [], [], { 'a': ['5'] })
        assert(g.flags('a') == ['5'])

    def test_default_cflags(self):
        path = os.path.join('gr1', 'gr1pkg1')
        pkg1 = Package(None, path, [], [], defaultdict(list))

        resolver = dict_resolver({ 'gr1pkg1': pkg1 })

        path = os.path.join('gr1')
        g = Group(resolver,
                  path,
                  frozenset(['gr1pkg1']),
                  None,
                  defaultdict(list))
        assert(g.flags('c') == ['-Igr1/gr1pkg1'])

    def test_default_and_user_cflags(self):
        path = os.path.join('gr1', 'gr1pkg1')
        pkg1 = Package(None, path, [], [], defaultdict(list))

        resolver = dict_resolver({ 'gr1pkg1': pkg1 })

        path = os.path.join('gr1')
        g = Group(resolver,
                  path,
                  frozenset(['gr1pkg1']),
                  None,
                  { 'c': ['foo'] })
        # note that user flags come before the default flags
        assert(g.flags('c') == ['foo', '-Igr1/gr1pkg1'])

    def test_default_ldflags(self):
        path = os.path.join('gr1')
        g = Group(None, path, frozenset(), None, defaultdict(list))
        assert(g.flags('ld') == ['-Lout/libs', '-lgr1'])

    def test_default_and_user_ldflags(self):
        path = os.path.join('gr1', 'gr1pkg1')
        pkg1 = Package(None, path, [], [], defaultdict(list))

        resolver = dict_resolver({ 'gr1pkg1': pkg1 })

        path = os.path.join('gr1')
        g = Group(resolver,
                  path,
                  frozenset(['gr1pkg1']),
                  None,
                  { 'ld': ['foo'] })
        # note that user flags come before the default flags
        assert(g.flags('ld') == ['foo', '-Lout/libs', '-lgr1'])

    def test_normal_components(self):
        path = os.path.join('gr1', 'gr1pkg1')
        pkg1 = Package(None, path, ['gr1pkg1_c1'], [], defaultdict(list))

        resolver = dict_resolver({ 'gr1pkg1': pkg1 })

        path = os.path.join('gr1')
        g = Group(resolver,
                  path,
                  frozenset(['gr1pkg1']),
                  [],
                  defaultdict(list))
        assert(g.components() == {
            'gr1pkg1_c1': {
                'cflags':  ['-Igr1/gr1pkg1'],
                'ldflags': ['-Lout/libs', '-lgr1'],
                'source':  'gr1/gr1pkg1/gr1pkg1_c1.cpp',
                'object':  'gr1pkg1_c1.o',
                'driver':  'gr1/gr1pkg1/gr1pkg1_c1.t.cpp',
                'test':    'gr1pkg1_c1.t'
            },
        })

    def test_special_components(self):
        path    = os.path.join('gr1', 'gr1pkg+1')
        members = ['a.c', 'b.cpp', 'c.txt']
        pkg1    = Package(None, path, members, [], defaultdict(list))

        resolver = dict_resolver({ 'gr1pkg+1': pkg1 })

        path = os.path.join('gr1')
        g = Group(resolver,
                  path,
                  frozenset(['gr1pkg+1']),
                  [],
                  defaultdict(list))
        assert(g.components() == {
            'gr1_gr1pkg+1_a': {
                'cflags':  ['-Igr1/gr1pkg+1'],
                'source':  'gr1/gr1pkg+1/a.c',
                'object':  'gr1_gr1pkg+1_a.o',
            },
            'gr1_gr1pkg+1_b': {
                'cflags':  ['-Igr1/gr1pkg+1'],
                'source':  'gr1/gr1pkg+1/b.cpp',
                'object':  'gr1_gr1pkg+1_b.o',
            },
        })

