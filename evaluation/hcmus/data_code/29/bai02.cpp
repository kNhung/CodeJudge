#include <iostream>

struct Matrix {
	int data[100][100];
	
	int rows;
	int cols;
};

void inputMatrix(Matrix &mat) {
	std::cout << "Input dim: ";
	std::cin >> mat.rows >> mat.cols;
	
	std::cout << "Input Arr: ";
	for (int i = 0; i < mat.rows; ++i) {
		for (int j = 0; j < mat.cols; ++j) {
			std::cin >> mat.data[i][j];
		}
	}
}

void printMatrix(const Matrix &mat) {
	for (int i = 0; i < mat.rows; ++i) {
		for (int j = 0; j < mat.cols; ++j) {
			std::cout << mat.data[i][j] << ' ';
		}
		std::cout << '\n';
	}
}

void reverseRows(Matrix &mat) {
	for (int i = 0; i < mat.rows; ++i) {
		for (int j = 0; j < mat.cols / 2; ++j) {
			int t = mat.data[i][j];
			mat.data[i][j] = mat.data[i][mat.cols - j - 1];
			mat.data[i][mat.cols - j - 1] = t;
		}
	}
}

int main(void) {
	Matrix mat;
	inputMatrix(mat);
	reverseRows(mat);
	printMatrix(mat);
	
	return 0;
}
