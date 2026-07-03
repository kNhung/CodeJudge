#include<iostream>
#include<string>
#include<cstring>
#include<fstream>
#include<cmath>
using namespace std;

struct Pokemon{
	string pokeID;
	string pokeName;
	string type1;
	string type2;
	int speed;
};

//void ReadFile(char fileName[], Pokemon pokemons[], int &n){
//	ifstream fin("fileName");
//	n++;
//	while(!fin.eof()){
//		fin.getline(pokemons[n-1].pokeID, ',');
//		strtok(pokemons[n-1].pokeName, ',');
//		strtok(pokemons[n-1].type1, ',');
//		strtok(pokemons[n-1].type2, ',');
//		fin >> pokemons[n-1].speed;
//	}
//	
//}

void printPokemon(Pokemon pokemons[], int n){
	int highest = pokemons[0].speed;
	int index;
	for (int i = 0; i < n; i++){
		if(pokemons[i].speed > highest){
			highest = pokemons[i].speed;
			index = i;
		}
	}
	cout << "ID: " << pokemons[index].pokeID << '\n';
	cout << "Pokemon name: " << pokemons[index].pokeName << '\n';
	if (pokemons[index].type1 != "NULL" && pokemons[index].type2 != "NULL")
		cout << "Type: " << pokemons[index].type1 << ", " << pokemons[index].type2 << '\n';
	else if (pokemons[index].type1 == "NULL")
		cout << "Type: " << pokemons[index].type2 << '\n';
	else if (pokemons[index].type2 == "NULL")
		cout << "Type: " << pokemons[index].type1 << '\n';
	cout << "Speed: " << pokemons[index].speed << '\n';
}

void searchPokemonByType(string type1, string type2, Pokemon pokemons[], int n, Pokemon result[], int& m){
	m++;
	if(type1 == "NULL"){
		for (int i = 0; i < n; i++)
			if (pokemons[i].type1 == type2 || pokemons[i].type2 == type2){
				result[m-1] = pokemons[i];
				m++;
			}
	}
	else if (type2 == "NULL"){
		for (int i = 0; i < n; i++)
			if (pokemons[i].type1 == type1 && pokemons[i].type2 == type1){
				result[m-1] = pokemons[i];
				m++;
			}
	}
	else {
		for (int i = 0; i < n; i++)
			if (pokemons[i].type1 == type1 && pokemons[i].type2 == type2 || pokemons[i].type1 == type2 && pokemons[i].type2 == type1)
			{
				result[m-1] = pokemons[i];
				m++;
			}
	}
}

void generate(Pokemon pokemons[]){
	pokemons[0].pokeID = "1";
	pokemons[0].pokeName = "Bulbasaur";
	pokemons[0].type1 = "Grass";
	pokemons[0].type2 = "Poison";
	pokemons[0].speed = 100;
	
	pokemons[1].pokeID = "7";
	pokemons[1].pokeName = "Squirtle";
	pokemons[1].type1 = "Water";
	pokemons[1].type2 = "NULL";
	pokemons[1].speed = 44;
	
	pokemons[2].pokeID = "8";
	pokemons[2].pokeName = "Wartortle";
	pokemons[2].type1 = "Water";
	pokemons[2].type2 = "NULL";
	pokemons[2].speed = 59;
}

int main(){
	int n = 3;
	Pokemon pokemons[n];
	generate(pokemons);
	printPokemon(pokemons, n);
	cout << '\n';
	
//	int m = 0;
//	Pokemon result[100];
//	cout << "Input Type: ";
//	string type1, type2;
//	cin.ignore();
//	cin >> type1 >> type2;
//	searchPokemonByType(type1, type2, pokemons, n, result, m);
//
//	if (type1 != "NULL" && type1 != "NULL")
//		cout << "The list of Pokemon with Type = " << type1 << ", " << type2 << '\n';
//	else if (type1 == "NULL")
//		cout << "The list of Pokemon with Type = " << type2 << '\n';
//	else if (type2 == "NULL")
//		cout << "The list of Pokemon with Type = " << type1 << '\n';
//	
//	for (int i = 0; i < m; i++) cout << "ID: " << result[i].pokeID << " - Name: " << result[i].pokeName << '\n'; 	
	
	return 0;
}
