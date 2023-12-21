#include "mfem.hpp"
#include <fstream>
#include <iostream>

using namespace std;
using namespace mfem;

int main(int argc, char *argv[])
{
   // 1. Initialize MPI.
   int num_procs, myid;
   MPI_Init(&argc, &argv);
   MPI_Comm_size(MPI_COMM_WORLD, &num_procs);
   MPI_Comm_rank(MPI_COMM_WORLD, &myid);

   // 2. Parse command-line options.
   const char *mesh_file = "../data/star-hilbert.mesh";

   OptionsParser args(argc, argv);
   args.AddOption(&mesh_file, "-m", "--mesh", "Mesh file to use.");
   args.Parse();
   if (!args.Good())
   {
      if (myid == 0)
      {
         args.PrintUsage(cout);
      }
      MPI_Finalize();
      return 1;
   }

   // 3. Read the (serial) mesh from the given mesh file on all processors.  We
   //    can handle triangular, quadrilateral, tetrahedral, hexahedral, surface
   //    and volume meshes with the same code.
   Mesh *mesh = new Mesh(mesh_file, 1, 1);
   int dim = mesh->Dimension();
   int sdim = mesh->SpaceDimension();

   // 4. Project a NURBS mesh to a piecewise-quadratic curved mesh. Make sure
   //    that the mesh is non-conforming if it has quads or hexes and refine it.
   mesh->EnsureNCMesh(true);
   // Make sure tet-only meshes are marked for local refinement.
   mesh->Finalize(true);

   // 5. Define a parallel mesh by partitioning the serial mesh.  Once the
   //    parallel mesh is defined, the serial mesh can be deleted.
   ParMesh pmesh(MPI_COMM_WORLD, *mesh);
   delete mesh;

   // pmesh.ExchangeFaceNbrData(); // <- works

   // 6. Do any refinement ...
   pmesh.RandomRefinement(0.25);

   // ... to crash this
   pmesh.ExchangeFaceNbrData();

   // 7. Exit
   MPI_Finalize();
   return 0;
}