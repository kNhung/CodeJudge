
#include <iostream>
using namespace std;

// Hàm để in ma trận
void printMatrix(int matrix[100][100], int rows, int cols) {
	for (int i = 0; i < rows; ++i) 
	{
		for (int j = 0; j < cols; ++j)
		{
			cout << matrix[i][j] << " ";
		}
		cout << endl;
	}
}

// Hàm tạo ma trận đối xứng theo chiều dọc tại cạnh bên phải
void createSymmetricMatrix(int matrix[100][100], int rows, int cols) {
	for (int i = 0; i < rows; ++i) 
	{
		for (int j = 0; j < cols / 2; ++j) 
		{
			int temp = matrix[i][j];
			matrix[i][j] = matrix[i][cols - j - 1];
			matrix[i][cols - j - 1] = temp;
		}
	}
}

int main() {
	int rows, cols;

	cout << "Input dim: ";
	cin >> rows >> cols;

	int matrix[100][100];

	cout << "Input Arr: ";
	for (int i = 0; i < rows; ++i) {
		for (int j = 0; j < cols; ++j) 
		{
			cin >> matrix[i][j];
		}
	}

	createSymmetricMatrix(matrix, rows, cols);

	cout << "Output:" << endl;
	printMatrix(matrix, rows, cols);

	return 0;
}