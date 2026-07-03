#include<iostream>
#include<cstring>
using namespace std;

struct Pokemon{
	char pokeID[10];
 	char pokeName[30];
	char type1[25];
	char type2[25];
	int speed;
};

void printPokemon(Pokemon pokemons[], int n) {
	int maxSpeed=-1, maxID;
	for(int i=0; i<n; i++) {
		if(pokemons[i].speed>maxSpeed) {
			maxSpeed=pokemons[i].speed;
			maxID=i+1;
		}
	}
	cout << "ID: " << pokemons[maxID].pokeID << "\n";
	cout << "Pokemon name: " << pokemons[maxID].pokeName << "\n";
	cout << "Type: " << pokemons[maxID].type1 << ", " << pokemons[maxID].type2 << "\n";
	cout << "Speed: " << pokemons[maxID].speed << endl;
}

void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n,
Pokemon result[], int& m) {
	m=0;
	for(int i=0; i<n; i++) {
		if(type1==NULL) {
			if(!strcmp(type2, pokemons[i].type1) || !strcmp(type2, pokemons[i].type2) ) {
				result[m++]=pokemons[i];
			}
		}
		if(type1!=NULL && type2!=NULL) {
			if((!strcmp(type1, pokemons[i].type1) && !strcmp(type2, pokemons[i].type2) ) || (!strcmp(type2, pokemons[i].type1) && !strcmp(type1, pokemons[i].type2) )) {
				result[m++]=pokemons[i];
			}
		}
		if(type2==NULL) {
			if(!strcmp(type1, pokemons[i].type1) || !strcmp(type1, pokemons[i].type2) ) {
				result[m++]=pokemons[i];
			}
		}
	}
}

int main() {
	Pokemon pokemons[100];
	int n;
	cout << "Nhap n: ";
	cin >> n;
	for(int i=0; i<n; i++) {
		cin.ignore();
		cout << "Nhap ID: ";
		cin.getline(pokemons[i].pokeID, 10);
		cout << "Nhapten: ";
		cin.getline(pokemons[i].pokeName, 30);
		cout << "Nhaploai1: ";
		cin.getline(pokemons[i].type1, 25);
		cout << "Nhaploai2: ";
		cin.getline(pokemons[i].type2, 25);
		cout << "Speed: ";
		cin >> pokemons[i].speed;
	}
	printPokemon(pokemons, n);
	return 0;
}
