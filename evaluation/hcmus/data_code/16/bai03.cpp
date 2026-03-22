#include <iostream>
#include <fstream>
#include <cstring>
using namespace std;
const int SIZE = 100;

struct Pokemon
{
    char pokeID[31];
    char pokeName[31];
    char type1[26];
    char type2[26];
    int speed;
};

void ReadFile(char filename[], Pokemon pokemons[], int &n)
{
    ifstream fin;
    fin.open(filename);

    char s[SIZE];

    int intID, speed, countPoke = 0;
    fin.getline(s,100);

    while (!fin.eof())
    {
        fin.getline(pokemons[countPoke].pokeID,SIZE,',');
        fin.getline(pokemons[countPoke].pokeName,SIZE,',');
        fin.getline(pokemons[countPoke].type1,SIZE,',');
        fin.getline(pokemons[countPoke].type2,SIZE,',');
        if (strcmp(pokemons[countPoke].type2,"NULL") == 0) pokemons[countPoke].type2[0] = '\0';
        fin >> pokemons[countPoke].speed;
        fin.ignore();
        countPoke++;
    }
    fin.close();
    n = countPoke;
}

Pokemon findFastesPoke(Pokemon pokemons[], int countPoke)
{
    int speedmax = pokemons[0].speed, IDpoke = 0;
    for (int i = 1; i < countPoke; ++i)
    {
        if (pokemons[i].speed > speedmax)
        {
            speedmax = pokemons[i].speed;
            IDpoke = i;
        }
    }
    return pokemons[IDpoke];
}

void printArrayPokemon(Pokemon pokemons[], int n)
{
    for (int i = 0; i < n; ++i)
    {
        cout << "ID: " << pokemons[i].pokeID << '\n';
        cout << "Pokemon name: " << pokemons[i].pokeName;
        if (pokemons[i].type2[0] != '\0')
            cout << "Type: " << pokemons[i].type1 << ", " << pokemons[i].type2 <<'\n';
        else
            cout <<  "Type: " << pokemons[i].type1 <<'\n';
        cout << "Speed: " << pokemons[i].speed;
    }

}

void printPokemon(Pokemon pokemons)
{

        cout << "ID: " << pokemons.pokeID << '\n';
        cout << "Pokemon name: " << pokemons.pokeName;
        if (pokemons.type2[0] != '\0')
            cout << "Type: " << pokemons.type1 << ", " << pokemons.type2 <<'\n';
        else
            cout <<  "Type: " << pokemons.type1 <<'\n';
        cout << "Speed: " << pokemons.speed;

}

void findType(Pokemon poke[], int n, char Type[])
{
    int arr_Type[SIZE],  nType = 0;
    for (int i = 0; i < n; ++i)
    {
        if (strcmp(poke[i].type1,Type) == 0 ||strcmp(poke[i].type2,Type) == 0)
        {
            arr_Type[nType] = i;
            nType++;
        }
    }

    if (nType != 0)
    {
        cout << "The list of Pokemon with Type = " << Type <<'\n';

        for (int i = 0; i < nType - 1; ++i)
        {
            cout << "ID: " << poke[arr_Type[i]].pokeID << " - Name: " << poke[arr_Type[i]].pokeName << '\n';
        }
        cout << "ID: " << poke[arr_Type[nType - 1]].pokeID << " - Name: " << poke[arr_Type[nType - 1]].pokeName;
    }
}

int main()
{
    int countPoke = 0;
    Pokemon arr[SIZE];
    ReadFile("pokemon.txt", arr, countPoke);
    printPokemon(findFastesPoke(arr, countPoke));

    char type[SIZE];
    cout << "\n\nInput Type: ";
    cin >> type;
    findType(arr, countPoke, type);
    return 0;
}

