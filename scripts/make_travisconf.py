import contextlib
import itertools

print("# Generated by scripts/make_travisconf.py")
print("")

i = 0


def p(s):
    print("    " * i + s)


@contextlib.contextmanager
def section(name):
    p("{}:".format(name))
    global i
    i += 1
    yield
    i -= 1
    print("")

p("sudo: true")
p("language: python")
p("")

with section("install"):
    # Travis uses an outdated PyPy, this installs the most recent one.  This
    # makes the tests run on Travis' legacy infrastructure, but so be it.
    # temporary pyenv installation to get pypy-2.6 before container infra
    # upgrade
    # Taken from werkzeug, which took it from pyca/cryptography
    p('- if [ "$TRAVIS_PYTHON_VERSION" == "pypy" ]; then')
    p('    git clone https://github.com/yyuu/pyenv.git ~/.pyenv;')
    p('    PYENV_ROOT="$HOME/.pyenv";')
    p('    PATH="$PYENV_ROOT/bin:$PATH";')
    p('    eval "$(pyenv init -)";')
    p('    pyenv install pypy-4.0.1;')
    p('    pyenv global pypy-4.0.1;')
    p('    python --version;')
    p('    pip --version;')
    p('  fi')

    p('- "pip install -U pip"')
    p('- "pip install wheel"')
    p('- "make -e install-dev"')
    p('- "make -e install-$BUILD"')

with section("script"):
    p('- "make -e $BUILD"')

with section("matrix"):
    with section("include"):
        for python in ("2.7", "3.3", "3.4", "3.5", "pypy"):
            h = lambda: p("- python: {}".format(python))
            h()
            p("  env: BUILD=style")

            if python in ("2.7", "3.5"):
                dav_servers = ("radicale", "owncloud", "baikal", "davical")
                rs_servers = ("mysteryshack",)
            else:
                dav_servers = ("radicale",)
                rs_servers = ()

            for (server_type, server), requirements in itertools.product(
                itertools.chain(
                    (("REMOTESTORAGE", x) for x in rs_servers),
                    (("DAV", x) for x in dav_servers)
                ),
                ("devel", "release", "minimal")
            ):
                h()
                p("  env: "
                  "BUILD=test "
                  "{server_type}_SERVER={server} "
                  "REQUIREMENTS={requirements}"
                  .format(server_type=server_type,
                          server=server,
                          requirements=requirements))
