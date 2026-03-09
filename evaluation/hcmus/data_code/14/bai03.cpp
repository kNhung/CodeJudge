#include<iostream>
#include<fstream>
#include<cstring>
#include<stdlib.h>
using namespace std;
const int Max = 100;
struct Pokemon
{
	char pokeID[10];
	char pokename[30];
	char type1[25], type2[25];
	int speed;
};
/*Bai 3.1
void ReadFile(char fileName[], Pokemon pokemons[], int &n)
{	
}*/

//Bai 3.2
Pokemon findPokemon(Pokemon pokemons[], int n)
{
	int max = pokemons[0].speed, pos = 0;
	for (int i = 0; i < n; i++) 
		if (pokemons[i].speed > max)
		{
			pos = i;
			max = pokemons[i].speed;
		}
	return pokemons[pos];
}

//Bai 3.3
void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int& m)
{
	m = 0;
	for (int i = 0; i < n; i ++)
	{
		if(type1 == NULL || strcmp(pokemons[i].type1, type1))
		if(type2 == NULL || strcmp(pokemons[i].type2,type2 )) 
		{
			m ++;
			result[m --] = pokemons[i];
		}
	}
}

int main()
{
	Pokemon pokemons[Max], result[Max];
	int n, m;
	cout<<"Number of pokemons : ";
	cin>> n;
	Pokemon max = findPokemon(pokemons, n);
	cout<<"Pokemon with max speed"<< endl;
	cout<<"ID: "<<max.pokeID<< endl;
	cout<<"Pokemon name: "<<max.pokename <<endl;
	cout<<"Type: "<<max.type1;
	if(max.type2 != NULL) cout <<","<<max.type2<<endl;
	cout<<"Speed: "<<max.speed<<endl;
	
	char type1[100];
	char type2[100];
	cout<<"Input type: ";
	cin.ignore();
	cin.getline(type1, 100);
	cout<<"Input type: ";
	cin.ignore();
	cin.getline(type2, 100);
	cout<<"The list of Pokemon with type : ";
	cout<<type1;
	if(max.type2 != NULL) cout <<","<<type2<<endl;
	for (int i = 0; i < m; i ++)
		cout<<"ID: "<<result[i].pokeID<<" - Name : "<<result[i].pokename;
	return 0;
}
