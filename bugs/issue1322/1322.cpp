#include "mfem.hpp"
#include <fstream>
#include <iostream>

using namespace std;
using namespace mfem;

int main(int argc, char *argv[])
{

   // 1. Parse command-line options.
   const char *device_config = "cpu";

   OptionsParser args(argc, argv);
   args.AddOption(&device_config, "-d", "--device",
                  "Device configuration string, see Device::Configure().");

   args.Parse();
   if (!args.Good())
   {
      args.PrintUsage(cout);
      return 1;
   }
   args.PrintOptions(cout);

   // 2. Enable hardware devices such as GPUs, and programming models such as
   //    CUDA, OCCA, RAJA and OpenMP based on command line options.
   Device device(device_config);
   device.Print();

   // Set-up mesh and finite element space

   int dim = 3;
   Mesh *mesh;
   // Making this mesh and test real simple with 8 elements and then a cubic element
   mesh = new Mesh(2, 2, 2, Element::HEXAHEDRON, 0, 1.0, 1.0, 1.0, false);
   int order = 1;
   int order_0 = 0;
   H1_FECollection fec(order, dim);
   L2_FECollection l2_fec(order_0, dim);

   FiniteElementSpace l2_fes(mesh, &l2_fec, dim);
   GridFunction grid_test(&l2_fes);

   Vector coeff(3);
   coeff[0] = 0.0;
   coeff[1] = 1.0;
   coeff[2] = 2.0;

   //This line is needed or else it fails when the fes->fe(i)->Project method is called
   coeff.HostReadWrite();

   VectorConstantCoefficient vec_coeff(coeff);
   //grid_test.HostReadWrite(); // This line doesn't appear to help any.
   grid_test.ProjectDiscCoefficient(vec_coeff, mfem::GridFunction::ARITHMETIC);

   delete mesh;
}