#include <iostream>
#include <fstream>
using namespace std;

struct Pokemon{
	char[10] pokeID;
	char[30] pokeName;
	char[25] type1;
	char[25] type2;
	int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n){
	char k;
	char arr[50];
	
	ifstream f;
	f.open(fileName,ios::in);
	for (int i=0;i<33;i++) {
		f>>arr[i];
	}
	
	for (int i=0;i<n;i++){
		
		f>>pokemons[i].pokeID;
		f>>k;f>>k;
		while(k!=","){
		
	    	pokemons[i].pokeName+=k;
	    	f>>k;
	    }
		f>>k;	
		while(k!=","){
		
	    	pokemons[i].type1+=k;
	    	f>>k;
	    }
		f>>k;
		while(k!=","){
		
	    	pokemons[i].type2+=k;
	    	f>>k;
	    }
		f>>k;
			while(k!=","){
		
	    	pokemons[i].speed+=k;
	    	f>>k;
	    }
		
	}
	
	f.close();
	
}

void printPokemon(Pokemon pokemons[], int n){
	int maxspeed=0;
	int vitri;
	for (int i=0;i<n;i++){
		if (pokemons[i].speed>max) {
		    maxspeed=pokemons[i].speed;
		    vitri=i;
	    }
	}
	cout<<"ID: "<<pokemons[vitri].pokeID<<endl;
	cout<<"Pokemon Name: "<<pokemons[vitri].pokeName<<endl;
	cout<<"Type: "<<pokemons[vitri].type1<<", "<<pokemons[vitri].type2<<endl;
	cout<<"Speed: "pokemons[vitri].speed;			
	
}

void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n,Pokemon result[],int& m){
	
}

int main(){
	Pokemon a[100];
	int n;
	ReadFile("pokemon.txt",a,n);
	
	
	return 0;
}
