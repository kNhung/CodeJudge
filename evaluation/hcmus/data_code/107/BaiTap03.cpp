//23127077
#include <iostream>
#include <cstring>
#include <cmath>

const int MAX = 10;

using namespace std;

struct team
{
	char name[40];
	int likes, cmt, share;
	int score;
};

int inputTeam(team a[], int &n, int &i)
{
	cout << "Name: ";
	cin.getline(a[i].name, 40);
	if (a[i].name == "000") return 1;
	cout << "Likes: ";
	cin >> a[i].likes;
	cout << "Comments: ";
	cin >> a[i].cmt;
	cout << "Shares: ";
	cin >> a[i].share;
	n++;
	i++;
	a[i].score = a[i].cmt * 2 + a[i].likes + a[i].share * 3;  
	return 0;
}

void result(team a[], int n)
{
	team tmp;
	for (int j = 0; j < n * n; j++)
	{
		for (int i = 0; i < n; i++)
		{
			if (a[i].score < a[i + 1].score)
			{
				tmp = a[i];
				a[i] = a[i + 1];
				a[i + 1] = tmp;
			}
		}
	}
	
	return;
}

void printResult(team a[], int n)
{
	for (int i = 0; i < 3; i++)
	{
		cout << a[i].name << endl;
	}	
}

int main()
{
	team a[MAX];
	int n, i =0;
	
	inputTeam(a, n, i);
	result(a, n);
	printResult(a, n);
	
}
