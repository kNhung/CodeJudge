#include <iostream>
#include <fstream>
#include <string>

using namespace std;

const int MAX_POKEMONS = 100;

struct Pokemon {
    string pokeID;
    string pokeName;
    string type1;
    string type2;
    int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n) {
    ifstream file(fileName);
    if (!file.is_open()) {
        cout << "Khong the mo file." << endl;
        return;
    }
    
    n = 0;
    
    while (!file.eof() && n < MAX_POKEMONS) {
        Pokemon pokemon;
        
        getline(file, pokemon.pokeID);
        getline(file, pokemon.pokeName);
        getline(file, pokemon.type1);
        getline(file, pokemon.type2);
        file >> pokemon.speed;
        file.ignore(); 
        
        pokemons[n] = pokemon;
        n++;
    }
    
    file.close();
}

int main() {
    char fileName[] = "pokemon.txt";
    Pokemon pokemons[MAX_POKEMONS];
    int numPokemons = 0;
    
    ReadFile(fileName, pokemons, numPokemons);
    
    
    for (int i = 0; i < numPokemons; i++) {
        cout << "Pokemon " << i+1 << ":" << endl;
        cout << "ID: " << pokemons[i].pokeID << endl;
        cout << "Name: " << pokemons[i].pokeName << endl;
        cout << "Type 1: " << pokemons[i].type1 << endl;
        cout << "Type 2: " << pokemons[i].type2 << endl;
        cout << "Speed: " << pokemons[i].speed << endl;
        cout << endl;
    }
    
    return 0;
}
