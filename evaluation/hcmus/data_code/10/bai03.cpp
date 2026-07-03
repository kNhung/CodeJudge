#include <iostream>
#include <cmath>
#include <cstring>
#include <string>
#include <fstream>

using namespace std;

struct Pokemon{
	char pokeID[11];
	char pokeName[31];
	char type1[26];
	char type2[26];
	int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n){
	string s(fileName);
	ifstream f;
	f.open(fileName);
	string ignore;
	getline(f, ignore);
	n = 0;
	while(!f.eof()){
		string s;
		getline(f, s, ',');
		strcpy(pokemons[n].pokeID, s.c_str());
		getline(f, s, ',');
		strcpy(pokemons[n].pokeName, s.c_str());
		getline(f, s, ',');
		strcpy(pokemons[n].type1, s.c_str());
		getline(f, s, ',');
		strcpy(pokemons[n].type2, s.c_str());
		cin >> pokemons[n].speed;
		n++;
	}
	f.close();
}

void printPokemon(Pokemon pokemons[], int n){
	int maxSpeed = pokemons[0].speed, posMax = 0;
	for(int i = 1; i < n; i++){
		if(pokemons[i].speed > maxSpeed){
			maxSpeed = pokemons[i].speed;
			posMax = i;
		}
	}
	cout << "Pokemon with max speed: " << endl;
	cout << "ID: " << pokemons[posMax].pokeID << endl;
	cout << "Pokemon name: " << pokemons[posMax].pokeName << endl;
	cout << "Type: " << pokemons[posMax].type1;
	if(strcmp(pokemons[posMax].type2, "NULL"))
		cout << ", " << pokemons[posMax].type2;
	cout << endl;
	cout << "Speed: " << maxSpeed << endl;
}

void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int& m){
	string type;
	m = 0;
	cout << "Input Type1: ";
	cin.getline(type1, 26);
	cout << "Input Type2: ";
	cin.getline(type2, 26);
	for(int i = 0; i < n; i++){
		if(!strcmp(pokemons[i].type1, type1) && !strcmp(pokemons[i].type2, type2)){
			result[m] = pokemons[i];
			m++;
		}
		else if(!strcmp(pokemons[i].type1, type2) && !strcmp(pokemons[i].type2, type1)){
			result[m] = pokemons[i];
			m++;
		}
	}
}



int main(){
	int n, m;
	Pokemon pokemons[100] = {}, result[100] = {};
	char fileName[100];
	strcpy(fileName, "pokemon.txt");
	ReadFile(fileName, pokemons, n);
	printPokemon(pokemons, n);
	char type1[26] = {}, type2[26] = {};
	searchPokemonByType(type1, type2, pokemons, n, result, m);
	cout << "The list of Pokemon with Type = " << type1;
	if(strcmp(type2, "NULL"))
		cout << ", " << type2;
	cout << ":" << endl;
	for(int i = 0; i < m; i++){
		cout << "ID" << result[i].pokeID << "- Name: " << result[i].pokeName << endl;
	}
	return 0;
}






