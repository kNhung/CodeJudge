#include <iostream>
#include <stdlib.h>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>

using namespace std;

const int MAXPOKE = 40;

struct Pokemon{
	string pokeID;
	string pokeName;
	string type1;
	string type2;
	int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n){
	n = 0;
	fstream fs;
	fs.open(fileName, ios::in);
	string s;
	char speed[100];
	getline(fs, s);
	while (!fs.eof()){
		getline(fs, pokemons[n].pokeID, ',');
		getline(fs, pokemons[n].pokeName, ',');
		getline(fs, pokemons[n].type1, ',');
		getline(fs, pokemons[n].type2, ',');
		fs.getline(speed, '\n');
		pokemons[n].speed = atoi(speed);
		n++;
	}
	n--; // vi co 1 lan xuong dong o trong file pokemon.txt
	fs.close();
}

void printPokemon(Pokemon pokemons[], int n){
	int posmax = 0;
	for (int i = 0; i < n; i++){
		if (pokemons[i].speed > pokemons[posmax].speed) posmax = i;
	}
	cout << "Pokemon with max speed: " << endl;
	cout << "ID: " << pokemons[posmax].pokeID << endl;
	cout << "Pokemon name: " << pokemons[posmax].pokeName << endl;
	cout << "Type: " << pokemons[posmax].type1;
	if (pokemons[posmax].type2 == "NULL") {
		cout << endl;
	}
	else cout << ", " << pokemons[posmax].type2 << endl;
	cout << "Speed: " << pokemons[posmax].speed << endl;
}

void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int &m){
	
}

int main(){
	int n, m;
	char type1[100], type2[100];
	char file[100] = "pokemon.txt";
	Pokemon pokemons[MAXPOKE];
	Pokemon results[MAXPOKE];
	ReadFile(file, pokemons, n);
	printPokemon(pokemons, n);
	cout << endl;
	cout << "Input Type 1: ";
	cin >> type1;
	cout << "Input Type 2: ";
	cin >> type2;
	cout << "The list of Pokemon with Type 1 = " << type1 << ", Type 2 = " << type2 << endl;
	
	return 0;
}
