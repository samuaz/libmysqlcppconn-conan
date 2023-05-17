cmake_minimum_required(VERSION 3.15)
project(MySQLConnectorCPPTest CXX)

find_package(libmysqlcppconn REQUIRED CONFIG)
add_executable(example src/test_package.cpp)
target_link_libraries(example libmysqlcppconn::libmysqlcppconn)

