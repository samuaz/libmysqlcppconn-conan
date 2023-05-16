from conan import ConanFile, tools
from conan.tools.scm import Git
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps

class mysql_connector_cxxRecipe(ConanFile):
    name = "libmysqlcppconn"
    version = "8.0.33"
    license = "GPL-2.0"
    author = "Samuel Aazcona <samuel@theopencompany.dev>"
    url = "https://github.com/samuaz/libmysqlcppconn-conan"
    homepage = "https://dev.mysql.com/doc/connector-cpp/8.0"
    description = "A Conan package for MySQL Connector/C++ with OpenSSL, Boost, and libmysqlclient"
    topics = ("conan", "mysql", "connector", "cpp", "openssl", "boost", "libmysqlclient", "jdbc", "static")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = ("boost/1.81.0", "openssl/1.1.1t", "libmysqlclient/8.0.31")

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/mysql/mysql-connector-cpp.git", target=".")
        # Please, be aware that using the head of the branch instead of an immutable tag
        # or commit is not a good practice in general
        git.checkout("8.0.33")

    def layout(self):
        cmake_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["WITH_JDBC"] = "ON"
        tc.cache_variables["WITHOUT_SERVER"] = "ON"
        tc.cache_variables["BUILD_STATIC"] = "ON"
        tc.cache_variables["MYSQL_LIB_DIR"] = self.dependencies["libmysqlclient"].cpp_info.aggregated_components().libdirs[0].replace("\\", "/")
        tc.cache_variables["MYSQL_INCLUDE_DIR"] = self.dependencies["libmysqlclient"].cpp_info.aggregated_components().includedirs[0].replace("\\", "/")
        tc.cache_variables["WITH_SSL"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build() 

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["mysqlcppconn-static", "mysqlcppconn8-static"]
        self.cpp_info.system_libs = ["resolv"]
        self.cpp_info.libdirs = ["lib","lib64"]
        self.cpp_info.includedirs = ["include"]

"""     def package_info(self):
        self.cpp_info.libs = ["mysqlcppconn"]
        self.cpp_info.system_libs = ["libmysqlcppconn8"]
        # conan sets libdirs = ["lib"] and includedirs = ["include"] by default
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]            """