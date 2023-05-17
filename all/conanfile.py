from conan import ConanFile, tools
from conan.tools.scm import Git
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building, stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.files import rename, apply_conandata_patches, replace_in_file, rmdir, rm, export_conandata_patches, copy, mkdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

class mysql_connector_cxxRecipe(ConanFile):
    name = "libmysqlcppconn"
    license = "GPL-2.0"
    author = "Samuel Aazcona <samuel@gmail.com>"
    url = "https://github.com/samuaz/libmysqlcppconn-conan"
    homepage = "https://dev.mysql.com/doc/connector-cpp/8.0"
    description = "A Conan package for MySQL Connector/C++ with OpenSSL, Boost, and libmysqlclient"
    topics = ("conan", "mysql", "connector", "cpp", "openssl", "boost", "libmysqlclient", "jdbc", "static")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = ("boost/1.81.0", "openssl/1.1.1t", "libmysqlclient/8.0.31")

    @property
    def _min_cppstd(self):
        return "17" if Version(self.version) >= "8.0.27" else "11"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "7" if Version(self.version) >= "8.0.27" else "5.3",
            "clang": "6",
        }

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        file_name = "mysql-connector-c++"
        cmake_layout(self, src_folder=f"{file_name}-{self.version}-src")

    def validate_build(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross compilation not yet supported by the recipe. Contributions are welcomed.")

    def validate(self):
        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(f"{self.ref} requires {self.settings.compiler} {minimum_version} or newer")

        # I dont have a windows computer to test it
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support windows for now")

        # Sice 8.0.17 this doesn't support shared library on MacOS.
        # https://github.com/mysql/mysql-server/blob/mysql-8.0.17/cmake/libutils.cmake#L333-L335
        if self.settings.compiler == "apple-clang" and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support shared library on apple-clang")

        # mysql < 8.0.29 uses `requires` in source code. It is the reserved keyword in C++20.
        # https://github.com/mysql/mysql-server/blob/mysql-8.0.0/include/mysql/components/services/dynamic_loader.h#L270
        if self.settings.compiler.get_safe("cppstd") == "20" and Version(self.version) < "8.0.29":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support C++20")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_BUILD_TYPE"] = "Release"
        tc.cache_variables["WITH_JDBC"] = "ON"
        tc.cache_variables["WITHOUT_SERVER"] = "ON"
        if self.options.shared == False:
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
        if not self.options.shared:
            stdcpplib = stdcpp_library(self)
            if stdcpplib:
                self.cpp_info.system_libs.append(stdcpplib)
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["m", "resolv"])
        self.cpp_info.names["cmake_find_package"] = "mysqlcppconn"
        self.cpp_info.names["cmake_find_package_multi"] = "mysqlcppconn"
