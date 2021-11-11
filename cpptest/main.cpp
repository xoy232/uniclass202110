#include <boost/version.hpp>  //包含 Boost 標頭檔案
#include <boost/config.hpp>  //包含 Boost 標頭檔案
#include <boost/python.hpp>
#include <iostream>

using namespace std;

int main()
{
    cout << BOOST_VERSION << endl;  //Boost 版本號
    cout << BOOST_LIB_VERSION << endl;  //Boost 版本號
    cout << BOOST_PLATFORM << endl;  //作業系統
    cout << BOOST_COMPILER << endl;  //編譯器
    cout << BOOST_STDLIB << endl;  //標準庫

    return 0;
}