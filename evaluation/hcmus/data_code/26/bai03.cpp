#include <iostream>
#include <fstream>
#include <cstring>
#include <stdlib.h>
using namespace std;

struct Pokemon{
	char pokeID[10];
	char pokeName[30];
	char type1[25];
	char type2[25];
	int speed;
};
//3.1
void ReadFile(char fileName[], Pokemon pokemons[], int &n)
{

}
//3.2
void printPokemon(Pokemon pokemons[], int n){
	int max=1;
	int pos=0;
	for (int i=0;i<=n-1;i++)
	{
		if(pokemons[i].speed>max)
		max=pokemons[i].speed;
		pos=i;
	}
		cout << "ID: "<< pokemons[pos].pokeID<< endl << "Pokemon name: "<< pokemons[pos].pokeName <<endl<< "Type: "<< pokemons[pos].type1 << ","<<pokemons[pos].type2<<endl<<"Speed: "<<pokemons[pos].speed;
}
//3.3
void searchPokemonByType(char type1[],char type2[], Pokemon pokemons[], int n, Pokemon result[], int &m)
{
	
}
int main()
{
	Pokemon pokemons[10];
	int n;
	//ReadFile(pokemon.txt,Pokemon pokemons,)
	cout << "Pokemon with max speed: "<< endl;
	printPokemon(pokemons,n);
	return 0;
}
