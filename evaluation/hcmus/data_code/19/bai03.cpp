#include <iostream>
#include <fstream>
#include <string>

using namespace std;

// Định nghĩa cấu trúc Pokemon
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
        cout << "Khong the mo file." << endl;
        return;
    }


    inputFile >> n;
    inputFile.ignore(); // Đọc và bỏ qua kí tự xuống dòng

    // Đọc thông tin của từng Pokemon
    for (int i = 0; i < n; ++i) {
        getline(inputFile, pokemons[i].pokeID, ',');
        getline(inputFile, pokemons[i].pokeName, ',');
        getline(inputFile, pokemons[i].type1, ',');
        getline(inputFile, pokemons[i].type2, ',');
        inputFile >> pokemons[i].speed;
        inputFile.ignore(); // Đọc và bỏ qua kí tự xuống dòng
    }

    inputFile.close();
}

int main() {
    const int MAX_POKEMONS = 100; // Số lượng tối đa cho mảng pokemons
    Pokemon pokemons[MAX_POKEMONS]; // Mảng chứa thông tin Pokemon
    int n; // Số lượng Pokemon

    // Gọi hàm đọc dữ liệu từ file
    ReadFile("pokemon.txt", pokemons, n);

    // In thông tin Pokemon
    cout << "Thong tin Pokemon tu file:" << endl;
    for (int i = 0; i < n; ++i) {
        cout << "ID: " << pokemons[i].pokeID << ", Name: " << pokemons[i].pokeName
             << ", Type1: " << pokemons[i].type1 << ", Type2: " << pokemons[i].type2
             << ", Speed: " << pokemons[i].speed << endl;
    }

    return 0;
}
