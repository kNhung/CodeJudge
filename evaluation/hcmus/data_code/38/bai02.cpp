#include <iostream>

using namespace std;

const int Max_Rows = 100;
const int Max_Cols = 100;

void print2DArray(int mat[][Max_Cols], int row, int col){
	cout<<"Input dim: ";
	cin>>row>>col;
	cout<<"Input Arr: ";
	for (int i = 0; i < row; i++){
		for (int j = 0; j < col; j++){
			cin>>mat[i][j];
		}
	}
}

void reflectMat(int mat[][Max_Cols], int row, int col){
	int temp;
	for(int i = 0; i < row; i++){
		for(int j = 0; j < col; j++){
			mat[i][j] = temp;
			temp = mat[i][col - 1 - j];
			mat[i][col - 1 - j] = mat[i][j];
		}
	}
	for(int i = 0; i < row; i ++){
		for(int j = 0; j < col; j++){
			cout<<mat[i][j];
		}
		cout<<endl;
	}
}

int main(){
	int row, col;
	int mat[row][100];
	print2DArray(mat, row, col);
	cout<<"Output: "<<endl;
	reflectMat(mat, row, col);
	return 0;
}
