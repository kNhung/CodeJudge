#include<iostream>

using namespace std;

const int MAX=1000;
void inputArr(int a[][MAX], int &hang, int &cot){
	cout << "Nhap so hang cua mang: ";
	cin >> hang;
	cout << "Nhap so cot cua mang: ";
	cin >> cot;
	for(int i=0;i < hang; i++){
		for(int j = 0; j < cot; j++){
			cout<<"Nhap a["<<i<<"]"<<"["<<j<<"]: ";
			cin>>a[i][j];
		}
	}
}

void inMang(int a[MAX][MAX], int &hang, int &cot){
	for(int i=0;i< hang;i++){
		for(int j=0;j<cot;j++){
			cout<<a[i][j];
		}
		cout<<endl;
	}
}

int main(){
	int a[MAX][MAX];
	int hang;
	int cot;
	inputArr(a, hang, cot);
	inMang(a, hang, cot);
	return 0;
}

