
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>

using namespace std;
struct Pokemon {
	string pokeID;
	string pokeName;
	string type1;
	string type2;
	int speed;
};

void ReadFile(char fileName[], Pokemon pokemons[], int &n) {
	ifstream inputFile(fileName);

	if (!inputFile.is_open()) {
		cout << "Unable to open file";
		return;
	}

	n = 0;

	while (!inputFile.eof()) {
		getline(inputFile, pokemons[n].pokeID, ',');
		if (pokemons[n].pokeID.empty()) {
			break;
		}
		getline(inputFile, pokemons[n].pokeName, ',');
		getline(inputFile, pokemons[n].type1, ',');
		getline(inputFile, pokemons[n].type2, ',');
		string speedStr;
		getline(inputFile, speedStr);

		stringstream speedStream(speedStr);
		speedStream >> pokemons[n].speed;

		n++;
	}

	inputFile.close();
}

void printPokemon(const Pokemon& p) {
	cout << "ID: " << p.pokeID << endl;
	cout << "Pokemon name: " << p.pokeName << endl;
	cout << "Type: " << p.type1;
	if (!p.type2.empty()) {
		cout << ", " << p.type2;
	}
	cout << endl;
	cout << "Speed: " << p.speed << endl;
}

// Hàm in ra Pokemon có tốc độ lớn nhất
void printFastestPokemon(const Pokemon pokemons[], int n) {
	if (n <= 0) {
		cout << "No Pokemon data available." << endl;
		return;
	}

	int maxSpeedIndex = 0;
	for (int i = 1; i < n; ++i) {
		if (pokemons[i].speed > pokemons[maxSpeedIndex].speed) {
			maxSpeedIndex = i;
		}
	}

	cout << "Fastest Pokemon:" << endl;
	printPokemon(pokemons[maxSpeedIndex]);
}

int main() {
	Pokemon pokemons[100];
	int n;

	char fileName[] = "pokemon.txt";
	ReadFile(fileName, pokemons, n);

	printFastestPokemon(pokemons, n);

	return 0;
}