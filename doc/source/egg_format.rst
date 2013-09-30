====================
Enstaller egg format
====================

Our egg format is an extension of the existing setuptools's egg.

A few notations:

    - $PREFIX: is understood as the prefix of the current python. In a standard
      install, $PREFIX/bin/python will contain python on unix,
      $PREFIX/python.exe on windows.
    - $BINDIR: where 'binaries' are installed. Generally $PREFIX/bin on unix,
      $PREFIX\\Scripts on windows.
    - $METADIR: package-specific directory where files/metadata get installed.
      Generally $PREFIX/EGG-INFO/$package_name

Metadata
========

All the metadata are contained within the EGG-INFO subdirectory.

This subdirectory contains all the metadata needed by egginst to install an egg
properly. It contains various text files with ad-hoc, poorly specified format:

        - EGG-INFO/info.json
        - EGG-INFO/inst/appinst.dat
        - EGG-INFO/inst/files_to_install.txt
        - EGG-INFO/spec/depend
        - EGG-INFO/spec/lib-depend
        - EGG-INFO/spec/lib-provide

inst subdirectory
-----------------

files_to_install.txt
~~~~~~~~~~~~~~~~~~~~

This file is used to define so-called proxies (a clumsy way to emulate
softlinks on windows) and support softlinks on non-windows platform. The file
defines one entry per line, and each entry is a space separated set of two
items.

On linux and os x, each entry looks as follows::

     EGG-INFO/usr/lib/libzmq.so                         libzmq.so.0.0.0

This defines a link join(prefix, 'lib/libzmq.so') to libzmq.so.0.0.0. More
precisely:

    - the left part is used to define the link name, the right part the target
      of the link.
    - the actual link name will be a join of the prefix + the part that comes
      after EGG-INFO/usr.

Entries may also look as follows::

     EGG-INFO/usr/bin/xslt-config                       False

This does not define a link to False, but instead tells egginst to ignore this
entry. Don't ask me why the entry is there in the first place...

A third format only encountered on windows' eggs::

    {TARGET}  {ACTION}

where {TARGET} must be in the zip archive, and where {ACTION} may be one of the
following:

    - PROXY: a proxy to the left part is created. A proxy is a set of two
      files, both written in the $BINDIR

        - one small exe which is a copy of the setuptools' cli.exe, renamed to
          basename({TARGET}).
        - another file {TARGET_NO_EXTENSION}-script.py where
          TARGET_NO_EXTENSION = basename(splitext({TARGET}))

    - Anything else: understood as a directory. In that case, {TARGET} will be
      copied into $ROOT\\{ACTION}\\basename({TARGET})

A PROXY example::

    EGG-INFO/usr/bin/ar.exe  PROXY

Egginst will create the following::

    # A copy of cli.exe
    $BINDIR\\ar.exe
    # the python script called by $BINDIR\\ar.exe, itself calling
    # $METADIR\\usr\\bin\\ar.exe
    $BINDIR\\ar-script.py

A non-PROXY example::

    EGG-INFO/usr/bin/ar.exe  EGG-INFO/mingw/usr/i686-w64-mingw32/bin

Egginst will create the following::
   
    # A copy of EGG-INFO/usr/bin/ar.exe
    $METADIR\\usr\\i686-w64-mingw32\\bin.ar.exe

appinst.dat
~~~~~~~~~~~

A python script that is used by 'applications' during the install process. Is
generally defined in the recipe files directory (as appinst.dat), and
explicitly included in our eggs through
workbench.eggcreator.EggCreator.add_appinst_dat()

Seems to be mostly used for setting up application shortcuts.

Misc
~~~~

I have seen a few other files in EGG-INFO/inst that seem bogus:

    - install_path.dat (in the sip-4.8.2-1.egg only), refer to some
      machine-specific installation path ?
    - app_install.py and app_uninstall.py. Coming from the obsolete enpisi (see
      buildsystem commit eb83c96aa2e1ccca78329faa0d7ddbca6da4a631). I am not
      sure whether enstaller is doing anything with them anymore

Icons may be found there as well, installed manually from recipes (see e.g.
idle-2.7.3 recipe).

spec subdirectory
-----------------

depend
~~~~~~

This file contains all the metadata required to solve dependencies.

It is a python script, which hopefully only defining variables, and is exec'ed
by egginst/enstaller to get the actual data (see egginst.eggmeta.parse_rawspec).

It is generally written by various functions in workbench.spec.

Typical format::

    metadata_version = '1.1'
    name = 'numpy'
    version = '1.7.1'
    build = 3

    arch = 'x86'
    platform = 'linux2'
    osdist = 'RedHat_5'
    python = '2.7'
    packages = [
      'MKL 10.3-1',
    ]

Regarding the content:

    - metadata_version is only used in our old style, obsolete (?) repo in
      enstaller.indexed_repo. It needs to be > '1.1' (yes, as a string, this is
      not a typo).
    - name: this is the name of the package. May use upper-case (e.g. for PIL,
      name will be 'PIL'). This is the name defined in our recipe.
    - version: the upstream version
    - build: the build #, as defined in the recipe.
    - arch/platform/osdist: should be one of the value in the corresponding
      attributes of epd_repo.platforms.Platform instances.  Note: those are set
      in a particularly convoluted way, as they are guessed from the egg
      content.  (See the code in workbench.spec.update_egg to get your mind
      blown away). I don't know what osdist is used for, and it can be None.
    - python: the python version, or None. As for arch/platform/osdist, this is
      not set directly, but guessed by looking into the .pyc code inside the
      egg. Unless you define that field explicitly that is (see greenlet recipe
      for an example of this technique).
    - packages: a list of dependencies, as defined in the PISI pspec.xml file.
      Note that if the platform is not correctly guessed, the dependencies will
      be silently ignoring the platform label. You will also note that name and
      version are space separated. The version part is actually optional.

summary
~~~~~~~

A copy of the Summary field in our pspec.xml. The code writing this is also in
workbench.spec.

lib-depend
~~~~~~~~~~

Free-form text format, contains the consolidated output of ldd or otool -L of
each library/python extension.

lib-provide
~~~~~~~~~~~

Free-form text format, contains the list of provided libraries in that egg.
While lib-depend unzip the egg to look for files, lib-provide uses the list of
files in files_to_install.txt and do a simple pattern matching to find out what
to write.

info.json
----------

Only eggs from pypi seem to contain that file. Looks like an aborted attempt of
using an existing file format to write our metadata.

The code to write this file is in endist.build_egg, and used in the
buildware/pypi package.

Note: if both this file and EGG-INFO/spec/depend are present, then info.json
overrides the attributes set in spec/depend (see egginst.eggmeta.info_from_z).
