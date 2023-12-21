#include "mfem.hpp"
#include <fstream>
#include <iostream>
#include <string>

using namespace mfem;

std::ostream& operator<<(std::ostream& os, const Vector& v)
{
  os << "{";
  for(int i=0; i<v.Size(); ++i)
  {
    os << v(i);
    if( i+1 < v.Size() ) { os <<","; }
  }

  os << "}";
  return os;
}

int main(int argc, char *argv[])
{
  std::cout << "Simple reproducer for Lagrange 1D bug" << std::endl;

  // Test on several different polynomial orders
  for(int order =1; order < 6; ++order)
  {
    std::cout <<"\nSampling Lagrange1DFiniteElement of order " << order << std::endl;

    Lagrange1DFiniteElement fe(order);

    IntegrationPoint ip;

    // Sample the shape functions at several uniform values inside/outside unit interval
    int N = 10;
    int NX = 5; // extra samples
    for(int i= 0 - NX ; i<= N + NX; ++i)
    {
      ip.x = static_cast<double>(i)/N;
      Vector weights(order+1);
      fe.CalcShape(ip, weights);

      double weightsSum = weights.Sum();  // weights should sum to 1., regardless of value of ip.x

      std::cout<<"\t for sample " << i
        << " with isopar " << ip.x
        << " weights are " << weights
        << " -- sum is " << weightsSum
        << std::endl;
    }
  }

  return 0;
}