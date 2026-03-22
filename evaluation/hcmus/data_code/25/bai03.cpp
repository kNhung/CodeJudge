#include <iostream>
#include <fstream>
#include <cstring>
using namespace std;

const int N = 500 + 25;

struct Pokemon {
    char pokeID[10];
    char pokeName[30];
    char type1[25];
    char type2[25];
    int speed;

    void print();
};

char checking[4] = {'N', 'U', 'L', 'L'};
bool checkNULL(char type[]) {
    for (int i = 0; i < 4; ++i)
        if (type[i] != checking[i])
            return false;
    return true;
}

void print(Pokemon poke) {
    cout << "ID: " << poke.pokeID << '\n';
    cout << "Pokemon name: " << poke.pokeName << '\n';
    cout << "Type: ";
    if (!checkNULL(poke.type1)) cout << poke.type1;
    if (!checkNULL(poke.type2)) {
        if (!checkNULL(poke.type1)) cout << ", " << poke.type2;
        else cout << poke.type2;
    }
    cout << '\n';
    cout << "Speed: " << poke.speed << '\n';
}

Pokemon pokemons[N];
Pokemon result[N];
char line[N];
char save[N];
int numpoke, m;
char input_type1[N];
char input_type2[N];

int toNumber(char save[], int limit) {
    int ret = 0;
    for (int i = 0; i < limit; ++i)
        ret = ret * 10 + (save[i] - '0');
    return ret;
}

void addInfo(char a[], char b[], int limit) {
    for (int i = 0; i < limit; ++i)
        a[i] = b[i];
}

void parseLine(char line[], Pokemon pokemons[], int index) {
    int n = strlen(line);
    int comma = 0;
    int iter = 0;
    for (int i = 0; i < n; ++i) {
        if (line[i] != ',') {
            save[iter] = line[i];
            ++iter;
        }
        else {
            ++comma;
            if (comma == 1) addInfo(pokemons[index].pokeID, save, iter);
            else if (comma == 2) addInfo(pokemons[index].pokeName, save, iter);
            else if (comma == 3) addInfo(pokemons[index].type1, save, iter);
            else if (comma == 4) addInfo(pokemons[index].type2, save, iter);
            iter = 0;
        }
    }

    pokemons[index].speed = toNumber(save, iter);
}

bool eq(char a[], char b[]) {
    for (int i = 0; i < strlen(b); ++i)
        if (a[i] != b[i]) return false;
    return true;
}

void printPokemon(Pokemon pokemons[], int n) {
    int max_speed = 0;
    int index = 0;
    for (int i = 0; i < n; ++i) {
        if (max_speed < pokemons[i].speed) {
            max_speed = pokemons[i].speed;
            index = i;
        }
    }

    print(pokemons[index]);
}

void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int & m) {
    if (checkNULL(type1) || checkNULL(type2)) {
        char type[N];
        for (int i = 0; i < strlen(type1); ++i) type[i] = type1[i];
        if (checkNULL(type1)) {
            for (int i = 0; i < strlen(type2); ++i) type[i] = type2[i];
            type[strlen(type2)] = '\0';
        }

        for (int i = 0; i < n; ++i) {
            if (eq(pokemons[i].type1, type) || eq(pokemons[i].type2, type)) {
                cout << "ID: " << pokemons[i].pokeID << " - Name: " << pokemons[i].pokeName << '\n';
                result[m++] = pokemons[i];
            }
        }
    }
    else {
        for (int i = 0; i < n; ++i) {
            if (eq(pokemons[i].type1, type1) && eq(pokemons[i].type2, type2)) {
                cout << "ID: " << pokemons[i].pokeID << " - Name: " << pokemons[i].pokeName << '\n';
                result[m++] = pokemons[i];
            }
            else if (eq(pokemons[i].type1, type2) && eq(pokemons[i].type2, type1)) {
                cout << "ID: " << pokemons[i].pokeID << " - Name: " << pokemons[i].pokeName << '\n';
                result[m++] = pokemons[i];
            }
        }
    }
}

int main() {
    ifstream fin;
    fin.open("pokemon.txt");
    if (fin.is_open() == false) {
        cout << "File does not exist";
        return 1;
    }

    fin.getline(line, N);
    numpoke = 0;
    while (fin.eof() == false) {
        fin.getline(line, N);
        if (strlen(line) > 0) {
            parseLine(line, pokemons, numpoke);
            ++numpoke;
        }
    }

    fin.close();
    cout << "Pokemon with max speed:\n";
    printPokemon(pokemons, numpoke);

    cout << "\nInput Type1: ";
    cin.getline(input_type1, N);
    if (strlen(input_type1) == 0) {
        for (int i = 0; i < 4; ++i) input_type1[i] = checking[i];
        input_type1[4] = '\0';
    }

    cout << "Input Type2: ";
    cin.getline(input_type2, N);
    if (strlen(input_type2) == 0) {
        for (int i = 0; i < 4; ++i) input_type2[i] = checking[i];
        input_type2[4] = '\0';
    }

    cout << "The list of Pokemon with Type = ";
    if (!checkNULL(input_type1)) cout << input_type1;
    if (!checkNULL(input_type2)) {
        if (!checkNULL(input_type1)) cout << ", " << input_type2;
        else cout << input_type2;
    }
    cout << '\n';

    searchPokemonByType(input_type1, input_type2, pokemons, numpoke, result, m);

    return 0;
}

