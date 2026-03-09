#include <iostream>
#include <fstream>
#include <cstring>
using namespace std;
struct Pokemon {
	char pokeID[15];
	char pokeName[35];
	char type1[35];
	char type2[35];
	int speed;
};
void ReadFile(char fileName[], Pokemon pokemons[], int &n) {
	ifstream FileIn;
	FileIn.open("pokemon.txt");
	if (!FileIn.is_open()) {
		cout << "Khong mo duoc file";
	} else {
		string s;
		cin >> s;
		char a[256][256];
		char b[256];
		char *pch;
		while (FileIn.eof()) {
			cin >> a[i++];
			pch = strtok(a, ',');
			pokemons[i].pokeID = pch;
			while (pch != NULL) {
				pch = strtok(pch, NULL);
				pokemons[i].pokeName = pch;
				pch = strtok(pch, NULL);
				pokemons[i].type1 = pch;
				pch = strtok(pch, NULL);
				pokemons[i].type2 = pch;
				pch = strtok(pch, NULL);
			}
			i++;
			}
		}
	}
}
void printPokemon(Pokemon pokemons[], int n) {
	int m = pokemons[0].speed;
	for (int i = 0; i < n; i++) {
		if (pokemons[i].speed > m) {
			m = pokemons[i].speed;
		}
	}
	for (int i = 0; i < n; i++) {
		if (pokemons[i].speed == m) {
			cout << "ID: "<<pokemons[i].pokeID<<endl;
			cout << "Pokemon name: "<<pokemons[i].pokeName<<endl;
			cout << "Type: "<<pokemons[i].type1 << ", ";
			cout << pokemons[i].type2<<endl;
			cout << "Speed: "pokemons[i].speed<<endl;
		}
	}
}
int main() {
	
}
