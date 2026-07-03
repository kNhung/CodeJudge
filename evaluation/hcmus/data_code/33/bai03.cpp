#include<iostream>
#include<cmath>
#include<string>
#include<cstdlib>
#include<fstream>
using namespace std;

struct Pokemon
{
	string pokeID;
	string pokeName;
	string type1;
	string type2;
	int speed;
}
typedef struct Pokemon POKEMON;
struct Danh_Sach_Poken
void (POKEMON &pk)
{
	do
	{
		cout<<"Nhap ID: ";
		getline(cin,pk.pokeID);
		if(pk.pokeID.length()>10){
			cout<<"Nhap lai";
		}
	}
	while(pk.pokeID.length()>10);
	do
	{
		cout<<"Nhap Name: ";
		fflush(stdin);
		getline(cin,pk.pokeName);
		if(pk.pokeName.length()>30){
			cout<<"Nhap lai";
		}
	}
	while(pk.pokeName.length()30);
	do
	{
		cout<<"Nhap type1: ";
		cin>>pk.type1;
		if(pk.type1.length()>25){
			cout<<"Nhap lai";
		}
	}
	while(pk.type1.length()>25);
	do
	{
		cout<<"Nhap type: ";
		cin>>pk.type2;
		if(pk.type2.length()>25){
			cout<<"Nhap lai";
		}
	}
	while(pk.type2.length()>25);
	do
	{
		cout<<"Nhap speed: ";
		int n;
		cin>>pk.speed;
		if(pk.speed<=0){
			cout<<"Nhap lai";
		}
	}
	while(n<=0);
}
void soluong(int &n)
{
	int n=0;
	while(filein.eof()==false)
	{
		n++;
	}
}
void DocFile(int a[],int&n,ifstream &filein)
{
	
}
int main()
{
	int a[100];
	Pokemon x;
	Nhap_Pokemon(x);
	ifstream filein;
	filein.open("pokemon.txt",ios_base::in);
	
	filein.close();
	
}
