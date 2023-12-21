// file lobpcg.cpp
#include "mfem.hpp"
#include <iostream>
using namespace std;
using namespace mfem;

int main(int argc, char *argv[]) {
   int num_procs, myid;
   MPI_Init(&argc, &argv);
   MPI_Comm_size(MPI_COMM_WORLD, &num_procs);
   MPI_Comm_rank(MPI_COMM_WORLD, &myid);

   int order = 1;
   int nev = 5;

   Mesh *mesh = new Mesh(10, 10, Element::QUADRILATERAL, 1);
   int dim = mesh->Dimension();

   ParMesh *pmesh = new ParMesh(MPI_COMM_WORLD, *mesh);
   delete mesh;

   FiniteElementCollection *fec = new H1_FECollection(order, dim);
   ParFiniteElementSpace *fespace = new ParFiniteElementSpace(pmesh, fec);
   HYPRE_Int size = fespace->GlobalTrueVSize();
   if (myid == 0)
      cout << "Number of unknowns: " << size << endl;

   ConstantCoefficient one(1.0);
   Array<int> ess_bdr;
   if (pmesh->bdr_attributes.Size()) {
      ess_bdr.SetSize(pmesh->bdr_attributes.Max());
      ess_bdr = 1;
   }

   ParBilinearForm *a = new ParBilinearForm(fespace);
   a->AddDomainIntegrator(new DiffusionIntegrator(one));
   if (pmesh->bdr_attributes.Size() == 0)
      a->AddDomainIntegrator(new MassIntegrator(one));
   a->Assemble();
   a->EliminateEssentialBCDiag(ess_bdr, 1.0);
   a->Finalize();

   ParBilinearForm *m = new ParBilinearForm(fespace);
   m->AddDomainIntegrator(new MassIntegrator(one));
   m->Assemble();
   // shift the eigenvalue corresponding to eliminated dofs to a large value
   m->EliminateEssentialBCDiag(ess_bdr, numeric_limits<double>::min());
   m->Finalize();

   HypreParMatrix *A = a->ParallelAssemble();
   HypreParMatrix *M = m->ParallelAssemble();

   delete a;
   delete m;

   HypreBoomerAMG * amg = new HypreBoomerAMG(*A);
   amg->SetPrintLevel(0);

   HypreLOBPCG * lobpcg = new HypreLOBPCG(MPI_COMM_WORLD);
   lobpcg->SetNumModes(nev);
   lobpcg->SetPreconditioner(*amg);
   lobpcg->SetMaxIter(100);
   lobpcg->SetTol(1e-8);
   lobpcg->SetPrecondUsageMode(1);
   lobpcg->SetPrintLevel(1);
   lobpcg->SetMassMatrix(*M);
   lobpcg->SetOperator(*A);

   Array<double> eigenvalues;
   lobpcg->Solve();
   lobpcg->GetEigenvalues(eigenvalues);
   ParGridFunction x(fespace);

   delete lobpcg;
   delete amg;
   delete M;
   delete A;

   delete fespace;
   delete fec;
   delete pmesh;

   MPI_Finalize();
   return 0;
}