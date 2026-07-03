#include <iostream>
#include <cmath>
#include <string>
#include <cstring>
#include <cstdlib>
#include <stdlib.h>
using namespace std;
void inputArr (int a[][10],int &row, int &col){
	for (int i = 0 ; i < row; i++){
		for (int j = 0 ; j < col ; j ++){
			cin >> a[i][j];
		}
	}
}
void outputArr (int a[][10],int row ,int col){
	for (int i = 0 ; i < row; i++){
		cout <<"\n";
		for (int j = 0; j < col; j++){
			cout <<a[i][j]<<" ";
		}
	}
}
void outputArrDx (int a[][10],int row ,int col){
	int b[10][10];
	for (int i = 0 ; i < row; i++){
		
		for (int j = 0; j < col; j++){
			b[i][j] = a[i][col - j - 1];
		}
	}
	outputArr (b, row , col);

}

int main(){
	int a[10][10];
	int row,col;
	cout << "Input dim: ";
	cin >> row >> col;
	
	cout <<"Input Arr: ";
	inputArr (a,row,col);
	cout << "Output: ";
	outputArrDx (a,row,col);
	return 0;
}
