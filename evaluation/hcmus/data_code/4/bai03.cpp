#include<iostream>
#include<fstream>
#include<string>
using namespace std;

struct Pokemon{
    string pokeID[10];
    string pokeName[30];
    string type1[25];
    string type2[25];
    int speed;
};

void doc_thong_tin_pokemon(ifstream &fileIn, Pokemon &poke)
{
    getline(fileIn,poke.pokeID,',');
    getline(fileIn,poke.pokeName,',');
    getline(fileIn,poke.type1,',');
    getline(fileIn,poke.type2,',');
    fileIn << poke.speed;
}
int main()
{
    ifstream fileIn;
    fileIn.open("pokemon.txt");
    Pokemon poke[];
    doc_thong_tin_pokemon(fileIn, poke);
    xuatthongtin(poke);
    fileIn.close();
}
