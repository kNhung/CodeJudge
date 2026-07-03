#include <iostream>
#include <fstream>
#include <cstring>
#include <string.h>
#include <stdlib.h>

#define max 1000
using namespace std;

struct Pokemon{
	char pokeID[11];
	char pokeName[31];
	char type1[26];
	char type2[26];
	int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n){
	char a[max];
	int i = 0;
	ifstream f("pokemon.txt");
	if(!f.is_open()){
		cout << "can not open file";
	}
	f.getline(a,1000);
	while(!f.eof()){
		f.getline(pokemons[i].pokeID,1000, ',');
		f.getline(pokemons[i].pokeName,1000, ',');
		f.getline(pokemons[i].type1,1000, ',');
		f.getline(pokemons[i].type2,1000, ',');
//		f.getline(pokemons[i].speed,1000);
	}
	for (int j = 0; j < i; j++){
		cout << pokemons[i].pokeID << endl;
		cout << pokemons[i].pokeName << endl;
		cout << pokemons[i].type1 << endl;
		cout << pokemons[i].type2 << endl;
		cout << pokemons[i].speed << endl;
	}
	f.close();
}

void printPokemon(Pokemon pokemon[], int n){
	int max = 0;
	int b;
	for (int i = 0; i < n; i++){
		if(pokemons[i].speed > max){
			max = pokemons[i].speed;
			b = i;
		}
	}
	cout << "ID" << pokemons[b].pokeID << endl;
	cout << "Pokemon name: " << pokemons[b].pokeName << endl;
	cout << "Type: " << pokemonsbi].type1 << ", " << pokemons[b].type2 << endl;
	cout << "speed: " << pokemons[b].speed;
}
int main(){
	char a[max];
	Pokemon pokemons;
	int n;
	ReadFile(a,Pokemon pokemons, n);
	return 0;
}
