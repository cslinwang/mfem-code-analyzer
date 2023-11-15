#include "mfem.hpp"
#include <mpi.h>
#include <iostream>

int main(int argc, char *argv[])
{
   MPI_Init(&argc, &argv);

   // Make a mesh
   mfem::Mesh mesh(10, 10, mfem::Element::QUADRILATERAL, 1,
                   1.0, 1.0);
   mesh.EnsureNCMesh();

   // Make it into a parallel mesh
   mfem::ParMesh pmesh(MPI_COMM_WORLD, mesh);
   std::cout << "After creation : Boundary attribute size: " << pmesh.bdr_attributes.Size() << std::endl;

   // Perform a refinement of every element
   pmesh.UniformRefinement();
   std::cout << "After refinement : Boundary attribute size: " << pmesh.bdr_attributes.Size() << std::endl;

   // Perform a derefinement of every element
   mfem::Vector error_indicator(pmesh.GetNE());
   error_indicator = 0.0; // Zero out indicator to force de-refinement everywhere
   pmesh.DerefineByError(error_indicator, 1.0, 1);
   std::cout << "After derefinement : Boundary attribute size: " <<  pmesh.bdr_attributes.Size() << std::endl;

   MPI_Finalize();
   return 0;
}