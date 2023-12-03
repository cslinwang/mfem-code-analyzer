
#include "mfem.hpp"
#include <fstream>
#include <iostream>
#ifdef __GNUC__
extern "C" void __gcov_flush(void);
#endif

using namespace std;
using namespace mfem;

int main(int argc, char *argv[])
{
   MPI_Session mpi;
   int num_procs = mpi.WorldSize();
   int myid = mpi.WorldRank();

   // 1. Parse command-line options.
   const char *mesh_file = "/root/mfem-code-analyzer/bugs/issue2809/lshape.mesh";
   int order = 2;

   Mesh mesh(mesh_file, 1, 1);
   int dim = mesh.Dimension();

   mesh.UniformRefinement();
   mesh.EnsureNCMesh();

   ParMesh pmesh(MPI_COMM_WORLD, mesh);
   mesh.Clear();

   for (int i = 0; i<4; i++)
   {
      Array<int> elements_to_refine;

      if (myid == 0)
      {
         if (i == 0)
         {
            elements_to_refine.Append(2);
         }
         else if (i == 1)
         {
            elements_to_refine.Append(4);
         }
         else if (i == 2)
         {
            elements_to_refine.Append(6);
         }
         else
         {
            elements_to_refine.Append(8);
         }
      }
      else if (myid == 1)
      {
         if (i == 0)
         {
            elements_to_refine.Append(2);
         }
         else if (i == 1)
         {
            elements_to_refine.Append(3);
         }
         else if (i == 2)
         {
            elements_to_refine.Append(4);
         }
         else
         {
            elements_to_refine.Append(5);
         }
      }
      else if (myid == 2)
      {

      }
      else
      {
         if (i == 0)
         {
            elements_to_refine.Append(2);
         }
         else if (i == 1)
         {
            elements_to_refine.Append(3);
         }
         else if (i == 2)
         {
            elements_to_refine.Append(4);
         }
         else
         {
            elements_to_refine.Append(5);
         }
      }
      pmesh.GeneralRefinement(elements_to_refine);
   }


   L2_FECollection u_fec(order-1,dim);
   RT_Trace_FECollection hatsigma_fec(order-1,dim);

   Array<ParFiniteElementSpace * > fes;

   fes.Append(new ParFiniteElementSpace(&pmesh,&hatsigma_fec));
   fes.Append(new ParFiniteElementSpace(&pmesh,&u_fec));


   int nblocks = fes.Size();

   HypreParMatrix * Pi = fes[0]->Dof_TrueDof_Matrix();
   HypreParMatrix * Pj = fes[1]->Dof_TrueDof_Matrix();

   SparseMatrix * temp = new SparseMatrix(fes[0]->GetVSize(),
                                          fes[1]->GetVSize());
   temp->Finalize();

   HypreParMatrix * A = new HypreParMatrix(MPI_COMM_WORLD, fes[0]->GlobalVSize(),
                           fes[1]->GlobalVSize(), fes[0]->GetDofOffsets(),
                           fes[1]->GetDofOffsets(), temp);

   HypreParMatrix * PtAP = RAP(Pi,A,Pj);

   // HypreParMatrix *APj = ParMult(A,Pj,true);
   // HypreParMatrix *Pt = Pi->Transpose();
   // HypreParMatrix * PtAP = ParMult(Pt,APj,true);
   // delete Pt;
   // delete APj;
   __gcov_flush(); // 强制写入覆盖率数据
   delete PtAP;
   delete A;
   delete temp;

   for (int i = 0; i<nblocks; i++)
   {
      __gcov_flush(); // 强制写入覆盖率数据
      delete fes[i];
      fes[i]=nullptr;
   }
   __gcov_flush(); // 强制写入覆盖率数据
   return 0;
}
