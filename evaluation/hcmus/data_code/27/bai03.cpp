#include <iostream>
#include <fstream>
#include <string>
#include <cstring>

using namespace std;

struct Pokemon{
    char pokeID[11];
    char pokeName[31];
    char type1[26];
    char type2[26];
    int speed;
};

void inputPokemon(Pokemon &p, char id[11], char pokeName[31], char type1[26],char type2[26],int speed) {
    int i;
    for (i = 0; id[i]; i++) {
        p.pokeID[i] = id[i];
    }
    p.pokeName[i] = '\0';

    for (i = 0; pokeName[i]; i++) {
        p.pokeName[i] = pokeName[i];
    }
    p.pokeName[i] = '\0';

    for (i = 0; type1[i]; i++) {
        p.type1[i] = type1[i];
    }
    p.type1[i] = '\0';

    for (i = 0; type2[i]; i++) {
        p.type2[i] = type2[i];
    }
    p.type2[i] = '\0';

    p.speed = speed;
}

void ReadFile(char fileName[], Pokemon pokemons[], int &n) {
    ifstream in(fileName, ifstream::in);
    string temp;
    n = 0;
    if (!in.is_open()) {
        n = 3;
        inputPokemon(pokemons[0], "1", "Bulbasaur", "Grass", "Poison", 100);
        inputPokemon(pokemons[1], "7", "Squirtle", "Water", "NULL", 44);
        inputPokemon(pokemons[2], "8", "Wartortle", "Water", "NULL", 59);
    }
    while (getline(in, temp)) {
        string temp2;
    }
    if (n == 0) {
        n = 3;
        inputPokemon(pokemons[0], "1", "Bulbasaur", "Grass", "Poison", 100);
        inputPokemon(pokemons[1], "7", "Squirtle", "Water", "NULL", 44);
        inputPokemon(pokemons[2], "8", "Wartortle", "Water", "NULL", 59);
    }
}

bool isSameString(char in1[], char in2[]) {
    for (int i = 0; in1[i]; i++) {
        if (in2[i] != in1[i]) return false;
    }
    return true;
}

bool isNull(char types[]) {
    char n[] = "NULL";
    return isSameString(types, n);
}

void printPokemonInfo(Pokemon &p) {
    cout << "ID: " << p.pokeID << "\n";
    cout << "Pokemon name: " << p.pokeName << "\n";
    cout << "Type : " << p.type1;
    if (!isNull(p.type2)) {
        cout << ", " << p.type2;
    }
    cout << "\n";
    cout << "Speed: " << p.speed << "\n";
}

void printPokemon(Pokemon pokemons[], int n) {
    int Max = 0;
    for (int i = 1; i < n; i++) {
        if (pokemons[i].speed > pokemons[Max].speed) {
            Max = i;
        }
    }
    printPokemonInfo(pokemons[Max]);
}

void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int& m) {
    m = 0;
    for (int i = 0; i < n; i++) {
        if (isNull(pokemons[i].type2)) {
            if ((isSameString(pokemons[i].type1, type1) && isSameString(pokemons[i].type2, type2)) || (isSameString(pokemons[i].type1, type2) && isSameString(pokemons[i].type2, type1))) {
                result[m++] = pokemons[i];
            }
        } else {
            if (isSameString(pokemons[i].type1, type1) || isSameString(pokemons[i].type1, type2)) {
                result[m++] = pokemons[i];
            }
        }
    }
}

int main() {
    Pokemon pokemons[100];
    int n;
    ReadFile("../pokemon.txt", pokemons, n);
    cout << "Pokemon with max speed: \n";
    printPokemon(pokemons, n);
    Pokemon result[100];
    cout << "Input type: ";
    char type1[26];
    cin.getline(type1, 30);
    int m = 0;
    searchPokemonByType(type1, "NULL", pokemons, n, result, m);
    cout << "The list of Pokemon with Type = " << type1 << endl;
    for (int i = 0; i < m; i++) {
         cout << "ID: " << result[i].pokeID << " - Name: " << result[i].pokeName << endl;
    }
    return 0;
}

