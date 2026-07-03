#include <iostream>
#include <cmath>
#include <cstring>
using namespace std;
int SoLuong(int a[], int &n, int x){
	int dem = 0;
	for(int i = 0; i < n; i++){
		for (int j = i + 1; j < n; j++){
			if (a[x] = a[i] = a[j]);
			dem++;
		}
	}
	return dem;
}
int Layso(int a[], int &n, int x){
	for ( int i = 0; i < n; i++){
		for (int j = i + 1; j < n; j++){
			if(a[x] = SoLuong(a,n,x)){
				a[0] =a[x];
			}
			j++;
		}
		i++;
	}
}

int main(){
	int n,m;
	int a[n];
	cout << "Input number of disks: ";
	cin >> n;
	cout << "Input number of changes: ";
	cin >> m;
	cout << "The order of changes: ";
	SoLuong(a,n,m);
	cout << "Dish stack: ";
	Layso(a,n,m);
	return 0;
}
