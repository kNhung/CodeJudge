#include <iostream>
#include <fstream>
#include <string>
#include <cstring>

using namespace std;

struct Pokemon {
	char pokeID [10], pokeName [30], type1 [25], type2 [25];
	int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n) {
	ifstream fin;
	fin.open (fileName);
	n = 0;
	
	if (!fin.is_open()) {
		cout << "Can't open file1";
	}
	
	string ignore_line = "";
	getline (fin, ignore_line);
	
	string pokeID, pokeName, type1, type2, speed;
	
	while (getline (fin, pokeID, ',')) {
		n++;
		getline (fin, pokeName, ',');
		getline (fin, type1, ',');
		getline (fin, type2, ',');	
		getline (fin, speed, ',');
		
		pokemons[n - 1].pokeID = pokeID;
		pokemons[n - 1].pokeName = pokeName;
		pokemons[n - 1].type1 = type1;
		pokemons[n - 1].type2 = type2;
		pokemons[n - 1].speed = stoi(speed);
	}
	
	fin.close();
}

void printPokemon (Pokemon pokemon) {
	cout << "ID: " << pokemon.pokeID << endl;
	cout << "Pokemon name: " << pokemon.pokeName << endl;
	cout << "Type: " << pokemon.type1 << ", " << pokemon.type2 << endl;
	cout << "Speed: " << pokemon.speed;

}

int main() {
	Pokemon pokemons[100];
	int n;
	
	ReadFile("pokemon.txt", pokemons, n);
	
	printPokemon (pokemons[0])
	
	return 0;
}
