#pragma once
#include <wiring.h>
#include <optional>
#include "utils/helpers.hpp"

/// @brief Possible angle units, radians, degrees, revolutions
enum AngleUnits
{
  RADIANS=0,
  DEGREES=2,
  REVS=3
};

/// \brief Converts an angle from one unit to another.
/// \param ang The angle to convert.
/// \param curr_unit The unit to convert from.
/// \param desr_unit The unit to convert to.
constexpr float convert_angular_units(
  float ang, const AngleUnits curr_unit,
  const AngleUnits desr_unit)
{
  if (curr_unit == AngleUnits::RADIANS && desr_unit == AngleUnits::DEGREES) {
    return ang *= (RAD_TO_DEG);
  }
  if (curr_unit == AngleUnits::RADIANS && desr_unit == AngleUnits::REVS) {
    return ang /= (TWO_PI);
  }
  if (curr_unit == AngleUnits::DEGREES && desr_unit == AngleUnits::RADIANS) {
    return ang *= (DEG_TO_RAD);
  }
  if (curr_unit == AngleUnits::DEGREES && desr_unit == AngleUnits::REVS) {
    return ang /= (360.0f);
  }
  if (curr_unit == AngleUnits::REVS && desr_unit == AngleUnits::RADIANS) {
    return ang *= (TWO_PI);
  }
  if (curr_unit == AngleUnits::REVS && desr_unit == AngleUnits::DEGREES) {
    return ang *= (360.0f);
  }
  return ang;
}

/// \brief Converts a limit from one unit to another.
/// \param angLimits The limit to convert.
/// \param curr_unit The unit to convert from.
/// \param desr_unit The unit to convert to.
constexpr Limits<float> convert_angular_units(
  const Limits<float> & angLimits, const AngleUnits curr_unit,
  const AngleUnits desr_unit)
{
  if (curr_unit == AngleUnits::RADIANS && desr_unit == AngleUnits::DEGREES) {
    return {angLimits.lower * static_cast<float>(RAD_TO_DEG), angLimits.upper * static_cast<float>(RAD_TO_DEG)};
  }
  if (curr_unit == AngleUnits::RADIANS && desr_unit == AngleUnits::REVS) {
    return {angLimits.lower / static_cast<float>(TWO_PI), angLimits.upper / static_cast<float>(TWO_PI)};
  }
  if (curr_unit == AngleUnits::DEGREES && desr_unit == AngleUnits::RADIANS) {
    return {angLimits.lower * static_cast<float>(DEG_TO_RAD), angLimits.upper * static_cast<float>(DEG_TO_RAD)};
  }
  if (curr_unit == AngleUnits::DEGREES && desr_unit == AngleUnits::REVS) {
    return {angLimits.lower / (360.0f), angLimits.upper / (360.0f)};
  }
  if (curr_unit == AngleUnits::REVS && desr_unit == AngleUnits::RADIANS) {
    return {angLimits.lower * static_cast<float>(TWO_PI), angLimits.upper * static_cast<float>(TWO_PI)};
  }
  if (curr_unit == AngleUnits::REVS && desr_unit == AngleUnits::DEGREES) {
    return {angLimits.lower * (360.0f), angLimits.upper * (360.0f)};
  }
  return angLimits;
}
