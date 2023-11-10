#include "mfem.hpp"
#include <iostream>

using namespace mfem;

void transfer_field_distributed(ParGridFunction* source_gf, ParGridFunction* target_gf, double default_value)
{
    *target_gf = default_value;

    const int vdim = source_gf->VectorDim();

    auto source_fes  = source_gf->ParFESpace();
    auto source_mesh = source_fes->GetParMesh();
    const int sdim   = source_mesh->SpaceDimension();

    auto target_fes  = target_gf->ParFESpace();
    auto target_mesh = target_fes->GetParMesh();

    const int target_NE                = target_fes->GetNE();
    const int target_nodes_per_element = target_fes->GetFE(0)->GetNodes().GetNPoints();

    // list of points where the grid function will be evaluated.
    Vector xyz(target_nodes_per_element*target_NE*sdim);
    for (int i = 0; i < target_NE; i++)
    {
        const FiniteElement *fe = target_fes->GetFE(i);
        const IntegrationRule ir = fe->GetNodes();
        ElementTransformation *et = target_fes->GetElementTransformation(i);

        // Obtain a "dimension x nodes per element" matrix with the coordinates in the columns.
        DenseMatrix pos;
        et->Transform(ir, pos);
        for(int d = 0;d < sdim; d++)
        {
            // xyz stores the nodal coordinates by dimension (i.e. XXXXXX...YYYYYY....ZZZZ....). We abuse
            // this to construct a  memory reference into which we write when reading the matrix row.
            Vector row(xyz.GetData() + i*target_nodes_per_element + d*target_NE*target_nodes_per_element, target_nodes_per_element);
            pos.GetRow(d, row);
        }
    }

    const int nodes_cnt = target_nodes_per_element*target_NE;

    // Carrying out interpolation.
    Vector interp_vals(nodes_cnt*vdim);
    FindPointsGSLIB finder(MPI_COMM_WORLD);
    finder.SetDefaultInterpolationValue(NAN);
    finder.Interpolate(*source_mesh, xyz, *source_gf, interp_vals);
    finder.FreeData();

    Array<int> vdofs;
    Vector elem_dof_vals(target_nodes_per_element*vdim);

    // Index helpers.
    // interp_vals stores the values sorted by nodes.
    auto interp_vals_idx = [target_nodes_per_element, target_NE](int element,int node,int component) mutable {
        return component*target_nodes_per_element*target_NE + element*target_nodes_per_element + node;
    };
    // elements also store the values sorted by nodes
    auto elem_dof_idx = [target_nodes_per_element](int node,int component) {
        return target_nodes_per_element*component + node;
    };

    // Transfer interpolation onto target grid function.
    for (int i = 0; i < target_NE; i++)
    {
        target_fes->GetElementVDofs(i, vdofs);

        // Move interpolated values to correct dofs
        int num_nans = 0;
        for (int j = 0; j < target_nodes_per_element; j++)
        {
            for (int d = 0; d < vdim; d++)
            {
                const auto val = interp_vals(interp_vals_idx(i,j,d));
                elem_dof_vals(elem_dof_idx(j,d)) = isnan(val) ? default_value : val;
            }
        }

        // Write the transfered solution into the vdofs
        target_gf->SetSubVector(vdofs, elem_dof_vals);
    }
}


