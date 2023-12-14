#include "mfem.hpp"
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

using namespace mfem;

static void mu_vec_fn(const Vector& x, Vector& V) {
   V = 0.0;
   for (int i = 0; i < std::min(V.Size(), x.Size()); i++) {
      V(i) = x(i) * x(i);
   }
}

int main(int argc, char *argv[]) {
   MPI_Init(&argc, &argv);

   int mpi_rank, mpi_size;
   MPI_Comm_rank(MPI_COMM_WORLD, &mpi_rank);
   MPI_Comm_size(MPI_COMM_WORLD, &mpi_size);

   ParMesh *pmesh = NULL;
   Mesh mesh("/root/mfem-code-analyzer/bugs/issue1230/test.mesh", 1, 1);
   mesh.UniformRefinement();
   mesh.EnsureNCMesh();
   pmesh = new ParMesh(MPI_COMM_WORLD, mesh);

   VectorFunctionCoefficient mu_vec(pmesh->SpaceDimension(), mu_vec_fn);

   int mu_ord = 2;
   FiniteElementCollection *mu_fec = new RT_FECollection(mu_ord, pmesh->Dimension());
   ParFiniteElementSpace *mu_fes = new ParFiniteElementSpace(pmesh, mu_fec, 1, Ordering::byVDIM);

   ParGridFunction gf(mu_fes);
   gf = 0.0;
   gf.ProjectDiscCoefficient(mu_vec, GridFunction::ARITHMETIC);

   std::ostringstream filename;
   filename << "out." << std::setfill('0') << std::setw(6) << mpi_rank;
   std::ofstream gfofs(filename.str().c_str());
   gfofs.precision(8);
   pmesh->Print(gfofs);
   gf.Save(gfofs);
   gfofs.close();

   // 读取并打印文件内容
   if (mpi_rank == 0) {
      std::ifstream file(filename.str());
      std::string line;
      while (std::getline(file, line)) {
         std::cout << line << std::endl;
      }
      file.close();

      std::cout << "程序执行完毕。" << std::endl;
      std::cout << "执行的进程数: " << mpi_size << std::endl;
   }

   delete mu_fes;
   delete mu_fec;
   delete pmesh;

   MPI_Finalize();
   return 0;
}
