#include <iostream>
#include <fstream>
#include <cstring>
using namespace std;

struct Pokemon{
	char pokeID[10];
	char pokeName[30];
	char type1[25];
	char type2[25];
	int speed;
};

void ReadFile(Pokemon pokemons[], int &n){
	char ignore[100];
	ifstream ifs;
	ifs.open("Pokemon.txt");
	ifs.getline(ignore, 100, '\n');
	for (int i = 0; i < n; i++){
		ifs.getline(pokemons[i].pokeID, 10, ',');
		ifs.getline(pokemons[i].pokeName, 30, ',');
		ifs.getline(pokemons[i].type1, 25, ',');
		ifs.getline(pokemons[i].type2, 25, ',');
		ifs >> pokemons[i].speed;
		ifs.getline(ignore, 1);
	}
	ifs.close();
}

int printPokemon(Pokemon pokemons[], int n){
	int temp = 0, max = pokemons[0].speed;
	for (int i = 1; i < n; i++){
		int check = pokemons[i].speed;
		if (check > max){
			temp = i;
			max = check;
		}
	}
	return temp;
}

void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int& m){
	for (int i = 0; i < n; i++){
		if (strcmp("NULL", type2) == 0){
			if (strcmp(type1, pokemons[i].type1) == 0 or strcmp(type1, pokemons[i].type2) == 0){
				result[m] = pokemons[i];
				m++;
			}
		} else if ((strcmp(type1, pokemons[i].type1) == 0 and strcmp(type2, pokemons[i].type2) == 0) or strcmp(type2, pokemons[i].type1) == 0 and strcmp(type1, pokemons[i].type2) == 0){
			result[m] = pokemons[i];
			m++;
		}
	}
}

int main(void){
	Pokemon pokemons[10], result[10];
	int n = 8, m = 0, temp;
	char type1[50], type2[50];
	ReadFile(pokemons, n);
	temp = printPokemon(pokemons, n);
	cout << "Pokemon with max speed: " << endl;
	cout << "ID: " << pokemons[temp].pokeID << endl;
	cout << "Pokemon name: " << pokemons[temp].pokeName << endl;
	cout << "Type: " << pokemons[temp].type1 << ", " << pokemons[temp].type2 << endl;
	cout << "Speed: " << pokemons[temp].speed << endl;
	cout << "Input Type 1: ";
	cin.getline(type1, 50);
	cout << "Input Type 2: ";
	cin.getline(type2, 50);
	cout << "The list of Pokemon with Type1, Type2 = " << type1 << " and " << type2 << ": " << endl;
	searchPokemonByType(type1, type2, pokemons, n, result, m);
	for (int i = 0; i < m; i++){
		cout << "ID: " << result[i].pokeID << " - Name: " << result[i].pokeName << endl;
	}
}
