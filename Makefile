CXX?=g++
CMS?=${CURDIR}/msoos_cryptominisat/build
PYTHON?=python3

# Python-specific configuration
PYINCLUDE=$(shell ${PYTHON} -c 'import sysconfig; print(sysconfig.get_config_var("INCLUDEPY"))')
PYLDVERSION=$(shell ${PYTHON} -c 'import sysconfig; print(sysconfig.get_config_var("LDVERSION"))')
PYEXT=$(shell ${PYTHON} -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')

# Various sets of compilation flags
DEBUGFLAGS=-Og -ggdb -DDEBUG=1 -pg
OPTIMIZEFLAGS=-O3 -march=native -mtune=native
DISABLEDWARNINGS=-Wno-error=cast-function-type -Wno-error=unused-parameter -Wno-error=missing-field-initializers -Wno-cast-function-type
CLANGWARNINGS=-Wno-unused-command-line-argument -Wno-unknown-warning-option
WARNINGFLAGS=-std=c++2a -Wall -Werror -Wextra -pedantic
GENERALFLAGS=-pthread -fwrapv -m64 -pipe -fexceptions -DDYNAMIC_ANNOTATIONS_ENABLED=1 -fPIC -fasynchronous-unwind-tables -D_GNU_SOURCE
SECURITYFLAGS+=-Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -fstack-protector-strong -grecord-gcc-switches -fcf-protection

COMPILEFLAGS=${CPPFLAGS} ${CXXFLAGS} ${GENERALFLAGS} ${SECURITYFLAGS}
CMSCOMPILEFLAGS=${GENERALFLAGS} ${SECURITYFLAGS}

# We need optimizations for -D_FORTIFY_SOURCE; always add some.
ifeq (${DEBUG},1)
COMPILEFLAGS+=${DEBUGFLAGS}
CMSCOMPILEFLAGS+=${DEBUGFLAGS}
else
COMPILEFLAGS+=${OPTIMIZEFLAGS}
CMSCOMPILEFLAGS+=${OPTIMIZEFLAGS}
endif

# Library linking flags
CMSFLAGS=-I${CURDIR}/build/include -L${CURDIR}/build/cmsh -lcryptominisat5 -Wl,-rpath,${CURDIR}/build/cmsh
CMSHFLAGS=${CMSFLAGS} -lcmsh -Wl,-rpath,${CURDIR}/build/cmsh
PYTHONFLAGS=-I${PYINCLUDE} -lpython${PYLDVERSION}
LINKERFLAGS=${LDFLAGS} -Wl,-z,relro -Wl,--as-needed -Wl,-z,now -g


# Build targets
all: cmsh check-native
.PHONY : all

cmsh: dirs cmslibs native module

dirs: build/include build/cmsh build/.objects

build/include:
	mkdir -p build/include

build/cmsh:
	mkdir -p build/cmsh

build/.objects:
	mkdir -p build/.objects

cmslibs: dirs
	cp -r ${CMS}/include/cryptominisat5 build/include/
	cp -r ${CMS}/lib/libcryptominisat5.so* build/cmsh/

native: dirs build/cmsh/libcmsh.so build/cmsh/_native${PYEXT}

build/cmsh/libcmsh.so: build/.objects/constraint_t.o build/.objects/model_t.o
	${CXX} ${WARNINGFLAGS} ${COMPILEFLAGS} ${LINKERFLAGS} -shared build/.objects/constraint_t.o build/.objects/model_t.o -o build/cmsh/libcmsh.so
	cp src/cmsh.h build/include/cmsh.h

build/.objects/constraint_t.o: src/constraint_t.cpp src/cmsh.h
	${CXX} ${WARNINGFLAGS} ${COMPILEFLAGS} ${CMSFLAGS} -c src/constraint_t.cpp -o build/.objects/constraint_t.o

build/.objects/model_t.o: src/model_t.cpp src/cmsh.h
	${CXX} ${WARNINGFLAGS} ${COMPILEFLAGS} ${CMSFLAGS} -c src/model_t.cpp -o build/.objects/model_t.o

build/cmsh/_native${PYEXT}: bindings/pycmsh.cpp build/cmsh/libcmsh.so
	${CXX} ${COMPILEFLAGS} ${DISABLEDWARNINGS} ${WARNINGFLAGS} ${CMSFLAGS} ${CMSHFLAGS} ${PYTHONFLAGS} -shared bindings/pycmsh.cpp -o build/cmsh/_native${PYEXT}

module: native python/*.py tools/setup.py
	cp python/*.py build/cmsh/
	cp python/*.pyi build/cmsh/
	cp tools/setup.py build/setup.py

test: check

check: check-native
	build/basic_api
	build/sudoku
	${PYTHON} -c 'import pytest' || ${PYTHON} -m pip install --user pytest
	PYTHONPATH=build ${PYTHON} -m pytest --ignore=msoos_cryptominisat

check-native: cmsh build/basic_api build/sudoku

build/basic_api: tests/native/basic_api.cpp
	${CXX} ${WARNINGFLAGS} ${COMPILEFLAGS} ${CMSHFLAGS} tests/native/basic_api.cpp -o build/basic_api

build/sudoku: tests/native/sudoku.cpp
	${CXX} ${WARNINGFLAGS} ${COMPILEFLAGS} ${CMSHFLAGS} tests/native/sudoku.cpp -o build/sudoku

# Clean targets
distclean: clean
	rm -rf msoos_cryptominisat/build/

clean:
	rm -rf build/
	mkdir -p build/
	touch build/.gitkeep

# Helpers
lint:
	${PYTHON} -c 'import pylint' || ${PYTHON} -m pip install --user pylint
	${PYTHON} -m pylint --disable=R0914,E1136 build/cmsh

typecheck:
	${PYTHON} -c 'import mypy' || ${PYTHON} -m pip install --user mypy
	cd build && ${PYTHON} -m mypy --python-executable ${PYTHON} cmsh
	MYPYPATH="build" ${PYTHON} -m mypy --python-executable ${PYTHON} --ignore-missing-imports tests/python

install:
	cd build/ && ${PYTHON} -m pip install --user -e .

cms: msoos_cryptominisat
	mkdir -p msoos_cryptominisat/build
	cd msoos_cryptominisat/build && CFLAGS="${CMSCOMPILEFLAGS}" CXX="${CXX}" cmake -DUSE_GAUSS=ON -DENABLE_TESTING=OFF -DMIT=OFF -DDNOVALGRIND=ON -DENABLE_PYTHON_INTERFACE=OFF .. && make -j $(shell nproc)
	cd ../../

msoos_cryptominisat:
	git clone https://github.com/msoos/cryptominisat msoos_cryptominisat
