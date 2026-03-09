#include <iostream>
#include <cmath>
#include <fstream>
#include <string>
using namespace std;

struct Pokemon{
		int pokeID;
		string pokeName;
		string type1;
		string type2;
		int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n){

	fstream fi, fo;
	fi.open("pokemon.txt", ios::in);
	fo.open("pokemon.txt", ios::app);
	if(!fi){
		cout<<"can not open";
	}
		
	string line[1000];
	int i = 0;
	while(getline(fi,line[i])){
		i++;
		fo<<line[i]<<" ";
	}
	fi.close();
}

void printPokemon(Pokemon pokemons[], int n){
	int max = pokemons[0].speed;
	for(int i=0; i<n; i++){
		if(pokemons[i].speed > max) max = pokemons[i].speed;
	}
	if (max == pokemons[i].speed) fo<< pokemons[i].speed;
}

int main(){
	int n;
	cin>>n;
	Pokemon pokemons[n];
	ReadFile("pokemon.txt", pokemons, n);
	printPokemon(pokemons,n);
	
	
	
	return 0;
}
