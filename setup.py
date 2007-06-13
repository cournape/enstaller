from setuptools \
    import setup, find_packages


setup(
    name         = "enthought.enstaller",
    version      = "2.1.0b1",
    description  = "The Enthought installer.  Enhances setuptools by adding " \
                   "query options, support for post-install scripts, and much " \
                   "more.",
    author       = "Richard L. Ratzel",
    author_email = "rlratzel@enthought.com",
    url          = "http://code.enthought.com/enstaller",
    license      = "BSD",
    zip_safe     = False,
    packages     = find_packages(),
    ext_modules  = [],
    include_package_data = True,

    entry_points = {"console_scripts":
                    ["enstaller = enthought.enstaller.launcher:launch"],
                    },

    install_requires = [
       "enthought.traits>=3.0.0b1",
       "enthought.ets>=2.0",
       ],
    
    extras_require = {
        "gui": ["enthought.enstaller.gui>=2.1.0b1, <2.1.1"],
        },
    
    namespace_packages = [
        "enthought",
        "enthought.enstaller",
        ],
)

