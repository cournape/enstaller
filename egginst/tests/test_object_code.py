import os
import shutil
import unittest

import os.path as op

import mock

from machotools.dependency import dependencies
from machotools.rpath import list_rpaths

from egginst.main import EggInst
from egginst.object_code import find_lib, fix_object_code, get_object_type

from .common import DUMMY_EGG_WITH_INST_TARGETS, FILE_TO_RPATHS, \
    LEGACY_PLACEHOLD_FILE, NOLEGACY_RPATH_FILE, MACHO_ARCH_TO_FILE, \
    PYEXT_WITH_LEGACY_PLACEHOLD_DEPENDENCY, PYEXT_DEPENDENCY, \
    PYTHON_VERSION, mkdtemp

class TestObjectCode(unittest.TestCase):
    def test_get_object_type(self):
        self.assertEqual(get_object_type(MACHO_ARCH_TO_FILE["x86"]), "MachO-i386")
        self.assertEqual(get_object_type(MACHO_ARCH_TO_FILE["amd64"]), "MachO-x86_64")

        self.assertEqual(get_object_type("dummy_no_exist"), None)
        self.assertEqual(get_object_type(__file__), None)

    def test_fix_object_code_legacy_macho(self):
        """
        Test that we handle correctly our legacy egg with the /PLACHOLD * 20 hack.
        """
        with mkdtemp() as d:
            copy = op.join(d, "foo.dylib")
            shutil.copy(LEGACY_PLACEHOLD_FILE, copy)

            with mock.patch("egginst.object_code._targets", [d]):
                fix_object_code(copy)
                rpaths = list_rpaths(copy)

                self.assertEqual(rpaths[0], [d])

    def test_fix_object_code_wo_legacy_macho(self):
        """
        Test that we handle correctly egg *without* the /PLACHOLD (i.e. we
        don't touch them).
        """
        r_rpaths = FILE_TO_RPATHS[NOLEGACY_RPATH_FILE]
        with mkdtemp() as d:
            copy = op.join(d, "foo.dylib")
            shutil.copy(NOLEGACY_RPATH_FILE, copy)

            with mock.patch("egginst.object_code._targets", [d]):
                fix_object_code(copy)
                rpaths = list_rpaths(copy)[0]

                self.assertEqual(rpaths, r_rpaths)

    def test_fix_object_code_with_targets(self):
        """
        Test we handle the targets.dat hack correctly in fix_object_code.

        Some of our eggs use /PLACEHOLD in the LC_LOAD_DYLIB command (i.e.
        inside the dependency names). Those are rewritten by finding the
        dependency in the installed egg first.

        We're ensuring here that those are also rewritten correctly.
        """
        # targets.dat hack is handled in the function that expects an egg, but
        # we don't want to deal with an egg. Instead, we emulate the
        # targets.dat hack by patching object_code._targets with mock
        pyext_dependency_dir = op.join("lib", "foo-4.2")

        with mkdtemp() as d:
            installed_pyext_dependency = op.join(d, pyext_dependency_dir, op.basename(PYEXT_DEPENDENCY))
            installed_pyext_dependency_dir = op.dirname(installed_pyext_dependency)
            with mock.patch("egginst.object_code._targets", [d, installed_pyext_dependency_dir]):
                installed_pyext = op.join(d, op.basename(PYEXT_WITH_LEGACY_PLACEHOLD_DEPENDENCY))
                shutil.copy(PYEXT_WITH_LEGACY_PLACEHOLD_DEPENDENCY, installed_pyext)

                os.makedirs(installed_pyext_dependency_dir)
                shutil.copy(PYEXT_DEPENDENCY, installed_pyext_dependency_dir)

                fix_object_code(installed_pyext)
                deps = set(dependencies(installed_pyext)[0])

                self.assertTrue(installed_pyext_dependency in deps)

    def test_find_lib_with_targets(self):
        """
        Test we handle the targets.dat hack correctly in find_lib.
        """
        with mkdtemp() as d:
            with mock.patch("egginst.object_code._targets", []):
                egg_inst = EggInst(DUMMY_EGG_WITH_INST_TARGETS, d)
                egg_inst.install()

                path = "libfoo.dylib"
                self.assertEqual(find_lib(path), op.join(d, "lib", "foo-4.2", path))
