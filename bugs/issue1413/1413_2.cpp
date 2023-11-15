#include "mfem.hpp"
using namespace mfem;
int main(int argc, char *argv[])
{
    int num_procs, myid;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &num_procs);
    MPI_Comm_rank(MPI_COMM_WORLD, &myid);

    const char *mesh_file = "beam-quad.mesh";

    Mesh *mesh = new Mesh(mesh_file, 1, 1);
    int dim = mesh->Dimension();
    int ref_levels = 5;
    for (int l = 0; l < ref_levels; l++) {
        mesh->UniformRefinement();
    }

    ParMesh *pmesh = new ParMesh(MPI_COMM_WORLD, *mesh);
    delete mesh;

    auto h1_fec = std::make_shared<H1_FECollection>(1, dim);
    auto h1_fespace =
        std::make_shared<ParFiniteElementSpace>(pmesh, h1_fec.get());
    auto h1_fespace_flux =
        std::make_shared<ParFiniteElementSpace>(pmesh, h1_fec.get(), dim);

    Vector flux_vec(2);
    flux_vec(0) = 1.0;
    flux_vec(1) = 1.0;
    VectorConstantCoefficient flux_coeff(flux_vec);

    ParGridFunction flux_func(h1_fespace_flux.get());
    flux_func.ProjectCoefficient(flux_coeff);

    VectorGridFunctionCoefficient flux_coef_vec(&flux_func);

    Array<int> flux_bdr(pmesh->bdr_attributes.Max());
    flux_bdr = 0;
    flux_bdr[1] = 1;

    auto flux_lf = std::make_shared<ParLinearForm>(h1_fespace.get());
    flux_lf->AddBoundaryIntegrator(new BoundaryNormalLFIntegrator(flux_coef_vec), flux_bdr);
    flux_lf->Assemble();
    ParGridFunction one_gf(h1_fespace.get());
    ConstantCoefficient onecoeff(1.0);
    one_gf.ProjectCoefficient(onecoeff);
    double flux = flux_lf->operator()(one_gf);
    std::cout << "flux value: " << flux << std::endl;
    delete pmesh;
}