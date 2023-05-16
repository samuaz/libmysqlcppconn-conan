#include <iostream>
#include <mysql/jdbc.h>
#include <jdbc/mysql_driver.h>
#include <jdbc/cppconn/driver.h>
#include <jdbc/cppconn/exception.h>

int main() {
    try {
        sql::Driver *driver = sql::mysql::get_driver_instance();;
        std::unique_ptr<sql::Connection> con(driver->connect("tcp://127.0.0.1:3306", "root", "password"));

        std::cout << "Connection successful!" << std::endl;
    } catch (sql::SQLException &e) {
        std::cerr << "Error connecting to MySQL: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}