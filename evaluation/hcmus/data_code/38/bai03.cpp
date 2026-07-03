#include <iostream>
#include <cstring>
#include <string>
#include <fstream>
using namespace std;

struct Pokemon{
	char pokeID[10];
	char pokeName[30];
	char type1[25];
	char type2[25];
	int speed;
};



int main(){
	fstream poke;
	string line;
	poke.open("pokemon.txt", ios::out);
	if(poke.is_open()){
		
		
		poke.close();
	}
	return 0;
}
