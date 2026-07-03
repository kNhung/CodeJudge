#include <iostream>
#include <cmath>
#include <cstring>
#include <string>
#include <cstdlib>
#include <fstream>
using namespace std;

struct Pokemon
{
    char pokeID[10];
    char pokeName[30];
    char type1[25];
    char type2[25];
    int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n){
    ifstream ifs;
    ifs.open(fileName);
    char line[100];
    char ds[10][100];
    n = 0;
    ifs.getline(line, 100);
    while (!ifs.eof()){
        ifs.getline(line, 100);
        strcpy(ds[n],line);
        n++;
    }
    ifs.close();
    for (int i = 0; i < n; i++){
        char c[10][50];
        int dem = 0;
        char *pch = strtok(ds[i],",");
        while (pch != NULL){
            strcpy(c[dem],pch);
            dem++;
            pch = strtok(NULL,",");
        }

        strcpy(pokemons[i].pokeID,c[0]);
        strcpy(pokemons[i].pokeName,c[1]);
        strcpy(pokemons[i].type1,c[2]);
        strcpy(pokemons[i].type2,c[3]);
        pokemons[i].speed = atoi(c[4]);
        }
}

void printPokemon(Pokemon pokemons[], int n){
    int maxSpeed=0, pkmIdx;
    for (int i = 0; i < n; i++){
        if (pokemons[i].speed > maxSpeed){
            pkmIdx = i;
        }
    }
    cout << "ID: " << pokemons[pkmIdx].pokeID << endl;
    cout << "Pokemon name: " << pokemons[pkmIdx].pokeName << endl;
    cout << "Type: " << pokemons[pkmIdx].type1 << ", " << pokemons[pkmIdx].type2 << endl;
    cout << "Speed: " << pokemons[pkmIdx].speed << endl;
}


int main(){

    char inputFilePath[] = "pokemon.txt";
    Pokemon pokemons[10];
    int n;
    ReadFile(inputFilePath,pokemons,n);
    printPokemon(pokemons,n);

    return 0;
}

