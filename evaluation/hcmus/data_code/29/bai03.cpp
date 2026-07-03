#include <iostream>
#include <fstream>
#include <cstring>

struct Pokemon {
	char pokeID[11];
	char pokeName[31];
	char type1[26];
	char type2[16];
	int speed;
};

void parsePokemon(const char line[], Pokemon &poke) {
	int pos = 0;
	int write_pos = 0;
	while (line[pos] != ',') poke.pokeID[write_pos++] = line[pos++];
	++pos;
	poke.pokeID[write_pos] = 0;
	write_pos = 0;
	while (line[pos] != ',') poke.pokeName[write_pos++] = line[pos++];
	++pos;
	poke.pokeName[write_pos] = 0;
	write_pos = 0;
	while (line[pos] != ',') poke.type1[write_pos++] = line[pos++];
	++pos;
	poke.type1[write_pos] = 0;
	write_pos = 0;
	while (line[pos] != ',') poke.type2[write_pos++] = line[pos++];
	++pos;
	poke.type2[write_pos] = 0;
	poke.speed = 0;
	while (line[pos]) poke.speed = poke.speed * 10 + (line[pos++] - '0');
}

void ReadFile(const char fileName[], Pokemon pokemons[], int &n) {
	std::ifstream fin;
	char line[256];
	fin.open(fileName);
	fin.getline(line, sizeof(line));
	n = 0;
	while (fin.getline(line, sizeof(line))) {
		parsePokemon(line, pokemons[n++]);
	}
	fin.close();
}

void printPokemon(Pokemon pokemons[], int n) {
	int best = 0;
	for (int i = 1; i < n; ++i) {
		if (pokemons[i].speed > pokemons[best].speed) best = i;
	}
	
	std::cout << "Pokemon with max speed:\n";
	std::cout << "ID: " << pokemons[best].pokeID << '\n';
	std::cout << "Pokemon name: " << pokemons[best].pokeName << '\n';
	std::cout << "Type: ";
	if (strcmp(pokemons[best].type1, "NULL")) {
		std::cout << pokemons[best].type1;
		if (strcmp(pokemons[best].type2, "NULL")) {
			std::cout << ", " << pokemons[best].type2;
		}
	} else {
		std::cout << pokemons[best].type2;
	}
	
	std::cout << '\n';
	std::cout << "Speed: " << pokemons[best].speed << '\n';
}

void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int& m) {
 	m = 0;
	for (int i = 0; i < n; ++i) {
		if (strcmp(pokemons[i].type1, type1) == 0 && strcmp(pokemons[i].type2, type2) == 0) {
			result[m++] = pokemons[i];
			continue;
		}
		
		if (strcmp(pokemons[i].type1, type2) == 0 && strcmp(pokemons[i].type2, type1) == 0) {
			result[m++] = pokemons[i];
			continue;
		}
	}
}

int main(void) {
	Pokemon pokemons[100];
	int n_pokemons;
	ReadFile("pokemon.txt", pokemons, n_pokemons);
	printPokemon(pokemons, n_pokemons);
	
	std::cout << '\n';
	
	char type1[100], type2[100];
	std::cout << "Input type1: ";
	std::cin.getline(type1, sizeof(type1));
	std::cout << "Input type2: ";
	std::cin.getline(type2, sizeof(type2));
	
	Pokemon results[100];
	std::cout << "The list of Pokemon with Type = ";
	if (strcmp(type1, "NULL")) {
		std::cout << type1;
		if (strcmp(type2, "NULL")) std::cout << ", " << type2;	
	} else std::cout << type2;
	std::cout << ":\n";
	
	int n_results;
	searchPokemonByType(type1, type2, pokemons, n_pokemons, results, n_results);
	for (int i = 0; i < n_results; ++i) {
		std::cout << "ID: " << results[i].pokeID << " - Name: " << results[i].pokeName << '\n';
	}
	return 0;
}
