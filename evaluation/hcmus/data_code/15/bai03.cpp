#include <iostream>
#include <cstring>
#include <fstream>

using namespace std;

struct Pokemon
{
    char pokeID[11];
    char pokeName[31];
    char type1[26];
    char type2[26];
    int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n);
void printPokemon(Pokemon pokemons[], int n);
void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int& m);



int main()
{

    //3.1

    Pokemon pokemons[100];
    int n = 0;

    ReadFile("pokemon.txt", pokemons, n);



    //3.2

    printPokemon(pokemons, n);
    cout << endl;



    //3.3

    char type1[26], type2[26];

    cout << "Input type1: ";
    cin.getline(type1, 26);

    cout << "Input type2: ";
    cin.getline(type2, 26);

    Pokemon result[100];
    int m = 0;

    searchPokemonByType(type1, type2, pokemons, n, result, m);

    if(strcmp(type1, "NULL") == 0) cout << "The list of Pokemon with Type = " << type2 << ":\n";
    else if (strcmp(type2, "NULL") == 0) cout << "The list of Pokemon with Type = " << type1 << ":\n";
    else cout << "The list of Pokemon with Type = " << type1 << " + " << type2 << ":\n";

    for(int i = 0; i < m; i++)
        cout << "ID: " << result[i].pokeID << " ~ " << "Name: " << result[i].pokeName << "\n";

    return 0;



}



void ReadFile(char fileName[], Pokemon pokemons[], int &n)
{
    ifstream fin(fileName);
    if(!fin) return;

    char skip[1000];
    fin.getline(skip, 1000);

    while(!fin.eof())
    {
        fin.getline(pokemons[n].pokeID, 11, ',');
        if(strlen(pokemons[n].pokeID) == 0) continue;
        fin.getline(pokemons[n].pokeName, 31, ',');
        fin.getline(pokemons[n].type1, 26, ',');
        fin.getline(pokemons[n].type2, 26, ',');
        fin >> pokemons[n].speed;
        fin.ignore();
        n++;
    }

    fin.close();
}



void printPokemon(Pokemon pokemons[], int n)
{
    int max_speed = 0;
    for(int i = 0; i < n; i++)
        if(pokemons[i].speed > max_speed) max_speed = pokemons[i].speed;

    cout << "Pokemon with max speed:\n";

    for(int i = 0; i < n; i++)
        if(pokemons[i].speed == max_speed)
        {
            cout << "ID: " << pokemons[i].pokeID << "\n";
            cout << "Pokemon name: " << pokemons[i].pokeName << "\n";
            cout << "Type: " << pokemons[i].type1;
            if(strcmp(pokemons[i].type2, "NULL") == 0) cout << "\n";
            else cout << ", " << pokemons[i].type2 << "\n";
            cout << "Speed: " << pokemons[i].speed << "\n";
        }
}



void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int& m)
{
    if(strcmp(type1, "NULL") == 0 && strcmp(type2, "NULL") == 0) return;
    else if(strcmp(type1, "NULL") == 0)
    {
        for(int i = 0; i < n; i++)
            if(strcmp(pokemons[i].type1, type2) == 0 || strcmp(pokemons[i].type2, type2) == 0)
                result[m++] = pokemons[i];
    }
    else if(strcmp(type2, "NULL") == 0)
    {
        for(int i = 0; i < n; i++)
            if(strcmp(pokemons[i].type1, type1) == 0 || strcmp(pokemons[i].type2, type1) == 0)
                result[m++] = pokemons[i];
    }
    else
    {
        for(int i = 0; i < n; i++)
            if((strcmp(pokemons[i].type1, type1) == 0 && strcmp(pokemons[i].type2, type2) == 0)|| (strcmp(pokemons[i].type1, type2) == 0 && strcmp(pokemons[i].type2, type1) == 0))
                result[m++] = pokemons[i];
    }
}
