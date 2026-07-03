#include <iostream>
#include <fstream>
using namespace std;
struct Pokemon {
	char pokeID[10];
	char pokeName[30];
	char type1[25];
	char type2[25];
	int speed;
};

void readFile(char fileName[], Pokemon pokemons[], int &n){
	fstream fs;
	fs.open("pokemon.txt", ios::in);
	bool ans = 1;
	while (!fs.eof()){
		if (ans){
			fs.getline(fileName, 100);
		}
		else {
			fs.getline(pokemons[n].pokeID, 100, ',');
			fs.getline(pokemons[n].pokeName, 100, ',');
			fs.getline(pokemons[n].type1, 100, ',');
			fs.getline(pokemons[n].type2, 100, ',');
			fs >> pokemons[n].speed;
			fs.ignore();
			n++;
		}
		ans = !ans;		
	}
}

void printPokemon(Pokemon pokemons[], int n){
	int index = 0;
	for (int i = 1; i < n; i++){
		if (pokemons[i].speed > pokemons[index].speed) index = i;
	}
    cout << "ID: " << pokemons[index].pokeID << endl;
    cout << "Pokemon name: " << pokemons[index].pokeName << endl;
    cout << "Type: " << pokemons[index].type1 << ", " << pokemons[index].type2 << endl;
    cout << "Speed: " << pokemons[index].speed;
}
int main(){
	Pokemon p[100];
	char fileName[100];
	int n = 0;
	readFile(fileName, p, n);
	printPokemon(p, n);
	return 0;
}
