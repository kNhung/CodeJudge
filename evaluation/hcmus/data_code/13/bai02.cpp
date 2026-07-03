#include <iostream>

void swap(int& a, int& b) {
    int temp = a;
    a = b;
    b = temp;
}

void createSymmetricMatrix(int** arr, int rows, int cols) {

    for (int i = 0; i < rows; i++) {
       
        for (int j = 0; j < cols / 2; j++) {
            swap(arr[i][j], arr[i][cols - 1 - j]);
        }
    }
}

int main() {
    int rows, cols;
    std::cout << "Input dim: ";
    std::cin >> rows >> cols;

    int** arr = new int*[rows];
    std::cout << "Input Arr: ";
    for (int i = 0; i < rows; i++) {
        arr[i] = new int[cols];
        for (int j = 0; j < cols; j++) {
            std::cin >> arr[i][j];
        }
    }

  
    createSymmetricMatrix(arr, rows, cols);

    
    std::cout << "Output:" << std::endl;
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            std::cout << arr[i][j] << " ";
        }
        std::cout << std::endl;
    }

    
    for (int i = 0; i < rows; i++) {
        delete[] arr[i];
    }
    delete[] arr;

    return 0;
}
