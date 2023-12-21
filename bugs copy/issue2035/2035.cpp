#include "mfem.hpp"
using namespace mfem;

int main(int argc, char *argv[])
{
   MPI_Init(&argc, &argv);
   const char *mesh_file = "/root/mfem/data/star.mesh";
   Mesh mesh(mesh_file, 1, 1);
   int dim = mesh.Dimension();
   ParMesh pmesh(MPI_COMM_WORLD, mesh);

   FiniteElementCollection *fec = new H1_FECollection(1, dim);
   ParFiniteElementSpace fespace(&pmesh, fec);

   ParBilinearForm a(&fespace);
   a.AddDomainIntegrator(new DiffusionIntegrator);
   a.Assemble();
   OperatorPtr A;
   Array<int> empty;
   a.FormSystemMatrix(empty, A);

   HypreParMatrix * hA = A.As<HypreParMatrix>();
   {
      HypreParMatrix * hAT = hA->Transpose();
      HypreParMatrix * yet_another = Add(1.0, *hA, 0.5, *hAT);
      delete hAT;
      delete yet_another;
   }

   delete fec;
   MPI_Finalize();
   return 0;
}