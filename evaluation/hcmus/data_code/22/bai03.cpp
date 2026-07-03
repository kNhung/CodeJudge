#include <iostream>
#include <fstream>
#include <string>
using namespace std;


struct Pokemon{
	char pokeID[11];
	char pokeName[31];
	char type1[26];
	char type2[26];
	int speed;
};

int main(){
	Pokemon pokemon[100];
	char fileName[100];
	int n;
	
	ReadFile("pokemon.txt", pokemon, n);
	
	printPokemon(pokemon, n);
	
	
	
	void searchPokemonByType(char type[], char type2[], Pokemon pokemon[], int n, Pokemon result[], int &m )
	
	fin.close();
	return 0;
}

void ReadFile(char fileName[], Pokemon pokemon[], int &n){
	iftream fin;
	fin.open("pokemon.txt");
	bool index = 1;
	while(fin.eof()){
		if(ans){
			fin.getline(fileName, 100);
		}
	} else {
		fin >> p[size].pokeID;
		fin.ignore();
		fin.getline(pokemon[n].pokeName, ',');
		fin.getline(pokemon[n].type1, ',');
		fin.getline(pokemon[n].type2, ',');
		fin >> pokemon[n].speed;
		fin.ignore();
		n++;
	}
	index = !index;	
}

void printPokemon(Pokemon pokemon[], int n){
	int maxSpeed = 0;
	for (int i = 1; i < n; i++){
		if (pokemon[i].speed > pokemon[maxSpeed].speed){
			maxSpeed = i;
		}
	}
	cout << "ID: " << pokemon[maxSpeed].pokeID << endl;
	cout << "Pokemon name: " << pokemon[maxSpeed].pokeName << endl;
	cout << "Type: " << pokemon[i].type1 << ", " << pokemon[i].type2 << endl;
	cout << "Speed: " << pokemon[i].speed;
}
void searchPokemonByType(char type[], char type2[], Pokemon pokemon[], int n, Pokemon result[], int &m )
