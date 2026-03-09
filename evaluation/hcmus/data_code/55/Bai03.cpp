#include<cmath>
#include <iostream>
using namespace std;

int reverse(int a)
{
	int result = 0;
	while (a != 0)
	{
		result = result * 10 + a % 10;
		a = a / 10;
	}
	return result;
}
int find(int a_l, int a_r)
{
	int index_r;
	int index_l;
	int a_l2 = a_l;
	int result = 0;
	while (a_r != 0)
	{
		int temp_al2 = a_l2;
		index_r = a_r % 10;
		a_r = a_r / 10;
		while (temp_al2 != 0)
		{
			index_l = temp_al2 % 10;
			temp_al2 = temp_al2 / 10;
			if (index_l == index_r)
			{
				result = result * 10 + index_r;
				break;
			}
		}
		if (temp_al2 != 0)
		{
			a_l2 = temp_al2;
		}
	}
	return result;
}
int Dem_sochuso(int a)
{
	int result = 1;
	while (a != 0)
	{
		a = a / 10;
		result * 10;
	}
	return result;
}
int Cutting(int a)
{
	int dem = 10;
	int a1 = a;
	int max = 0;
	int result;
	int a_r, a_l, mid = -1;
	while (a1 != 0)
	{
		if (mid == -1)
		{
			a_r = a1 % dem;
			a_l = a1 / dem;
			a1 = a1 / 10;
			if (a_l < a_r)
			{
				int temp = a_r;
				a_r = a_l;
				a_l = temp;
			}
			a_r = reverse(a_r);
			int a_cutted = find(a_l, a_r);
			int count = Dem_sochuso(a_cutted);
			result = a_cutted * count + a_cutted;
			if (max < result)
			{
				max = result;
			}
			mid = -1;
		}
		else
		{
			a_r = a1 % dem;
			mid = a1 / dem;
			mid = a1 % 10;
			a_l = a1 / (dem * 10);
			a_l = a1 / dem;
			a1 = a1 / 10;
			if (a_l < a_r)
			{
				int temp = a_r;
				a_r = a_l;
				a_l = temp;
			}
			a_r = reverse(a_r);
			int a_cutted = find(a_l, a_r);
			int count = Dem_sochuso(a_cutted);
			result = a_cutted * count + a_cutted;
			if (max < result)
			{
				max = result;
			}
			mid = 0;
		}

	}
	return max;
}
int main()
{
	cout << Cutting(12341);
	return 0;
}