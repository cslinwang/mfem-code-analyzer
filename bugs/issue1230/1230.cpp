#include <mfem.hpp>

#include <iostream>
#include <fstream>
#include <sstream>

using namespace mfem;

static void mu_vec_fn(const Vector& x,Vector& V)
{
   V = 0.0;
   for (int i = 0; i < std::min(V.Size(),x.Size()); i++)
   {
      V(i) = x(i)*x(i);
   }
}

int main(int argc, char *argv[])
{
   MPI_Init(&argc,&argv);

   ParMesh *pmesh = NULL;
   Mesh mesh("/root/mfem-code-analyzer/bugs/issue1230/test.mesh", 1, 1);
   mesh.UniformRefinement();
   // if EnsureNCMesh is not called, everything is ok
   mesh.EnsureNCMesh();
   pmesh = new ParMesh(MPI_COMM_WORLD, mesh);

   VectorFunctionCoefficient mu_vec(pmesh->SpaceDimension(),mu_vec_fn);

   int mu_ord = 2;
   FiniteElementCollection *mu_fec = NULL;
   ParFiniteElementSpace *mu_fes = NULL;
   // Both ND and RT fails using EnsureNCMesh
   //mu_fec = new ND_FECollection(mu_ord,pmesh->Dimension());
   mu_fec = new RT_FECollection(mu_ord,pmesh->Dimension());
   mu_fes = new ParFiniteElementSpace(pmesh,mu_fec,1,Ordering::byVDIM);

   ParGridFunction gf(mu_fes);
   gf = 0.0;
   gf.ProjectDiscCoefficient(mu_vec,GridFunction::ARITHMETIC);
   // Using this is always fine
   //gf.ProjectCoefficient(mu_vec);

   int rank;
   MPI_Comm_rank(MPI_COMM_WORLD,&rank);
   std::ostringstream oname;
   oname << "out." << std::setfill('0') << std::setw(6) << rank;

   std::ofstream gfofs(oname.str().c_str());
   gfofs.precision(8);
   pmesh->Print(gfofs);
   gf.Save(gfofs);

   delete mu_fes;
   delete mu_fec;
   delete pmesh;

   MPI_Finalize();
   return 0;
}
