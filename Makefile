CXX?=g++
CMS?=/home/cipherboy/GitHub/msoos/cryptominisat/build
PYTHON?=python3

# Python-specific configuration
PYINCLUDE=$(shell $(PYTHON) -c 'import sysconfig; print(sysconfig.get_config_var("INCLUDEPY"))')
PYLDVERSION=$(shell $(PYTHON) -c 'import sysconfig; print(sysconfig.get_config_var("LDVERSION"))')
PYEXT=$(shell $(PYTHON) -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')

# Various sets of compilation flags
DEBUGFLAGS=-Og -ggdb -DDEBUG=1 -pg
OPTIMIZEFLAGS=-O3 -march=native -mtune=native
DISABLEDWARNINGS=-Wno-error=cast-function-type -Wno-error=unused-parameter -Wno-error=missing-field-initializers
CLANGWARNINGS=-Wno-unused-command-line-argument -Wno-unknown-warning-option
WARNINGFLAGS=-std=c++2a -Wall -Werror -Wextra -pedantic
GENERALFLAGS=-pthread -fwrapv -m64 -pipe -fexceptions -DDYNAMIC_ANNOTATIONS_ENABLED=1 -fPIC -fasynchronous-unwind-tables -D_GNU_SOURCE
SECURITYFLAGS=-Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -fstack-protector-strong -grecord-gcc-switches -fcf-protection
COMPILEFLAGS=${CPPFLAGS} ${CXXFLAGS} ${GENERALFLAGS} ${SECURITYFLAGS}

# We need optimizations for -D_FORTIFY_SOURCE; always add some.
ifeq ($(DEBUG),1)
COMPILEFLAGS+=${DEBUGFLAGS}
else
COMPILEFLAGS+=${OPTIMIZEFLAGS}
endif

# Library linking flags
CMSFLAGS=-I$(CMS)/cmsat5-src -L$(CMS)/lib -lcryptominisat5 -Wl,-rpath,$(CMS)/lib
CMSHFLAGS=$(CMSFLAGS) -I$(CURDIR)/build/include -L$(CURDIR)/build/lib -lcmsh -Wl,-rpath,$(CURDIR)/build/lib
PYTHONFLAGS=-I$(PYINCLUDE) -lpython$(PYLDVERSION)
LINKERFLAGS=${LDFLAGS} -Wl,-z,relro -Wl,--as-needed -Wl,-z,now -g


# Build targets
all: cmsh check-native
.PHONY : all

cmsh: dirs native module

dirs:
	mkdir -p build/lib
	mkdir -p build/include
	mkdir -p build/cmsh
	mkdir -p build/.objects

native: dirs build/lib/libcmsh.so build/cmsh/_native${PYEXT}

build/lib/libcmsh.so: build/.objects/constraint_t.o build/.objects/model_t.o
	$(CXX) $(WARNINGFLAGS) $(COMPILEFLAGS) $(LINKERFLAGS) -shared build/.objects/constraint_t.o build/.objects/model_t.o -o build/lib/libcmsh.so
	cp src/cmsh.h build/include/cmsh.h

build/.objects/constraint_t.o: src/constraint_t.cpp src/cmsh.h
	$(CXX) $(WARNINGFLAGS) $(COMPILEFLAGS) $(CMSFLAGS) -c src/constraint_t.cpp -o build/.objects/constraint_t.o

build/.objects/model_t.o: src/model_t.cpp src/cmsh.h
	$(CXX) $(WARNINGFLAGS) $(COMPILEFLAGS) $(CMSFLAGS) -c src/model_t.cpp -o build/.objects/model_t.o

build/cmsh/_native$(PYEXT): bindings/pycmsh.cpp build/lib/libcmsh.so
	$(CXX) $(COMPILEFLAGS) $(DISABLEDWARNINGS) $(WARNINGFLAGS) $(CMSFLAGS) $(CMSHFLAGS) $(PYTHONFLAGS) -shared bindings/pycmsh.cpp -o build/cmsh/_native$(PYEXT)

module: native python/*.py tools/setup.py
	cp python/*.py build/cmsh/
	cp tools/setup.py build/setup.py

test: check

check: check-native
	build/basic_api
	build/sudoku
	PYTHONPATH=build $(PYTHON) -m pytest

check-native: build/basic_api build/sudoku

build/basic_api: native tests/native/basic_api.cpp
	$(CXX) $(WARNINGFLAGS) $(COMPILEFLAGS) $(CMSHFLAGS) tests/native/basic_api.cpp -o build/basic_api

build/sudoku: native tests/native/sudoku.cpp
	$(CXX) $(WARNINGFLAGS) $(COMPILEFLAGS) $(CMSHFLAGS) tests/native/sudoku.cpp -o build/sudoku

distclean: clean

clean:
	rm -rf build/
	mkdir -p build/
	touch build/.gitkeep

lint:
	pylint cmsh
