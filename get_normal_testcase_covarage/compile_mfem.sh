#!/bin/bash

full_sha="${1:-93393c5c58ecaa3eb6fb9bbd6a822e7c3fd96be5}"

cd /root/mfem

# 编译
rm -rf build
mkdir build
cd build
cmake ..
make exec -j $(nproc)
make install

cd tests
make -j $(nproc)
