#include <iostream>
#include <fstream>
#include <cstring>

using namespace std;

struct Pokemon{
	char pokeID[10];
	char pokeName[30];
	char type1[25];
	char type2[25];
	int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n);

int main ()
{
	int n;
	Pokemon a[100];
	char filename[100];
	cin >> filename;
	cin.ignore();
	ReadFile(filename, a,n);
	cout << a[1].pokeName << cout << a[2].pokeName;
}
void ReadFile(char fileName[], Pokemon pokemons[], int &n)
{
	int i = 0;
	n = 0;
	char ch[100];
	ifstream fin;
	fin.open(fileName);
	fin.getline(ch, 100 ,',');
	while (pokemons.speed != '')
	{
		fin.getline(pokemons[i].pokeID,100,',');
		fin.getline(pokemons[i].pokeName,100,',');
		fin.getline(pokemons[i].type1,100,',');
		fin.getline(pokemon[i].type2,100,'\n');
		fin >> pokemons.speed;
	}
	
}
