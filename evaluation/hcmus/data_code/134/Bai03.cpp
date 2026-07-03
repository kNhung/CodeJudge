#include <iostream> 

using namespace std;

struct CuocThi{
	char name[50];
	int like;
	int cmt;
	int share;
};

void inputInfo(CuocThi player[100]) {
	for(int i = 0; i < 100; i++) {
		cout << "Name: ";
		cin.getline(player[i].name, 50);
		if(player[i].name == 000) {
			break;
		}
		else {
			cout << "Like: ";
			cin >> player[i].like;
			cout << "Comment: ";
			cin >> player[i].cmt;
			cout << "Share: ";
			cin >> player[i].share;
		}
	}
}

int calculatePoint(CuocThi player[100]) {
	int point = 0;
	point = player.like * 1 + player.cmt * 2 + player.share * 3;
	return point;
}

void find1st(CuocThi player) {
	int max = calculatePoint(player[0]);
	for(int i = 0; i < 100; i++) {
		tmp = calculatePoint(player[i]);
		if(tmp > max) {
			max = tmp;
		}
	}
	cout << max.name;
}

int main() {
	CuocThi player[100];
	inputInfo(player);
	return 0;
}