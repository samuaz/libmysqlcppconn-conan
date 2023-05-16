#pragma once


#ifdef _WIN32
  #define MYSQL_CONNECTOR_CXX_EXPORT __declspec(dllexport)
#else
  #define MYSQL_CONNECTOR_CXX_EXPORT
#endif

MYSQL_CONNECTOR_CXX_EXPORT void mysql_connector_cxx();
