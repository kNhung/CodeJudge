#include <iostream>
#include <cstdlib>
#include <fstream>
#include <string>
#include <cstring>
using namespace std;

struct Pokemon {
	char pokeID[10];
	char pokeName[30];
	char type1[25];
	char type2[25];
	int speed;
};

void ReadFile (char fileName[], Pokemon pokemons[], int &n){
	fstream f;
	f.open(fileName, ios::in);
	if (!f.is_open()){
		cout << "Cannot open file." << endl;
		return ;
	}
	Pokemon temp;
	f.getline(temp.pokeID, 10, ',');
	f.getline(temp.pokeName, 30, ',');
	f.getline(temp.type1, 25, ',');
	f.getline(temp.type2, 25);
	
	n = 0;
	while (!f.eof()){
		f.getline(pokemons[n].pokeID, 10, ',');
		f.getline(pokemons[n].pokeName, 30, ',');
		f.getline(pokemons[n].type1, 25, ',');
		f.getline(pokemons[n].type2, 25, ',');
		f >> pokemons[n].speed;
		n++;
	}
}

void print1Pokemon (Pokemon p){
	cout << "ID: " << p.pokeID << endl;
	cout << "Pokemon name: " << p.pokeName << endl;
	if (p.type2 == "NULL")
		cout << "Type: " << p.type1 << endl;
	else
		cout << "Type: " << p.type1 << ", " << p.type2 << endl;
	cout << "Speed: " << p.speed << endl; 
}
void printPokemon (Pokemon pokemons[], int n){
	int max = 0;
	for (int i = 0; i < n; i++){
		if (max < pokemons[i].speed)
			max = pokemons[i].speed;
	}
	
	for (int i = 0; i < n; i++){
		if (pokemons[i].speed == max){
			print1Pokemon(pokemons[i]);
		}
	}
}

void printSearch (Pokemon p[], int n){
	for (int i = 0; i < n; i++){
		cout << "ID: " << p[i].pokeID << " - " << "Name: " << p[i].pokeName << endl;
	}
}

void searchPokemonByType (char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int &m){
	m = 0;
	for (int i = 0; i < n; i++){
		if (pokemons[i].type1 == type1){
			if (type2 == "NULL"){
				for (int j = 0; j < strlen(pokemons[i].pokeID); j++){
					result[m].pokeID[j] = pokemons[i].pokeID[i];
				}
				result[m].pokeID[strlen(pokemons[i].pokeID)] = '\0';
				for (int j = 0; j < strlen(pokemons[i].pokeName); j++){
					result[m].pokeName[j] = pokemons[i].pokeName[i];
				}
				result[m].pokeName[strlen(pokemons[i].pokeName)] = '\0';
				m++;
			} else if (type2 != "NULL" && pokemons[i].type2 == type2){
				for (int j = 0; j < strlen(pokemons[i].pokeID); j++){
					result[m].pokeID[j] = pokemons[i].pokeID[i];
				}
				result[m].pokeID[strlen(pokemons[i].pokeID)] = '\0';
				for (int j = 0; j < strlen(pokemons[i].pokeName); j++){
					result[m].pokeName[j] = pokemons[i].pokeName[i];
				}
				result[m].pokeName[strlen(pokemons[i].pokeName)] = '\0';
				m++;
			} 
		}
		
		if (pokemons[i].type1 == type2){
			if (type1 == "NULL"){
				for (int j = 0; j < strlen(pokemons[i].pokeID); j++){
					result[m].pokeID[j] = pokemons[i].pokeID[i];
				}
				result[m].pokeID[strlen(pokemons[i].pokeID)] = '\0';
				for (int j = 0; j < strlen(pokemons[i].pokeName); j++){
					result[m].pokeName[j] = pokemons[i].pokeName[i];
				}
				result[m].pokeName[strlen(pokemons[i].pokeName)] = '\0';
				m++;
			} else if (type1 != "NULL" && pokemons[i].type2 == type1){
				for (int j = 0; j < strlen(pokemons[i].pokeID); j++){
					result[m].pokeID[j] = pokemons[i].pokeID[i];
				}
				result[m].pokeID[strlen(pokemons[i].pokeID)] = '\0';
				for (int j = 0; j < strlen(pokemons[i].pokeName); j++){
					result[m].pokeName[j] = pokemons[i].pokeName[i];
				}
				result[m].pokeName[strlen(pokemons[i].pokeName)] = '\0';
				m++;
			} 
		}
	}
}

int main (){
	char fileName[100] = "pokemon.txt";
	Pokemon pokemon[100];
	int n;
	
	ReadFile(fileName, pokemon, n);
	cout << "Pokemon with max speed: " << endl;
	printPokemon(pokemon, n);
	
	cout << endl;
	char type1[100], type2[100];
	Pokemon result[100];
	int m;
	cout << "Input type1: ";
	cin.getline(type1, 100);
	cout << "Input type2: ";
	cin.getline(type2, 100);
	cout << "The list of Pokemon with Type = " << type1 << " " << type2 << ": " << endl;
	searchPokemonByType(type1, type2, pokemon, n, result, m);
	printSearch(result, m);
	return 0;
}
