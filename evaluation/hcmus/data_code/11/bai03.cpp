#include <iostream>
#include <fstream>

using namespace std;

struct Pokemon{
    char pokeID[10];
    char pokeName[30];
    char type1[25];
    char type2[25];
    int speed;
};

void ReadFile(char filename[], Pokemon pokemons[], int &n){
    fstream fin;
    fin.open("pokemon.txt");
    fin >> Pokemon;
}

void
