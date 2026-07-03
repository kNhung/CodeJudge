#include <iostream>
#include <math.h>
#include <cstring>
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

void ReadFile(char fileName[], Pokemon pokemons[], int &n){
	fstream fin;
	int i = 0;
	fin.open(fileName, fstream::in);
	
	if(!fin.is_open()){
		cout << "Khong mo duoc file!";
	}
	fin.ignore(34);
	while(!fin.eof()){
		getline(fin, pokemons[i].pokeID, ',');
		getline(fin, pokemons[i].pokeName, ',');
		getline(fin, pokemons[i].type1, ',');
		getline(fin, pokemons[i].type2,  ',');
		fin >> pokemons[i].speed;
		fin.ignore();
		i++;
	} 
	n = i;
	
	fin.close();
}

/*void inputPokemon(Pokemon pokemons[], int &n){
	for(int i = 0; i < n; i++){
		getline(cin, pokemons[i].pokeID);
		getline(cin, pokemons[i].pokeName);
		getline(cin, pokemons[i].type1);
		getline(cin, pokemons[i].type2);
		cin >> pokemons[i].speed;
		cin.ignore();
	}
}*/

void printPokemon(Pokemon pokemons[], int n){
	cout << "ID: " << pokemons[n].pokeID << endl;
	cout << "Pokemon name: " << pokemons[n].pokeName << endl;
	cout << "Type: " << pokemons[n].type1 << ", " << pokemons[n].type2 << endl;
	cout << "Speed: " << pokemons[n].speed;
}


int main(){
	int n = 0;
	Pokemon pokemons[100];
	//pokemons[0]("1", "Bulbasaur", "Grass", "Poison", 100);
 	//pokemons[1]("7", "Squirtle", "Water", "", 44);
	//pokemons[2]("8", "Wartortle", "Water", "", 59);
	//inputPokemon(pokemons, n);				
	char file[12] = "pokemon.txt";
	ReadFile(file, pokemons, n);
	
	int max = 0;
	int pokemax;
	
	for(int i = 0; i < n; i++){
		if(pokemons[i].speed > max){
			max = pokemons[i].speed;
			pokemax = i;
		}
	}
	cout << "Pokemon with max speed: " << endl;
	printPokemon(pokemons, pokemax);
	
	return 0;
}
