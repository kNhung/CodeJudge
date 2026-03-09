#include <iostream>
#include <string>
#include <fstream>
using namespace std;

struct Pokemon{
char pokeID[11];
char pokeName[31];
char type1[26];
char type2[26];
int speed;
};
void ReadFile (char fileName[], Pokemon pokemons[], int &n)
{ ifstream FileIn;
  FileIn.open("pokemon.txt",ios_base::in);
  if(FileIn.is_open()==true)
  
  FileIn.close();

  
}
int main()
{ 
 return 0;
}
 Cau 3.3
void printPokemon(Pokemon pokemons[], int n)
{ for(int i = 0; i < n-1; i++)
   for(int j = i+1; j < n ; j++)
     if(pokemons[i].speed < pokemons[j].speed)
      {int temp = pokemons[i].speed;
         pokemons[i] = pokenmons[j];
         pokemons[j] = temp;
       }
  cout << "Pokemon with max speed: ";
  cout << "ID: " << pokemons[0].pokeID;
  cout << " Pokemon name" << pokemons[0].pokeName;
  cout << "Type" << pokemons[0].type1 << "," <<pokemons[0].type2; 
  cout << " Speed: " << speed;
}





