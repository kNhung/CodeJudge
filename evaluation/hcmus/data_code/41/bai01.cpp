#include <iostream>

using namespace std;
void xuatdia(int a[], int n);
void themcacdiaconlai(int temp[], int ndia,int tongdia);
bool findDisk(int temp[], int ndia, int dia);

int main ()
{
	int temp[10000];
	int tongdia;
	int ndia;
	
	cout << "Input number of disks: "; cin >> tongdia;
	cout <<"Input number of changes: "; cin >> ndia;
	cout <<"The order of changes: ";
	for (int i = 0; i < ndia; i++)
	{
		cin >> temp[ndia - i - 1];
	}
	themcacdiaconlai(temp, ndia, tongdia);
	cout <<"Disk stack: ";
	xuatdia(temp, tongdia);
	
}
bool findDisk(int temp[], int ndia, int dia)
{
	for (int i = 0; i < ndia; i++)
	{
		if (temp[i] == dia)
		return true;
	}
	return false;
}
void themcacdiaconlai(int temp[], int ndia, int tongdia)
{
	int dem = 1;
	int temp2 [10000];
	for (int i = 0; i < ndia; i++)
	{
		temp2[i] = temp[i];
	}
	for (int i = ndia; i < tongdia; i++)
	{
		if (findDisk(temp2, ndia, dem))
		{
			while (findDisk(temp2, ndia, dem))
			{
				dem++;
			}
			temp[i] = dem;
			dem++;
		}
		else
		{
			temp[i] = dem;
			dem++;
		}
	}
}
void xuatdia(int a[], int n)
{
	for (int i = 0; i < n; i++)
	{
		cout << a[i] <<" ";
	}
}
