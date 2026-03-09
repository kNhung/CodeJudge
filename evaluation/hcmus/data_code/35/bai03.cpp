#include <iostream>
#include <fstream>
#include <cstring>
#include <string>
using namespace std ;
struct Pokemon
{
    char pokeID [10];
    char pokeName[100];
    char type1[100];
    char type2[100];
    int speed;
};
void ReadFile(char fileName[][100], Pokemon pokemons[], int &n)
{
    char *pch;
    char tmp[100];
    int k;
    ifstream infile;
    infile.open("pokemon.txt");
    if (infile.is_open())
        cout << "Cannot open file!!" ;
    else
        while (!infile.eof())
        {
            infile.getline(fileName[n],100);
            n++;
        }
    for (int i=0 ; i<n ; i++)
    {
        pch=strtok(fileName[i],',')
        while (pch!=NULL)
        {
            strcpy(tmp,pch);
            pch=strtok(fileName[i],',');
        }


    }
    int k,j=0;

}
void printPokemon(Pokemon pokemons[],int n)
{
    int maxspeed=0;
    Pokemon pokemaxspeed;
    for(int i=0 ; i<n ; i++)
        if(pokemons[i].speed>maxspeed)
        {
            maxspeed=pokemons[i].speed;
            strcpy(pokemaxspeed.pokeID,pokemons[i].pokeID);
            strcpy(pokemaxspeed.pokeName,pokemons[i].pokeName);
            strcpy(pokemaxspeed.type1,pokemons[i].type1);
            strcpy(pokemaxspeed.type2,pokemons[i].type2);
        }
    cout << "ID: " << pokemaxspeed.pokeID << "\n" ;
    cout << "Pokemon name: " << pokemaxspeed.pokeName << "\n" ;
    cout << "Pokemon type: " ;
    if(pokemaxspeed.type1==NULL)
        cout << "\0" ;
    else
        cout << pokemaxspeed.type1 << " " ;
    if(pokemaxspeed.type2==NULL)
        cout << "\n" ;
    else
        cout << pokemaxspeed.type2 << "\n" ;
    cout << "Speed: " << maxspeed << "\n" ;
}
int main()
{
    Pokemon pokemons[100];
    char fileName[100][100] ;
    int n;

    return 0;
}
