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
    const char *mesh_file = "./data/star.mesh";
    int order = 1;

    // Get parmesh
    Mesh *mesh = new Mesh(mesh_file, 1, 1);
    int dim = mesh->Dimension();
    int ref_levels = 1;
    for (int l = 0; l < ref_levels; l++) {
        mesh->UniformRefinement();
    }
    ParMesh *pmesh = new ParMesh(MPI_COMM_WORLD, *mesh);
    delete mesh;

    // Finite element spaces
    L2_FECollection *l2_coll = new L2_FECollection(order, dim);
    ParFiniteElementSpace *dg_space = new ParFiniteElementSpace(pmesh, l2_coll);
    H1_FECollection *h1_coll = new H1_FECollection(order+1, dim);
    ParFiniteElementSpace *h1_space = new ParFiniteElementSpace(pmesh, h1_coll, dim); // dim copies of H1

    // Hypre matrices
    ParBilinearForm* mass_dg = new ParBilinearForm(dg_space);
    mass_dg->AddDomainIntegrator(new MassIntegrator());
    mass_dg->Assemble();
    mass_dg->Finalize();
    HypreParMatrix* Ma = mass_dg->ParallelAssemble();

    ParMixedBilinearForm* div = new ParMixedBilinearForm(h1_space, dg_space);
    div->AddDomainIntegrator(new VectorDivergenceIntegrator);
    div->Assemble();
    div->Finalize();
    HypreParMatrix* D = div->ParallelAssemble();
    HypreParMatrix* Dt = D->Transpose();

    // get schur complement S = Ma - D*G
    HypreParMatrix* DG = ParMult(D, Dt);
    // TODO : BELOW BOTH OF THE ADD FUNCTIONS SEG FAULT WITH MORE THAN ONE PROCESSOR
    // HypreParMatrix *S = Add(1., *Ma, -1., *DG);
    HypreParMatrix *S = ParAdd(Ma, DG);

    // clean up pointers...
}