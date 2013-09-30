import contextlib
import os
import shutil
import tempfile

import os.path as op

SUPPORT_SYMLINK = hasattr(os, "symlink")

DYLIB_DIRECTORY = op.join(op.dirname(__file__), "data")

LEGACY_PLACEHOLD_FILE = op.join(DYLIB_DIRECTORY, "foo_legacy_placehold.dylib")
NOLEGACY_RPATH_FILE = op.join(DYLIB_DIRECTORY, "foo_rpath.dylib")

FILE_TO_RPATHS = {
    NOLEGACY_RPATH_FILE: ["@loader_path/../lib"],
    LEGACY_PLACEHOLD_FILE: ["/PLACEHOLD" * 20],
}

MACHO_ARCH_TO_FILE = {
    "x86": op.join(DYLIB_DIRECTORY, "foo_x86"),
    "amd64": op.join(DYLIB_DIRECTORY, "foo_amd64"),
}

@contextlib.contextmanager
def mkdtemp():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

