#include <iostream>
#include <cmath>
#include <string>
#include <cstring>
#include <cstdlib>
#include <stdlib.h>
#include <fstream>
using namespace std;
struct Pokemon{
	char pokeID[10];
	char pokeName[30];
	char type1[25];
	char type2[25];
	int speed;
};
void ReadFile(char fileName[], Pokemon pokemons[], int &n){
	char ch = strtok (pokemon," ,");
	
	
	
	
}



int main(){
	Pokemon pokemons[100];
	int n = 10;
	
	ifstream inFile;
	inFile.open("pokemon.txt");
	char ch;
	char pokemon[10000];
	int i = 0;
	while (inFile.get(ch)){
		pokemon[i] = ch;
		cout <<pokemon[i];
		i++;
		
	}
	ReadFile (pokemon , pokemons , i);
	inFile.close();
	
	return 0;
}
