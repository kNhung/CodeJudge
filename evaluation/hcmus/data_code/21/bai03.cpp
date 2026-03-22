#include <iostream>
#include <cmath>
#include <cstring>
#include <string>
#include <fstream>
using namespace std;
struct Pokemon{
	int speed;
	char pokeName, pokeID;
	char type1, type2;
};

void in(Pokemon &a){
	cin >> a.pokeName, a.pokeID;
	cin.ignore();
	cin >> a.type1 >> a.type2;
	cin >> a.speed;
}

void out(Pokemon &a){
	cout << "ID: " << a.pokeID;
	cout << "Pokemon name: " << a.pokeName;
	cout << "Type: " << a.type1 << "," << a.type2;
}
void ReadFile(char fileName[],char Pokemonpokemons[], int &n){
	ifstream filein;
	filein.open(fileName);
}

//3.2
void printPokemon(char Pokemonpokemons[], int &m){
	int max = Pokemonpokemons[0];
	for (int i = 0; i < m; i++){
		if(Pokemonpokemons[i] > max){
			max = Pokemonpokemons[i]; 
		}
	}
}
int main(){
	ifstream filein;
	filein.open("pokemon.txt",ios_base::in);
	int n,m,a;
	int a[n];
	struct Pokemon a;
	ReadFile(filein ,a, m);
	printPokemon(n,m);
	filein.close();
	return 0;
}
