
#include <iostream>
#include<cstring>
#include<cmath>
#define MAX 100
using namespace std;

struct team {
	char name[MAX];
	int like;
	int com;
	int share;

	int diem;
};

void input(team& a, bool& check)
{
	cout << "Name: ";
	cin.get(a.name, MAX);

	if ((a.name[0] == '0') && (a.name[1] == '0') && (a.name[2] == '0'))
	{
		check = false;
		return;
	}
	//cin.ignore();
	cout << "Like: ";
	cin >> a.like;
	cout << "Comment: ";
	cin >> a.com;
	cout << "Share: ";
	cin >> a.share;
	cin.ignore();
}
int main()
{

	team arr[MAX];
	int size = 0;
	bool check = true;
	int index = 0;

	while (check) {

		bool check_input = true;

		input(arr[size], check_input);

		if (!check_input)
			break;

		size += 1;
	}



	for (int i = 0; i < size; i++)
	{
		arr[i].diem = arr[i].like + arr[i].com * 2 + arr[i].share * 3;
	}


	for (int i = 0; i < size; i++)
	{
		for (int j = i + 1; j < size; j++)
		{
			if (arr[j].diem > arr[i].diem) {
				swap(arr[j], arr[i]);
			}
			else
			{
				if (arr[j].share > arr[i].share)
				{
					swap(arr[j], arr[i]);
				}
				else
				{
					if (arr[j].com > arr[i].com)
					{
						swap(arr[j], arr[i]);
					}
					else
					{
						if (arr[j].like > arr[i].like)
						{
							swap(arr[j], arr[i]);
						}
					}
				}
			}
		}
	}

	for (int i = 0; i < strlen(arr[0].name); i++)
	{
		cout << arr[0].name[i];
	}
	cout << endl;
	for (int i = 0; i < strlen(arr[1].name); i++)
	{
		cout << arr[1].name[i];
	}
	cout << endl;
	for (int i = 0; i < strlen(arr[2].name); i++)
	{
		cout << arr[2].name[i];
	}
	cout << endl;
}