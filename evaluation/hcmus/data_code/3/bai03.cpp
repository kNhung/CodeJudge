#include <iostream>
#include <cmath>
#include <string>
#include <cstdlib>
#include <fstream>

using namespace std;

struct Pokemon{
	string pokeID;
	string pokeName;
	string type1;
	string type2;
	int speed;
};

void printPokemon(Pokemon pokemons[], int n){
	cout << "ID: " << pokemons[n].pokeID << endl;
	cout << "Pokemon name: " << pokemons[n].pokeName << endl;
	cout << "Type: " << pokemons[n].type1;
	if (pokemons[n].type2 != "NULL") cout << ", " << pokemons[n].type2;
	cout << endl << "Speed: " << pokemons[n].speed << endl;
}

int findMaxSpeed(Pokemon pokemons[], int n){
	int max = pokemons[0].speed;
	int pos = 0;
	for (int i = 0; i < n; i++){
		if (pokemons[i].speed > max) {
			max = pokemons[i].speed;
			pos = i;
		}
	}
	return pos;
}

void searchPokemonByType(string type1, string type2, Pokemon pokemons[], int n, Pokemon result[], int& m){
	for (int i = 0; i < n; i++){
		if (type2 == "NULL"){
			if (type1 == pokemons[i].type1 || type2 == pokemons[i].type2){
				result[m] = pokemons[i];
				m++;
			}
		}
		else{
			if (type1 == pokemons[i].type1 && type2 == pokemons[i].type2){
				result[m] = pokemons[i];
				m++;
			}
		}
	}
}
//
//void ReadFile(char fileName[], Pokemon pokemons[], int &n){
//	ifstream fi("pokemon.txt");
//	cin.ignore();
//	int i = 0;
//	Pokemon temp;
//	string temp1;
//	temp1 = fi.getline(',');
//	/*while (!fi.eof()){
//		Pokemon temp;
//		fi.getline()
//	}*/
//	fi.close();
//}

void Default(Pokemon pokemons[], int &n){
	int i = 0;
	pokemons[i].pokeID = "1";
	pokemons[i].pokeName = "Bulbasaur";
	pokemons[i].type1 = "Grass";
	pokemons[i].type2 = "Poison";
	pokemons[i].speed = 100;

	pokemons[i++].pokeID = "7";
	pokemons[i++].pokeName = "Squirtle";
	pokemons[i++].type1 = "Water";
	pokemons[i++].type2 = "NULL";
	pokemons[i++].speed = 44;

	pokemons[i++].pokeID = "8";
	pokemons[i++].pokeName = "Wartortle";
	pokemons[i++].type1 = "Water";
	pokemons[i++].type2 = "NULL";
	pokemons[i++].speed = 59;
	n = i + 1;
}

int main(){
	int n;
	Pokemon pokemons[100];
	Default(pokemons, n);
	cout << "Pokemon with max speed: " << endl;
	printPokemon(pokemons, findMaxSpeed(pokemons, n));

	string s, type1, type2;
	//type1 = NULL;
	//type2 = NULL;
	bool duelType = false;
	cout << "Input Type: ";
	cin >> s;
	for (int i = 0; i < s.size(); i++){
		if (s[i] == ',') duelType = true;
		else {
			type1 = s;
			type2 = "NULL";
		}
	}
	int i = 0;
	if (duelType == 1){
		while (s[i] != ','){
			type1[i] = s[i];
			i++;
		}
		int i = type1.size() + 1;
		while (s[i] != '\0'){
			type2 += s[i];
			i++;
		}
	}
	Pokemon result[100];
	int m = 0;
	searchPokemonByType(type1, type2, pokemons, n, result, m);
	cout << "The list of Pokemon with Type = " << type1;
	if (type2 != "NULL") cout << "/" << type2;
	cout << ":" << endl;
	for (int i = 0; i < m; i++){
		cout << "ID: " << result[i].pokeID << " - Name: " << result[i].pokeName << endl;
	}
	system("pause");
	return 0;
}