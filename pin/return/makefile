

TOOL_NAME = return_pin

PIN_HOME=/home/songlh/tools/pin/pin-2.12-56759-gcc.4.4.7-linux

CC=gcc

CXX=g++

CXX_FLAGS=-DBIGARRAY_MULTIPLIER=1 -DUSING_XED -Wall -Werror -Wno-unknown-pragmas -fno-stack-protector -DTARGET_IA32E -DHOST_IA32E -fPIC -DTARGET_LINUX -O3 -fomit-frame-pointer -fno-strict-aliasing -Wno-deprecated -c

CXX_INCLUDES=-I${PIN_HOME}/source/tools/InstLib -I${PIN_HOME}/source/include/pin -I${PIN_HOME}/source/include/pin/gen -I${PIN_HOME}/extras/components/include -I${PIN_HOME}/extras/xed2-intel64/include 

LINK_FLAGS=-shared -Wl,-rpath=${PIN_HOME}/intel64/runtime/cpplibs -Wl,--hash-style=sysv -Wl,-Bsymbolic -Wl,--version-script=${PIN_HOME}/source/include/pin/pintool.ver 

LIBRARY= -L${PIN_HOME}/intel64/runtime/cpplibs -L${PIN_HOME}/intel64/lib -L${PIN_HOME}/intel64/lib-ext -L${PIN_HOME}/extras/xed2-intel64/lib -lpin -lxed -ldwarf -lelf -ldl

## build rules

all :
	${CXX} ${CXX_FLAGS} ${CXX_INCLUDES} ${TOOL_NAME}.cpp -o ${TOOL_NAME}.o

	${CXX} ${LINK_FLAGS} -o ${TOOL_NAME}.so ${TOOL_NAME}.o ${LIBRARY}

## cleaning
clean:
	-rm -rf *.o *.out *.tested *.failed *.d *makefile.copy *.exp *.lib