int main(int argc, char *argv[])
{
    Mpi::Init(argc, argv);
    const auto myid = Mpi::WorldRank();
    Hypre::Init();

    const char *mesh_file_src = "../../data/fichera.mesh";
    const char *mesh_file_target = "../../data/beam-hex.mesh";
    int order = 0;
    int fec_type = 3;
    int ref_levels = 0;
    int reorder_mesh = 1;

    OptionsParser args(argc, argv);
    args.AddOption(&mesh_file_src, "-m1", "--mesh_src", "Mesh file to use.");
    args.AddOption(&mesh_file_target, "-m2", "--mesh_target", "Mesh file to use.");
    args.AddOption(&order, "-o", "--order", "Order to generate.");
    args.AddOption(&fec_type, "-t", "--finite-element-type", "0=H1, 1=H(curl), 2=H(div), 3=L2. (default=L2).");
    args.Parse();
    if (!args.Good())
    {
        args.PrintUsage(std::cout);
        return 1;
    }
    args.PrintOptions(std::cout);

    // Load first mesh
    Mesh *mesh = new Mesh(mesh_file_src, 1, 1);
    mesh->EnsureNodes();
    const int dim = mesh->Dimension();
    const int sdim = mesh->SpaceDimension();
    auto mesh_src = ParMesh(MPI_COMM_WORLD, *mesh);
    delete mesh;

    // Load second mesh
    mesh = new Mesh(mesh_file_target, 1, 1);
    mesh->EnsureNodes();
    auto mesh_target = ParMesh(MPI_COMM_WORLD, *mesh);
    delete mesh;

    // Choose FE spaces
    auto fec = [&]()->FiniteElementCollection*{
        switch(fec_type)
        {
            case 0:
                return new H1_FECollection(order, dim);
            case 1:
                return new ND_FECollection(order, dim);
            case 2:
                return new RT_FECollection(order, dim);
            default:
            case 3:
                return new L2_FECollection(order, dim);
        }
    }();

    if(fec_type != 1 && fec_type != 2)
    {
        if(myid == 0) std::cout << "Scalar transfer." << std::endl;

        auto fes_src = ParFiniteElementSpace(&mesh_src, fec);
        auto gf_src = ParGridFunction(&fes_src);
        auto fes_target = ParFiniteElementSpace(&mesh_target, fec);
        auto gf_target = ParGridFunction(&fes_target);

        auto coeff = FunctionCoefficient([](const Vector& X)
        {
            return X.Norml2();
        });
        gf_src.ProjectCoefficient(coeff);
        mesh_src.SaveAsOne("source.mesh");
        gf_src.SaveAsOne("source.gf");

        // Transfer forth ...
        transfer_field_distributed(&gf_src, &gf_target, 0.0);
        mesh_target.SaveAsOne("target.mesh");
        gf_target.SaveAsOne("target.gf");

        // ... and back.
        transfer_field_distributed(&gf_target, &gf_src, 0.0);
        gf_src.SaveAsOne("source_again.gf");
    }

    // Project some vortex onto the mesh
    if(myid == 0) std::cout << "Vector transfer by nodes." << std::endl;
    {
        auto fes_src = ParFiniteElementSpace(&mesh_src, fec, dim, Ordering::byNODES);
        auto gf_src = ParGridFunction(&fes_src);
        auto fes_target = ParFiniteElementSpace(&mesh_target, fec, dim, Ordering::byNODES);
        auto gf_target = ParGridFunction(&fes_target);

        auto coeff = VectorFunctionCoefficient(dim, [&dim](const Vector& X, Vector& Y)
        {
            Y(0) = X(1);
            Y(1) = -X(0);
            if(dim>2) Y(2) = X(2)*X(2);
        });

        gf_src.ProjectCoefficient(coeff);
        gf_src.SaveAsOne("source_v1.gf");

        // Transfer forth ...
        transfer_field_distributed(&gf_src, &gf_target, 0.0);
        gf_target.SaveAsOne("target_v1.gf");

        // ... and back.
        transfer_field_distributed(&gf_target, &gf_src, 0.0);
        gf_src.SaveAsOne("source_again_v1.gf");
    }
    if(myid == 0) std::cout << "Vector transfer by vdim." << std::endl;
    {
        auto fes_src = ParFiniteElementSpace(&mesh_src, fec, dim, Ordering::byVDIM);
        auto gf_src = ParGridFunction(&fes_src);
        auto fes_target = ParFiniteElementSpace(&mesh_target, fec, dim, Ordering::byVDIM);
        auto gf_target = ParGridFunction(&fes_target);

        auto coeff = VectorFunctionCoefficient(dim, [&dim](const Vector& X, Vector& Y)
        {
            Y(0) = X(1);
            Y(1) = -X(0);
            if(dim>2) Y(2) = X(2)*X(2);
        });

        gf_src.ProjectCoefficient(coeff);
        gf_src.SaveAsOne("source_v2.gf");

        // Transfer forth ...
        transfer_field_distributed(&gf_src, &gf_target, 0.0);
        gf_target.SaveAsOne("target_v2.gf");

        // ... and back.
        transfer_field_distributed(&gf_target, &gf_src, 0.0);
        gf_src.SaveAsOne("source_again_v2.gf");
    }

    delete fec;

    return 0;
}