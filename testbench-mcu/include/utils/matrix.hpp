#pragma once
#include <vector>
#include "wiring.h"
#include "stdexcept"

/// @brief Class that treats a std::vector as a matrix and implements simple operations
class Matrix
{
public:
  Matrix() = default;
  ~Matrix() = default;

  Matrix(size_t rows, size_t cols)
  : mRows(rows),
    mCols(cols),
    mData(rows * cols)
  {}

  Matrix(size_t rows, size_t cols, std::vector<float> data)
  : mRows(rows),
    mCols(cols),
    mData(data)
  {}

  float & operator()(size_t i, size_t j)
  {
    return mData.at(i * mCols + j);
  }

  float operator()(size_t i, size_t j) const
  {
    return mData.at(i * mCols + j);
  }

  /// @brief Gets the transpose of the matrix
  Matrix transpose() const
  {
    auto M_T = Matrix{mCols, mRows};
    for (size_t i = 0; i < mRows; ++i) {
      for (size_t j = 0; j < mCols; ++j) {
        M_T(j, i) = mData.at(i * mCols + j);
      }
    }
    return M_T;
  }

  /// @brief Alias for transpose()
  Matrix T() const
  {
    return transpose();
  }

  /// @brief Overloaded multiplication operator for matrix-matrix multiplication
  std::vector<float> operator*(const std::vector<float> & v) const
  {
    if (v.size() != mCols) {
      Serial.println("Matrix multiplication error: vector size does not match matrix columns");
      return {};
    }
    std::vector<float> v_(mRows);
    for (size_t i = 0; i < mRows; ++i) {
      auto sum = 0.f;
      for (size_t j = 0; j < mCols; ++j) {
        sum += v.at(j) * mData.at(i * mCols + j);
      }
      v_.at(i) = sum;
    }
    return v_;
  }

  /// @brief Gets the data vector of the matrix
  std::vector<float> getData() const
  {
    return mData;
  }

  ///@brief Overloaded equality operator that returns true if matrices are equal value-wise
  bool operator==(const Matrix & rhs) const
  {
    return mData == rhs.getData();
  }

private:

  size_t mRows;
  size_t mCols;
  std::vector<float> mData;
};
