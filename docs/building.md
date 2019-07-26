# Building `cmsh`

`cmsh` currently relies on a Make-based approach to building and supports
parallel make invocations. It respects `CXXFLAGS`, `CPPFLAGS`, and `LDFLAGS`,
but doesn't pass these through to CryptoMiniSat. Additionally, CryptoMiniSat
can be built with `DEBUG=1` in the environment to automatically select flags
reasonable for debug builds.

To use an already-built CryptoMiniSat, pass the `CMS` environment variable
equal to the path of the `build/` directory:

	CMS=/path/to/cryptominisat/build make clean all check

## Makefile targets

The `cmsh` Makefile supports the following targets:

	- `all` -- equivalent to `cmsh` + `check-native`
	- `check` -- execute all tests
	- `check-native` -- build native test cases
	- `clean` -- clean the build/ folder
	- `cms` -- clone and build CryptoMiniSat
	- `cmsh` -- build everything for the Python bindings
	- `distclean` -- `clean` + removes CryptoMiniSat build artifacts
	- `lint` -- runs pylint on `cmsh`

## Build Artifacts

All build artifacts are placed under `build/`: this includes a `setup.py` for
installing `build/cmsh`, `build/include` for referencing CryptoMiniSat and
`cmsh` headers, and the core `cmsh` library in `build/cmsh`. Native tests are
placed directly under `build/` as executables. Intermediate object files are
hidden under `cmsh/.objects`.

## Installing `cmsh`

To install cmsh for the current user, run:

	cd build && pip3 install --user -e .

Remove the `--user` flag and invoke with `sudo` if you truly wish to install
for all users. This is usually not desired.

We currently don't support packaging `cmsh` in distros and wouldn't
recommend it. While possible, it would require the versions of CryptoMiniSat
that are shipped to be updated and to turn on Gaussian Elimination support.
