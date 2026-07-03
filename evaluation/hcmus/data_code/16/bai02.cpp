#include <iostream>
const int SIZE = 100;
using namespace std;

void makeSymmerVerticalAxis(int mat[][SIZE], int row, int col)
{
    int mid;
    if (col % 2 != 0) mid = (col / 2);
    else mid = (col / 2) ;

    for (int i = 0; i < row; ++i)
    {
        int right = col - 1; //vi tri cot ben phai
        for (int j = 0; j < mid; ++j)
        {
            int temp = mat[i][j];
            mat[i][j] = mat[i][right];
            mat[i][right] = temp;
            right--;
        }
    }
}


int main()
{
    int row, col, mat[SIZE][SIZE];
    cout << "Input dim: ";
    cin >> row >> col;
    cout <<"Input Arr: ";

    for (int i = 0; i < row; ++i)
    {
        for (int j = 0; j < col; ++j)
            cin >> mat[i][j];
    }

    cout << "Ouput:\n";
    makeSymmerVerticalAxis(mat, row, col);

    for (int i = 0; i < row - 1; i++)
    {
        for (int j = 0; j < col -1; j++)
        {
            cout << mat[i][j] << ' ';
        }
        cout << mat[i][col - 1] <<'\n';
    }

    for (int i = 0; i < col - 1; ++i)
        cout << mat[row - 1][i] << ' ';
    cout << mat[row - 1][col - 1];
    return 0;
}

