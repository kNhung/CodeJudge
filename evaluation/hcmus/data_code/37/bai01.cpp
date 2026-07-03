#include <iostream>
#include <fstream>
#include <cstring>
#include <string.h>
#include <stdlib.h>
#define max 100
using namespace std;

int check(int a, int b, int c[]){
		for (int j = 0; j < b; j++){
			if(a == c[j]){
				return 1;
			}
		}
		return 2;

}

void in(int a, int b, int c[]){
	int d[max];
	int e[max];
	int m = 0;
	int n = 0;
	int h = b;
	for (int i = 0; i < b; i++){
		d[i] = c[b - i - 1];
	}
	
	for (int i = 1; i < a; i++){
			if(check(i, b, c) == 2){
				d[h++] = i;
			}
	}
	for (int i = 0; i < a; i++){
		cout << d[i] << "\t";
	}
}


int main(){
	int a, b;
	int c[max];
	cout << "input number of disks: ";
	cin >> a;
	cout << "input number of changes: ";
	cin >> b;
	cout << "the order of changes: ";
	for (int i = 0; i < b; i++){
		cin >> c[i];
	}
	cout << "disk stack: ";
	in(a, b, c);
	return 0;
}
