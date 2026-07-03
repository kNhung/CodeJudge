#include <iostream>
#include <cstring>
#include <fstream>

using namespace std;

struct Pokemon{
	string pokeID;
	string pokeName;
	string type1;
	string type2;
	int speed;
};

void readFile(char filename[], Pokemon pokemons[], int &n){
	
}

void xuli(string line){
	
}

void printPokemon(Pokemon pokemons[], int n){
	int max = -1000000;
	int idx;
	for(int i = 0; i < n; i++){
		if(max < pokemon[i].speed){
			max = pokemon[i].speed;
			idx = i;
		}		
	}
	cout << "ID: " << pokemons[idx].pokeID;
	cout << endl;
	cout << "Pokemon name: " << pokemons[idx].pokeName;
	cout << endl;
	cout << "Type: " << pokemons[idx].type1 << "," << pokemons[idx].type2;
	cout << endl;
	cout << "Speed: "<< pokemons[idx].speed << endl;
}
int main(){
	fstream fs;
	Pokemon poke[100]
	fs.open("pokemon.txt", ios::in);
	if(!fs){
		cout << "MO KHONG THANH CONG";
		return 1;
	}
	string line
	string temp;
	fs >> temp;
	int n = 0;
	while(!fs.eof()){
		fs >> line;
		line.c_str();
		readFile(line,poke[n],int n);
		
		
		
		
	}
}
