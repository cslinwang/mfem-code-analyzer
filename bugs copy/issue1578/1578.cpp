#include "mfem.hpp"
#include <iostream>

using namespace std;
using namespace mfem;

int main(int argc, char *argv[])
{
    const int vSize = 10;
    Vector v;
    v.UseDevice(true);
    v.SetSize(vSize);
    v = 0.0;

    cout << "IsHost(v) = " << IsHostMemory(v.GetMemory().GetMemoryType()) << endl;

    Vector w;
    w.MakeRef(v, 0, vSize);

    cout << "IsHost(w) = " << IsHostMemory(w.GetMemory().GetMemoryType()) << endl;

    auto hv = v.HostWrite();
    for (int j = 0; j < vSize; j++) { hv[j] = 1.0; }

    cout << "IsHost(v) = " << IsHostMemory(v.GetMemory().GetMemoryType()) << endl;
    cout << "IsHost(w) = " << IsHostMemory(w.GetMemory().GetMemoryType()) << endl;

    Vector z;
    z.UseDevice(true);
    z.SetSize(vSize);
    auto dz = z.Write();
    auto dw = w.Read();

    MFEM_FORALL(i, vSize,
    {
        dz[i] = dw[i];
    });

    z.HostRead();
    cout << "norm(z) = " << z.Norml2() << endl;

    dz = z.Write();
    auto dv = v.Read();

    MFEM_FORALL(i, vSize,
    {
        dz[i] = dv[i];
    });

    z.HostRead();
    cout << "norm(z) = " << z.Norml2() << endl;

    return 0;
}
