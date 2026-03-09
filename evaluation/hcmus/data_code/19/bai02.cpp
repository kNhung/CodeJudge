#include <iostream>

void createSymmetricMatrix(int** originalMatrix, int numRows, int numCols) {
    // Đảo ngược giá trị trong cột để tạo ma trận đối xứng
    for (int i = 0; i < numRows; ++i) {
        for (int j = 0; j < numCols / 2; ++j) {
            std::swap(originalMatrix[i][j], originalMatrix[i][numCols - 1 - j]);
        }
    }
}

int main() {
    int numRows, numCols;

    // Nhập số hàng và số cột
    std::cout << "Input dim: ";
    std::cin >> numRows >> numCols;

    // Nhập ma trận
    std::cout << "Input Arr: ";
    int** originalMatrix = new int*[numRows];
    for (int i = 0; i < numRows; ++i) {
        originalMatrix[i] = new int[numCols];
        for (int j = 0; j < numCols; ++j) {
            std::cin >> originalMatrix[i][j];
        }
    }

    // Tạo ma trận đối xứng
    createSymmetricMatrix(originalMatrix, numRows, numCols);

    // In ra ma trận đối xứng
    std::cout << "Output:" << std::endl;
    for (int i = 0; i < numRows; ++i) {
        for (int j = 0; j < numCols; ++j) {
            std::cout << originalMatrix[i][j] << " ";
        }
        std::cout << std::endl;
    }

    // Giải phóng bộ nhớ
    for (int i = 0; i < numRows; ++i) {
        delete[] originalMatrix[i];
    }
    delete[] originalMatrix;

    return 0;
}
