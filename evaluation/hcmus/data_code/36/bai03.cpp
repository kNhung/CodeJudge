#include<iostream>
#include<fstream>
#include<cstring>
using namespace std;
struct Pokemon{
	int pokeID;
	char pokeName[100];
	char type1[20];
	char type2[20];
	int speed;
};
void ReadFile(char fileName[], Pokemon pokemons[], int &n){
	ifstream fin("pokemon.txt");
	char s[100];
	fin.getline(s, 100);
	while (!fin.eof()){
		fin>>pokemons[n].pokeID;
		fin.get();
		fin.getline(pokemons[n].pokeName, 100, ',');
		fin.getline(pokemons[n].type1, 20,',');
		fin.getline(pokemons[n].type2, 20, ',');
		fin>>pokemons[n].speed;
		fin.get();
		n++;
	}
	fin.close();
}
void printPokemon(Pokemon pokemons[], int n){
	int max=0;
	char s[20]="NULL";
	for (int i=0; i<n; i++){
		if (pokemons[i].speed>max) max=pokemons[i].speed;
	}
	for (int i=0; i<n; i++){
		if (pokemons[i].speed==max){
			cout<<"ID: "<<pokemons[i].pokeID<<endl;
			cout<<"Pokemon names:"<<pokemons[i].pokeName<<endl;
			cout<<"Type:"<<pokemons[i].type1;
			if (strcmp(pokemons[i].type2, s)!=0)
				cout<<", "<<pokemons[i].type2<<endl;
			cout<<"Speed: "<<pokemons[i].speed;
		}
	}
}
void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int& m){
	for (int i=0; i<n; i++){
		char s[20]="NULL";
		if ((strcmp(type1, pokemons[i].type2)==0 || strcmp(type1, pokemons[i].type1)==0) && strcmp(type2, s)==0){
			result[m].pokeID=pokemons[i].pokeID;
			strcpy(result[m].pokeName, pokemons[i].pokeName);
			m++;
		}
		else if (strcmp(type2, s)!=0 && (strcmp(type1, pokemons[i].type2)==0 && strcmp(type2, pokemons[i].type1)==0)){
			result[m].pokeID=pokemons[i].pokeID;
			strcpy(result[m].pokeName, pokemons[i].pokeName);
			m++;
		}
		else if (strcmp(type2, s)!=0 && (strcmp(type1, pokemons[i].type1)==0 && strcmp(type2, pokemons[i].type2)==0)){
			result[m].pokeID=pokemons[i].pokeID;
			strcpy(result[m].pokeName, pokemons[i].pokeName);
			m++;
		}
	}
}
int main(){
	Pokemon pokemons[100], result[100];
	int n=0, m=0;
	char s[20]="NULL";
	char type1[20], type2[20];
	ReadFile("pokemon.txt", pokemons, n);
	printPokemon(pokemons, n);
	cout<<endl<<"Input type 1: ";
	cin>>type1;
	cout<<"Input type 2: ";
	cin>>type2;
	if (strcmp(type1, s)==0){
		char p[20];
		strcpy(p, type1);
		strcpy(type1, type2);
		strcpy(type2, p);
	}
	searchPokemonByType(type1, type2, pokemons, n, result, m);
	cout<<endl<<"The list of Pokemon with Type = "<<type1;
	if (strcmp(s, type2)!=0){
		cout<<", "<<type2<<": "<<endl;
	}
	for (int i=0; i<m; i++){
		cout<<"ID: "<<result[i].pokeID<<"-Name: "<<result[i].pokeName<<endl;
	}
	//if (m==0) cout<<"No Pokemon";
	return 0;
}
