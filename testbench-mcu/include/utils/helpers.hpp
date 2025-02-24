#ifndef __HELPERS_H__
#define __HELPERS_H__

#pragma once
#include <math.h>
#include <stdexcept>
#include <wiring.h>
#include <iostream>
#include <optional>

/// @brief Compare two floats for equality under a tolerance
/// @param a - The first float
/// @param b - The second float
/// @param tol - The acceptable tolerance, defaults to 1e-6
/// @returns True if the difference of the floats is less than the tolerance, false otherwise
static bool float_close_compare(float a, float b, float tol = 1e-6)
{
    return std::abs(a - b) < tol;
}

/// @brief Compare two {x, y, z} floats for equality under a tolerance
/// @param a - The first {x, y, z}
/// @param b - The second {x, y, z}
/// @param tol - The acceptable tolerance, defaults to 1e-6
/// @returns True if the difference of the floats is less than the tolerance, false otherwise
static bool point_close_compare(std::vector<float> a, std::vector<float> b, float tol = 1e-6)
{
    return std::hypot(b.at(0) - a.at(0), b.at(1) - a.at(1), b.at(2) - a.at(2)) < tol;
}

/// \brief Clamps an input value to a
/// \tparam T - The type of the value to be limited
/// \param input - The variable to limit.
/// \param max_value - The maximum value to limit. If no other value is provided, the negative of this is assumed the minimum value.
/// \param min_value - The minimum value to limit. Defaults to nullopt and uses the negative of the maximum value.
/// \returns the clamped value
template <typename T>
static T limit(T input, const T max_value, const std::optional<T>(min_value) = std::nullopt)
{
    return std::min(std::max(input, min_value.value_or(-1.0 * max_value)), max_value);
}

/// @brief Limit struct to store upper and lower limits
/// @tparam The type of the limit
template <typename T>
struct Limits
{
    T lower;
    T upper;

    T over_limits(T compare) const
    {
        if (compare > upper)
        {
            return compare - upper;
        }
        if (compare < lower)
        {
            return compare - lower;
        }
        return 0.0;
    }
};

/// @brief Special case of the limit function accepting a Limit struct instead.
/// @tparam T - The type of the input
/// @param input - The value to input.
/// @param limits - The limit struct.
/// @returns the clamped value.
template <typename T>
static T limit(T input, Limits<T> limits)
{
    return limit<T>(input, limits.upper, limits.lower);
}
#endif // __HELPERS_H__