// Copyright (c) 2010-2021, Lawrence Livermore National Security, LLC. Produced
// at the Lawrence Livermore National Laboratory. All Rights reserved. See files
// LICENSE and NOTICE for details. LLNL-CODE-806117.
//
// This file is part of the MFEM library. For more information and source code
// availability visit https://mfem.org.
//
// MFEM is free software; you can redistribute it and/or modify it under the
// terms of the BSD-3 license. We welcome feedback and contributions, see file
// CONTRIBUTING.md for details.

#include "unit_tests.hpp"
#include "mfem.hpp"
#include <fstream>
#include <iostream>
#ifdef __GNUC__
extern "C" void __gcov_flush(void);
#endif

using namespace mfem;

namespace assembly_levels
{

enum class Problem { Mass,
                     Convection,
                     Diffusion
                   };

std::string getString(Problem pb)
{
   switch (pb)
   {
      case Problem::Mass:
         return "Mass";
         break;
      case Problem::Convection:
         return "Convection";
         break;
      case Problem::Diffusion:
         return "Diffusion";
         break;
   }
   MFEM_ABORT("Unknown Problem.");
   return "";
}

std::string getString(AssemblyLevel assembly)
{
   switch (assembly)
   {
      case AssemblyLevel::NONE:
         return "None";
         break;
      case AssemblyLevel::PARTIAL:
         return "Partial";
         break;
      case AssemblyLevel::ELEMENT:
         return "Element";
         break;
      case AssemblyLevel::FULL:
         return "Full";
         break;
      case AssemblyLevel::LEGACY:
         return "Legacy";
         break;
   }
   MFEM_ABORT("Unknown assembly level.");
   return "";
}

void velocity_function(const Vector &x, Vector &v)
{
   int dim = x.Size();
   switch (dim)
   {
      case 1: v(0) = 1.0; break;
      case 2: v(0) = x(1); v(1) = -x(0); break;
      case 3: v(0) = x(1); v(1) = -x(0); v(2) = x(0); break;
   }
}

void AddConvectionIntegrators(BilinearForm &k, VectorCoefficient &velocity,
                              bool dg)
{
   k.AddDomainIntegrator(new ConvectionIntegrator(velocity, -1.0));

   if (dg)
   {
      k.AddInteriorFaceIntegrator(
         new TransposeIntegrator(new DGTraceIntegrator(velocity, 1.0, -0.5)));
      k.AddBdrFaceIntegrator(
         new TransposeIntegrator(new DGTraceIntegrator(velocity, 1.0, -0.5)));
   }
}

void test_assembly_level(const char *meshname, int order, bool dg,
                         const Problem pb, const AssemblyLevel assembly)
{
   INFO("mesh=" << meshname << ", order=" << order << ", DG=" << dg
        << ", pb=" << getString(pb) << ", assembly=" << getString(assembly));
   Mesh mesh(meshname, 1, 1);
   mesh.EnsureNodes();
   int dim = mesh.Dimension();

   FiniteElementCollection *fec;
   if (dg)
   {
      fec = new L2_FECollection(order, dim, BasisType::GaussLobatto);
   }
   else
   {
      fec = new H1_FECollection(order, dim);
   }

   FiniteElementSpace fespace(&mesh, fec);

   BilinearForm k_test(&fespace);
   BilinearForm k_ref(&fespace);

   ConstantCoefficient one(1.0);
   VectorFunctionCoefficient vel_coeff(dim, velocity_function);

   switch (pb)
   {
      case Problem::Mass:
         k_ref.AddDomainIntegrator(new MassIntegrator(one));
         k_test.AddDomainIntegrator(new MassIntegrator(one));
         break;
      case Problem::Convection:
         AddConvectionIntegrators(k_ref, vel_coeff, dg);
         AddConvectionIntegrators(k_test, vel_coeff, dg);
         break;
      case Problem::Diffusion:
         k_ref.AddDomainIntegrator(new DiffusionIntegrator(one));
         k_test.AddDomainIntegrator(new DiffusionIntegrator(one));
         break;
   }

   k_ref.Assemble();
   k_ref.Finalize();

   k_test.SetAssemblyLevel(assembly);
   k_test.Assemble();

   GridFunction x(&fespace), y_ref(&fespace), y_test(&fespace);

   x.Randomize(1);

   // Test Mult
   k_ref.Mult(x,y_ref);
   k_test.Mult(x,y_test);

   y_test -= y_ref;

   REQUIRE(y_test.Norml2() < 1.e-12);

   // Test MultTranspose
   k_ref.MultTranspose(x,y_ref);
   k_test.MultTranspose(x,y_test);

   y_test -= y_ref;

   REQUIRE(y_test.Norml2() < 1.e-12);

   delete fec;
}

TEST_CASE("H1 Assembly Levels", "[AssemblyLevel], [PartialAssembly]")
{
   const bool dg = false;
   auto pb = GENERATE(Problem::Mass,Problem::Convection,Problem::Diffusion);
   auto assembly = GENERATE(AssemblyLevel::PARTIAL, AssemblyLevel::ELEMENT,
                            AssemblyLevel::FULL);

   SECTION("Conforming")
   __gcov_flush(); // 强制写入覆盖率数据
   {
      SECTION("2D")
      {
         __gcov_flush(); // 强制写入覆盖率数据
         auto order = GENERATE(2, 3);
         test_assembly_level("../../data/periodic-square.mesh",
                             order, dg, pb, assembly);
         test_assembly_level("../../data/periodic-hexagon.mesh",
                             order, dg, pb, assembly);
         test_assembly_level("../../data/star-q3.mesh",
                             order, dg, pb, assembly);
      }

      SECTION("3D")
      {
         int order = 2;
         test_assembly_level("../../data/periodic-cube.mesh",
                             order, dg, pb, assembly);
         test_assembly_level("../../data/fichera-q3.mesh",
                             order, dg, pb, assembly);
      }
   }

   SECTION("Nonconforming")
   {
      // Test AMR cases (DG not implemented)
      SECTION("AMR 2D")
      {
         auto order = GENERATE(2, 3);
         test_assembly_level("../../data/amr-quad.mesh",
                             order, dg, pb, assembly);
      }
      SECTION("AMR 3D")
      {
         int order = 2;
         test_assembly_level("../../data/fichera-amr.mesh",
                             order, dg, pb, assembly);
      }
   }
} // test case

TEST_CASE("L2 Assembly Levels", "[AssemblyLevel], [PartialAssembly]")
{
   const bool dg = true;
   auto pb = GENERATE(Problem::Mass,Problem::Convection);

   SECTION("Conforming")
   {
      auto assembly = GENERATE(AssemblyLevel::PARTIAL,
                               AssemblyLevel::ELEMENT,
                               AssemblyLevel::FULL);

      SECTION("2D")
      {
         auto order = GENERATE(2, 3);
         test_assembly_level("../../data/periodic-square.mesh",
                             order, dg, pb, assembly);
         test_assembly_level("../../data/periodic-hexagon.mesh",
                             order, dg, pb, assembly);
         test_assembly_level("../../data/star-q3.mesh",
                             order, dg, pb, assembly);
      }

      SECTION("3D")
      {
         int order = 2;
         test_assembly_level("../../data/periodic-cube.mesh",
                             order, dg, pb, assembly);
         test_assembly_level("../../data/fichera-q3.mesh",
                             order, dg, pb, assembly);
      }
   }

   SECTION("Nonconforming")
   {
      // Full assembly DG not implemented on NCMesh
      auto assembly = GENERATE(AssemblyLevel::PARTIAL,
                               AssemblyLevel::ELEMENT);

      SECTION("AMR 2D")
      {
         auto order = GENERATE(2, 3);
         test_assembly_level("../../data/amr-quad.mesh",
                             order, dg, pb, assembly);
      }
      SECTION("AMR 3D")
      {
         int order = 2;
         test_assembly_level("../../data/fichera-amr.mesh",
                             order, dg, pb, assembly);
      }
   }
} // test case

} // namespace assembly_levels
