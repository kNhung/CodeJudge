#include <iostream>
#define MAX 1000
using namespace std;

void buildMatrix(int matrix[][MAX], int& width, int a[], int n)
{
	width = sqrt(n);
	int dem = 0;
	for (int i = 0; i < width; i++)
	{
		for (int j = 0; j < width; j++)
		{
			matrix[i][j] = a[dem];
			dem++;
		}
	}
}

bool checkDoiXung(int matrix[][MAX], int width)
{
	for (int i = 0; i < width; i++)
	{
		for (int j = 0; j < width; j++)
		{
			if (matrix[i][j] != matrix[width - 1 - j][width - 1 - i]
				&& matrix[i][j] != matrix[j][i])
				return false;

		}
	}
	return true;
}

int main()
{
	int n = 9;
	int a[] = { 1,2,3,4,5,2,7,4,1 };
	int width;
	int matrix[MAX][MAX];
	buildMatrix(matrix, width, a, n);
	cout << checkDoiXung(matrix, width);
	return 0;
}