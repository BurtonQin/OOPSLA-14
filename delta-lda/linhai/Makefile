CXX=g++
CFLAGS = -g -Wall


TARGET=deltaLDA

SRC := parser.cpp deltaLDA.cpp
OBJ := $(SRC:.cpp=.o)


all: deltaLDA

%.o: %.cpp
	@echo "   CXX '$<' ==> '$@'"
	$(CXX) $(CFLAGS) $(CXXFLAGS) -c $< -o $@


deltaLDA: ${OBJ}
	$(CXX) $(CFLAGS) ${OBJ} -o deltaLDA 


clean:
	rm -rf deltaLDA *.o
