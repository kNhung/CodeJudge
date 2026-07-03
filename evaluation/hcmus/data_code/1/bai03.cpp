#include <iostream>
#include <fstream>
#include <string>  // Ð?m b?o bao g?m thu vi?n này d? s? d?ng std::string

void removeEmptyLines(const std::string& filePath) {
    std::ifstream inFile(filePath.c_str());  // S? d?ng .c_str() d? chuy?n d?i t? std::string sang const char*
    if (!inFile.is_open()) {
        std::cerr << "Unable to open file: " << filePath << std::endl;
        return;
    }

    std::ofstream outFile("hello.txt");  // T?o m?t t?p tin t?m th?i

    std::string line;

    while (std::getline(inFile, line)) {
        // Ki?m tra dòng có ch? ch?a kí t? '\n' không
        if (line == "\n" || line == "\r\n" || line == "\r" || !line.empty()) {
            outFile << line << std::endl;
        }
    }

    inFile.close();
    outFile.close();

  
}

int main() {
    std::string filePath = "input.txt";
    removeEmptyLines(filePath);

    return 0;
}

void xoaXe(xe ds[], int n){
    int nam;
    time_t now = time(0);
    tm* t = localtime(&now);
    cout<<"Nhap so nam: "; cin>>nam;
    for(int i=0; i<n; i++){
        if((1900 + t->tm_year) - ds[i].namSX == nam){
            for(int j=i; j<n-1; j++){
                ds[j]=ds[j+1];
            }
            n--;
            i--;
        }
    }
    xuatDS(ds, n);
}

#include <iostream>
#include <fstream>
#include <string>

using namespace std;

const int MAX_STUDENTS = 100;
const int MAX_SUBJECTS = 10;


struct pokemon {
	int id;
	string name;
	string type1;
	string type2;
	float speed;
};

void docThongTinSinhVien(ifstream& fileIn, pokemon &poke) {
    getline(fileIn, sinhVien.hoTen, ',');
    getline(fileIn, sinhVien.mssv, ',');
    getline(fileIn, sinhVien.ngaySinh);

    fileIn >> sinhVien.soMonHoc;
    fileIn.ignore(); // Ð?c ký t? xu?ng dòng

    for (int i = 0; i < sinhVien.soMonHoc; ++i) {
        docThongTinMonHoc(fileIn, sinhVien.dsMonHoc[i]);
    }
}

void ReadFile(char fileName[], Pokemon pokemons[], int &n) {
	ifstream fileIn(fileName);
	if (!fileIn.is_open()) {
        cout << "Khong the mo file." << endl;
        return 1;
    }
    while (!fileIn.eof()) {
        docThongTinSinhVien(fileIn, dsSinhVien[soSinhVien]);
        soSinhVien++;
    }

}

void docThongTinMonHoc(ifstream& fileIn, MonHoc& monHoc) {
    getline(fileIn, monHoc.tenMon, '-');
    fileIn >> monHoc.diem;
}



void inThongTinSinhVien(SinhVien sinhVien) {
    cout << "Ho ten: " << sinhVien.hoTen << endl;
    cout << "MSSV: " << sinhVien.mssv << endl;
    cout << "Ngay sinh: " << sinhVien.ngaySinh << endl;

    cout << "Ds mon hoc:" << endl;
    for (int i = 0; i < sinhVien.soMonHoc; ++i) {
        cout << sinhVien.dsMonHoc[i].tenMon << ": " << sinhVien.dsMonHoc[i].diem << endl;
    }

    cout << endl;
}

int main() {
    ifstream fileIn("input.txt");

    
    SinhVien dsSinhVien[MAX_STUDENTS];
    int soSinhVien = 0;

    

    fileIn.close();

    // In ra thong tin cac sinh vien
    for (int i = 0; i < soSinhVien; ++i) {
        inThongTinSinhVien(dsSinhVien[i]);
    }

    return 0;
}
