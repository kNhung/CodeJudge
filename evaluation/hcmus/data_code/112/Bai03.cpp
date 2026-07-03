#include <iostream>
#include <cstring>

using namespace std;

const int MAX = 1000;

struct Team{
	char name[41];
	int like;
	int comment;
	int share;
	int point;
};

bool checkValidName(char a[]) {
	int n = strlen(a);
	
	if (n != 3) {
		return true;
	} else {
		for (int i = 0; i < 3; i++) {
			if(a[i] != '0') {
				return true;
			}
		}
	}
	
	return false;
}

void inputTeams(Team a[], int &n) {
	cout << "Name: ";
	cin.getline(a[n].name, 41);
	while (checkValidName(a[n].name)) {
		cout << "Like: ";
		cin >> a[n].like;
		cout << "Comment: ";
		cin >> a[n].comment;
		cout << "Share: ";
		cin >> a[n].share;
		cout << endl;
		
		n++;
		
		cin.ignore();
		cout << "Name: ";
		cin.getline(a[n].name, 41);
	}
}

void calcPoint(Team a[], int n) {
	for (int i = 0; i < n; i++) {
		a[i].point = a[i].like + a[i].comment * 2 + a[i].share * 3;
	}
}

void swap(Team &a, Team &b) {
	Team tmp;
	tmp = a;
	a = b;
	b = tmp;
}

void sortFromLargestPoint(Team a[], int n) {
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n - 1; j++) {
			if (a[j].point < a[j + 1].point) {
				swap(a[j], a[j + 1]);
			} else if (a[j].point == a[j + 1].point) {
				if (a[j].share < a[j + 1].share) {
					swap(a[j], a[j + 1]);
				} else if (a[j].share == a[j + 1].share) {
					if (a[j].comment < a[j + 1].comment) {
						swap(a[j], a[j + 1]);
					} else if (a[j].comment == a[j + 1].comment) {
						if (a[j].like < a[j + 1].like) {
							swap(a[j], a[j + 1]);
						}
					}
				}
			}
		} 
	}
}

void printName(Team a[]) {
	int n = 3;
	
	for (int i = 2; i < n; i++) {
		if(a[i].point == a[i + 1].point && a[i].share == a[i + 1].share && a[i].comment == a[i + 1].comment && a[i].like == a[i + 1].like) {
			n++;
		} else {
			break;
		}
	}
	
	for (int i = 0; i < n; i++) {
		cout << a[i].name << endl;
	}
}

int main() {
	Team teams[MAX];
	int n = 0;
	
	inputTeams(teams, n);
	calcPoint(teams, n);
	sortFromLargestPoint(teams, n);
	printName(teams);
	
	return 0;
}
