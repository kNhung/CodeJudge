#include <iostream>
#include <string>
#include <fstream>
using namespace std;
struct Pokemon{
    string pokeID;
    string pokeName;
    string type1;
    string type2;
    int speed;
};
void ReadFile(char fileName[], Pokemon pokemons[], int &n){
    fstream fin;
    fin.open(fileName, ios::in);
    if(!fin) cout << "Cannot open file";
    string space;
    getline(fin, space);
    while(!fin.eof()){
        getline(fin, pokemons[n].pokeID, ',');
        getline(fin, pokemons[n].pokeName, ',');
        getline(fin, pokemons[n].type1, ',');
        getline(fin, pokemons[n].type2, ',');
        fin >> pokemons[n].speed;
        fin.ignore();
        n++;
    }
    fin.close();
}

void printPokemon(Pokemon pokemons[], int n){
    int max = 0;
    for (int i = 0; i < n; i++){
        if(pokemons[i].speed > max) max = pokemons[i].speed;
    }
    for (int i = 0; i < n; i++){
        if(pokemons[i].speed == max){
            cout << "ID: " << pokemons[i].pokeID << endl;
            cout << "Pokemon name: " << pokemons[i].pokeName << endl;
            cout << "Type: " << pokemons[i].type1 << ", " << pokemons[i].type2 << endl;
            cout << "Speed: " << pokemons[i].type2 << endl;
        }
    }
}
void searchPokemonByType(string type1, string type2, Pokemon pokemons[], int n, Pokemon result[], int& m){
    for (int i = 0; i < n; i++){
        if ((pokemons[i].type1 == type1 || pokemons[i].type1 == type2) && (pokemons[i].type2 == type1 || pokemons[i].type2 == type2)){
            result[m].pokeID = pokemons[i].pokeID;
            result[m].pokeName = pokemons[i].pokeName;
            m++;
        }
    }
    for (int i = 0; i < m; i++){
        cout << "ID: " << result[i].pokeID << " - Name: " << result[i].pokeName << endl;
    }
}
int main(){
    char fileName[100] = "pokemon.txt";
    Pokemon pokemons[100];
    int n = 0;
    ReadFile(fileName, pokemons, n);
    printPokemon(pokemons, n);
    cout << "Input Type: ";
    string type1;
    cin >> type1;
    cout << "Input Type: ";
    string type2;
    cin >> type2;
    cout << "The list of Pokemon with Type = " << type1 << ", " << type2 << ": " << endl;
    Pokemon result[100];
    int m = 0;
    searchPokemonByType(type1, type2, pokemons, n, result, m);
    return 0;
}
