# include <iostream>
# include <iostream>
# include <cmath>
# include <string>
# include <cstring>
# include <cstdlib>
# include <stdlib.h>
# include <fstream>

# define Max 100

using namespace std;

struct Pokemon {
	char pokeID[11];
	char type1[26];
	char type2[26];
	int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n) {
	fstream fin;
	fin.open(fileName, ios::in);
	if (!fin.is_open()) {
		cout << "Cannot open" << '\n';
	}
	
	else {
		
	}
}

void printPokemon(Pokemon pokemons[], int n){
	
}


void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n,
Pokemon result[], int& m) {
	
}

int main () {
	char fileName[Max] = "pokemon.txt";
	int n;
	
	return 0;
}
