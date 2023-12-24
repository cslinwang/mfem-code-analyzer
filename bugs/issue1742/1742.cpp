#include "mfem.hpp"
#include <iostream>

using namespace std;
using namespace mfem;

int main() {
    try {
        // 尝试加载一个不存在的网格文件
        Mesh mesh("nonexistent.mesh");
    } catch (const std::exception &ex) {
        // 捕获并打印异常信息
        cout << "Caught exception: " << ex.what() << endl;
    }
    return 0;
}
