#include <iostream>

using namespace std;

#define MAX 100

bool ladoixung(int a[][MAX], int rows, int cols) {
    for (int i = 0; i < rows; ++i) 
    {
        for (int j = 0; j < cols; ++j) 
        {
            if (a[i][j] != a[j][i]) 
            {
                return false;
            }
        }
    }

    for (int i = 0; i < rows; ++i) 
    {
        for (int j = 0; j < cols; ++j) 
        {
            if (a[i][j] != a[rows - 1 - j][cols - 1 - i]) 
            {
                return false;
            }
        }
    }

    return true;
}

int main() {
    int rows, cols;
    cout << "Nhap so hang cua mang 2 chieu: ";
    cin >> rows;
    cout << "Nhap so cot cua mang 2 chieu: ";
    cin >> cols;


    int a[MAX][MAX];

    for (int i = 0; i < rows; ++i) 
    {
        for (int j = 0; j < cols; ++j) {
            cout << "Nhap gia tri tai vi tri [" << i << "][" << j << "]: ";
            cin >> a[i][j];
        }
    }

    if (ladoixung(a, rows, cols)) {
        cout << "Mang la mang doi xung." << endl;
    } else {
        cout << "Mang khong doi xung." << endl;
    }

    return 0;
}
