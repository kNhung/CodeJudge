#include<iostream>
#include<cstring>
#define MAX 1000
using namespace std;

struct thongtindoituyen {
	char name[MAX];
	int likes;
	int comments;
	int share;
	int tongdiem = likes + comments * 2 + share * 3;
};

void nhapthongtin(thongtindoituyen doituyen) {
	cout << "Name: ";
	cin >> doituyen.name;
	cout << "Like: ";
	cin >> doituyen.likes;
	cout << "Comment: ";
	cin >> doituyen.comments;
	cout << "Share: ";
	cin >> doituyen.share;
	cout << endl;
}


int main() {

	while (true) {

		int dem = 0;

		cout << "Nhap vao thong tin doi tuyen " << dem + 1;

		thongtindoituyen doituyen;
		nhapthongtin(doituyen);






		if (doituyen.name == "000") {
			break;
		}

	}


	return 0;
}