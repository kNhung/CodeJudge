#include <iostream>
#include <fstream>


using namespace std;

struct Pokemon{
    char pokeID[11];
    char pokeName[31];
    char type1[26];
    char type2[26];
    int speed;

};

void ReadFile(char fileName[], Pokemon pokemons[], int &n)
{
    ifstream fin;
    fin.open("pokemon.txt", ios::in);
    int demdong = 0;
    char tieude[100];
    while (!fin.eof())
    {
        if (demdong == 0) {
            fin.getline(tieude, 100, '\n');
        }

        fin.getline(pokemons[demdong].pokeID, 1000, ',');
        fin.getline(pokemons[demdong].pokeName, 1000, ',');
        fin.getline(pokemons[demdong].type1, 1000, ',');
        fin.getline(pokemons[demdong].type2, 1000, ',');
        fin >> pokemons[demdong].speed;
        demdong++;
    }

    n = demdong - 1;
   // for (int i = 0 ; i < n; i++)
      //  cout << pokemons[i].pokeID << " " << pokemons[i].pokeName << " " << pokemons[i].type1 << " " << pokemons[i].type2 << " " << pokemons[i].speed << endl;

}

void printPokemon(Pokemon pokemons[], int n)
{
    // for (int i = 0 ; i < n; i++)
      //  cout << pokemons[i].pokeID << " " << pokemons[i].pokeName << " " << pokemons[i].type1 << " " << pokemons[i].type2 << " " << pokemons[i].speed << endl;

    int MAX = 0;
    for (int i = 0; i < n; i++)
        if (pokemons[i].speed > MAX) MAX = pokemons[i].speed;

    Pokemon ans[12];
    int pos = 0;
    for (int i = 0; i < n; i++)
    if (pokemons[i].speed  == MAX) {
        ans[pos] = pokemons[i];
        pos++;
    }
    cout << "ID: ";
    for (int i = 0; i < pos; i++) {
        cout << ans[i].pokeID;
        if (i != pos - 1) cout << ", ";
    }
    cout << endl;
   cout << "Pokemon name: ";
    for (int i = 0; i < pos; i++) {
        cout << ans[i].pokeName;
        if (i != pos - 1) cout << ", ";
    }
    cout << endl;
    cout << "Type: ";
    for (int i = 0; i < pos; i++) {
        if (ans[i].type1 != "NULL") cout << ans[i].type1;
        if (i != pos - 1 || (ans[i].type2 != "NULL")) cout << ", ";
        if (ans[i].type2 != "NULL") cout << ans[i].type2;
        if (i != pos - 1) cout << ", ";
    }
    cout << endl;
    cout << "Speed: ";
    for (int i = 0; i < pos; i++) {
        cout << ans[i].speed;
        if (i != pos - 1) cout << ", ";
    }
}

void searchPokemonByType(char type1[], char type2[], Pokemon pokemons[], int n, Pokemon result[], int& m)
{
    int pos = 0;

    char null[5] = "NULL";
    for (int i = 0; i < n; i++) {
        if (type2 != "NULL" && type1 != "NULL") {
            if (pokemons[i].type1 == type1 && pokemons[i].type2 ==  type2) {
                result[pos++] = pokemons[i];
            }
            if (pokemons[i].type1 == type2 && pokemons[i].type2 ==  type1) {
                result[pos++] = pokemons[i];
            }
        }
        else {
            if (type2 == "NULL" && type1 != "NULL") {
                if (pokemons[i].type1 == type1 || pokemons[i].type2 ==  type1) {
                    result[pos++] = pokemons[i];
                }
            }
            if (type2 != "NULL" && type1 == "NULL") {
                if (pokemons[i].type1 == type2 || pokemons[i].type2 ==  type2) {
                    result[pos++] = pokemons[i];
                }
            }
        }
    }
    m = pos;

}

int main()
{
    int n, m;
    char fileName[12], type1[12], type2[12];
    Pokemon pokemons[12];
    Pokemon result[12];
    ReadFile(fileName, pokemons, n);
   // printPokemon(pokemons, n);
    searchPokemonByType( type1, type2, pokemons, n, result, m);

    cout << "Input type1: ";
    cin.getline(type1, 100, '\n');
    cout << "Input type2: ";
    cin.getline(type2, 100, '\n');

    cout << "The list of Pokemon with Type = ";
    if (type1 != "NULL") cout << type1;
    if (type1 != "NULL" && type2 != "NULL") cout << type2;
    cout << endl;

    cout << m;
    for (int i = 0; i < m; i++)
        cout << "ID" << result[i].pokeID << " - Name: " <<  result[i].pokeName << endl;

    return 0;
}
