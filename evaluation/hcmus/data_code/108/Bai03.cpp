#include <iostream>

using namespace std;

struct Team{
	char Name[40];
	int like;
	int cmt;
	int share;
	
	void input();
};

void Team::input(){
	cin.ignore();
	cout << "Nhap vao ten doi: ";
	cin.getline(Name, 40);
	
	cout << "Nhap vao so luot like: ";
	cin >> like;
	cout << "Nhap vao so luot comment: ";
	cin >> cmt;
	cout << "Nhap vao so luot share: ";
	cin >> share;
	
}

void input(Team a[], int &n){
	cout << "Nhap vao so doi: ";
	cin >> n;
	for (int i = 0; i < n; i++){
		a[i].input();
	}
}

void solve(Team a[], int n){
	int max1 = 0;
	int max2 = 0;
	int max3 = 0;
	int save1;
	int save2;
	int save3;
	for (int i = 0; i < n; i++){
		int point = a[i].like * 1 + a[i].cmt * 2 + a[i].share * 3;
		if (point > max1){
			max1 = point;
			a[i] = a[0];
			save1 = i;
		}
		if (point == max1){
			if (a[i].share > a[save1].share){
				a[i] = a[i + 1];
				a[i] = a[0];
				a[save1] = a[1];
			}
			else if (a[i].share == a[save1].share){
				if (a[i].cmt > a[save1].cmt){
					a[i] = a[i + 1];
					a[i] = a[0];
					a[save1] = a[1];
				}
			}
			else{
				a[i] = a[1];
			}
			
		}	
	}
	
	for (int i = 1; i < n; i++){
		int point = a[i].like * 1 + a[i].cmt * 2 + a[i].share * 3;
		if (point > max2){
			max2 = point;
			a[i] = a[1];
			save2 = i;
		}
		if (point == max2){
			if (a[i].share > a[save2].share){
				a[i] = a[i + 1];
				a[i] = a[1];
				a[save1] = a[2];
			}
			else if (a[i].share == a[save2].share){
				if (a[i].cmt > a[save2].cmt){
					a[i] = a[i + 1];
					a[i] = a[save2 + 1];
					a[save2] = a[save2 + 2];
				}
			}
			else{
				a[i] = a[save2 + 1];
			}
				
	}
	
	for (int i = 2; i < n; i++){
		int point = a[i].like * 1 + a[i].cmt * 2 + a[i].share * 3;
		if (point > max3){
			max3 = point;
			a[i] = a[2];
			save3 = i;
		}
		if (point == max3){
			if (a[i].share > a[save3].share){
				a[i] = a[i + 1];
				a[i] = a[2];
				a[save1] = a[3];
			}
			else if (a[i].share == a[save3].share){
				if (a[i].cmt > a[save3].cmt){
					a[i] = a[i + 1];
					a[i] = a[save3 + 1];
					a[save2]= a[save3 + 2];
				}
			}
			else{
				a[i] = a[save3 + 1];
			}	
	}
}
}
}

void print(Team a[], int n){
	for (int i = 0; i < 3; i++){
		cout << a[i].Name << endl;
	}
}
int main(){
	Team a[1000];
	int n;
	input(a, n);
	solve(a, n);
	
	return 0;
}


