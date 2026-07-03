#include <iostream>
#include <cmath>
#include <string>
#include <cstring>
#include <cstdlib>
#include <stdlib.h>

using namespace std;

struct Pokemon{
	int pokeID;
	char pokeName[30];
	char type1[25];
	char type2[25];
	int speed;
};

void ReadFile (char fileName[], Pokemon pokemons[20], int &n){

	
}

int main(){
	int n=20;
	Pokemon pokemons[20];
	
	ifstream fin;
	fin.open("pokemon.txt");
	
	if (!fin.is_open){
		cout << "cannot open";
		return 0;
	}
	
	
	return 0;
}
