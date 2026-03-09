#include <iostream>
#include <cstring>

using namespace std;

struct Team {
	char name[40];
	int like;
	int comment;
	int share;
	int point;
	void input();
};

void Team::input() {
	cout << "Name: ";
	cin.ignore();
	cin.getline(name, 40);
	cout << "Like: ";
	cin >> like;
	cout << "Comment: ";
	cin >> comment;
	cout << "Share: ";
	cin >> share;
}

void inputArr(Team a[], int& n) {
	cin >> n;
	for (int i = 0; i < n; i++) {
		a[i].input();
	}
}

void tinhdiem(Team a[], int n) {
	Team Thebest[1000];
	int pos = -1, numberBest = 0;

	for (int i = 0; i < n; i++) {
		a[i].point = a[i].like + 2 * a[i].comment + 3 * a[i].share;
	}

	int max = a[0].point;

	for (int i = 0; i < n; i++) {
		if (max < a[i].point) {
			max = a[i].point;
			pos = i;
			Thebest[numberBest] = a[i];
		}
	}

	numberBest = 1;

	for (int i = 0; i < n; i++) {
		if (i == pos)
			continue;
		else {
			if (a[i].point == max) {
				Thebest[numberBest] = a[i];
				numberBest++;
			}
		}
	}

	for (int i = 0; i < numberBest; i++) {
		cout << Thebest[i].name << endl;
	}
}

int main() {
	Team a[1000];
	int n;
	inputArr(a, n);
	tinhdiem(a, n);

	return 0;
}