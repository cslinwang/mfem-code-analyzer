#include <iostream>
#include "mfem.hpp"

using namespace mfem;

int main()
{
    // Initialize MFEM
    MFEMInitialize();

    // Create a 3D Cartesian mesh
    Mesh mesh(10, 10, 10, Element::HEXAHEDRON);

    // Define boundary attributes
    Array<int> bdr_attributes(mesh.bdr_attributes.Max());

    // Access boundary attributes
    for (int i = 0; i < mesh.GetNumFaces(); ++i)
    {
        if (mesh.GetElementType(i) == Element::QUADRILATERAL)
        {
            int ind = mesh.GetBdrAttribute(i);
            bdr_attributes[ind - 1]++; // Increment the attribute count
        }
    }

    // Print boundary attribute counts
    for (int i = 0; i < bdr_attributes.Size(); ++i)
    {
        std::cout << "Boundary attribute " << i + 1 << ": " << bdr_attributes[i] << " quadrilaterals" << std::endl;
    }

    // Finalize MFEM
    MFEMFinalize();

    return 0;
}
