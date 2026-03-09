#include <iostream>
#include <fstream>
using namespace std;

struct Pokemon {
	char pokeID[11];
	char pokeName[31];
	char type1[26];
	char type2[26];
	int speed;
};

void input (Pokemon a) {
	cout << "ID: ";
	cin.ignore();
	cin.getline(a.pokeID, 11);
	cout << "Pokemon name: ";
	cin.ignore();
	cin.getline(a.pokeName, 31);
	cout << "Type: ";
	cin.ignore();
	cin.getline(a.type1, 26);
	cin.ignore();
	cin.getline(a.type2, 26);
	cout << "Speed: ";
	cin >> a.speed;
}

void print (Pokemon a) {
	cout << "ID: " << a.pokeID << endl;
	cout << "Pokemon name: " << a.pokeName << endl;
	cout << "Type: " << a.type1 << ", " << a.type2 << endl;
	cout << "Speed: " << a.speed << endl;
}

void printPokemon(Pokemon pokemons[], int &n) {
	int max = 0;
	for (int i = 1; i < n; i++) {
		if (pokemons[i].speed > pokemons[max].speed) max = i;
	}
	print (pokemons[max]);
}

int main () {
	Pokemon pokemon[3];
	for (int i = 0; i < 3; i++) {
		input(pokemon[i]);
	}
	int n = 3;
	printPokemon (pokemon, n);
}
