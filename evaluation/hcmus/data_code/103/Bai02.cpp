#include <iostream>
#include<cstring>
#include<cmath>

#define MAX 100
using namespace std;

int find(char arr[MAX], int& count)
{
	int size = strlen(arr);

	for (int i = 0; i < size; i++) {
		if (arr[i] == arr[i + 1]) {
			for (int j = i; j < size; j++)
			{
				if (arr[j] != arr[i])
				{
					break;
				}
				count++;
			}
			return i;
		}

	}
	return -1;
}

void deleteArray(char arr[MAX], int& size)
{
	int index = 0;

	bool check = true;
	while (check)
	{
		int count = 0;
		index = find(arr, count);
		if (index == -1)
		{
			break;
		}

		size -= count;

		for (int i = index; i < size; i++)
		{
			arr[i] = arr[i + count];
		}
	}
}

int main()
{
	char arr[MAX];
	cin.getline(arr, MAX);
	cout << endl;
	int size = strlen(arr);
	deleteArray(arr, size);
	for (int i = 0; i < size; i++)
	{
		cout << arr[i];
	}
}