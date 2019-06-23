CPP?=g++
CMS?=/home/cipherboy/GitHub/msoos/cryptominisat/build
CPPFLAGS+=-std=c++2a -Wall -Werror -Wextra -pedantic -I$(CMS)/cmsat5-src -L$(CMS)/lib -lcryptominisat5 -Wl,-rpath,$(CMS)/lib -fPIC
CMSHFLAGS=-Ibuild/include -Lbuild/lib -lcmsh -Wl,-rpath,build/lib

cmsh: native

native: build/lib/libcmsh.so

build/lib/libcmsh.so: build/constraint_t.o build/model_t.o
	mkdir -p build/lib
	mkdir -p build/include
	g++ $(CPPFLAGS) -shared build/constraint_t.o build/model_t.o -o build/lib/libcmsh.so
	cp src/cmsh.h build/include/cmsh.h

build/constraint_t.o: src/constraint_t.cpp src/cmsh.h
	g++ $(CPPFLAGS) -c src/constraint_t.cpp -o build/constraint_t.o

build/model_t.o: src/model_t.cpp src/cmsh.h
	g++ $(CPPFLAGS) -c src/model_t.cpp -o build/model_t.o

test: check

check: check-native
	build/basic_api
	# pytest-3

check-native: native
	mkdir -p build/tests
	g++ $(CPPFLAGS) $(CMSHFLAGS) tests/native/basic_api.cpp -o build/basic_api

distclean: clean

clean:
	rm -rf build/
	mkdir -p build/
	touch build/.gitkeep
