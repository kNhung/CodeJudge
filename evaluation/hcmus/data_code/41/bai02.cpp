#include <iostream>

using namespace std;

void set2dArray(int a[][100], int row, int col);
void print2dArray(int a[][100], int row, int col);
void matrandoixung(int a[][100], int row, int col);

int main ()
{
	int row,col;
	int a[100][100];
	cout << "Input dim: "; cin >> row >> col;
	cout << "Input Arr: " ; set2dArray(a, row, col);
	matrandoixung(a, row, col);
	cout << "Output: " << endl;
	print2dArray(a, row, col);
	
}
void set2dArray(int a[][100], int row, int col){
	for (int i = 0; i < row; i++)
	{
		for (int j = 0; j < col; j++)
		{
			cin >> a[i][j];
		}
	}
}
void print2dArray(int a[][100], int row, int col)
{
	for (int i= 0; i < row; i++)
	{
		for (int j = 0; j < col; j++)
		{
			cout << a[i][j] << " ";
		}
		cout << endl;
	}
}
void matrandoixung(int a[][100], int row, int col)
{
	int temp[100][100];
	for (int i = 0; i < row; i++)
	{
		for (int j = 0; j < col; j++)
		{
			temp[i][j] = a[i][col - 1 - j];
		}
	}
	for (int i = 0; i < row; i++)
	{
		for (int j = 0; j < col; j++)
		{
			a[i][j] = temp[i][j];
		}
	}
}
