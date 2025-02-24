#pragma once
#include <Arduino.h>
#include "defines.h"

/// @brief Color struct for RGB values
struct Color
{
  bool r;
  bool g;
  bool b;
};

// Red 1, 0, 0
// Green 0, 1, 0
// Blue 0, 0, 1
// Yellow 1, 1, 0
// Cyan 0, 1, 1
// Magenta 1, 0, 1
// White 1, 1, 1
Color red = Color{1, 0, 0};
Color green = Color{0, 1, 0};
Color blue = Color{0, 0, 1};
Color yellow = Color{1, 1, 0};
Color cyan = Color{0, 1, 1};
Color magenta = Color{1, 0, 1};
Color white = Color{1, 1, 1};
Color off = Color{0, 0, 0};

/// \brief Sets the color for the data board LEDs using color struct
/// \param idx - LED to change colour
/// \param color - color to set the LED
void setColor(int idx, Color color)
{
  switch (idx) {
    case 1:
      digitalWrite(LED_R1, color.r);
      digitalWrite(LED_G1, color.g);
      digitalWrite(LED_B1, color.b);
      break;
    case 2:
      digitalWrite(LED_R2, color.r);
      digitalWrite(LED_G2, color.g);
      digitalWrite(LED_B2, color.b);
      break;
    case 3:
      digitalWrite(LED_R3, color.r);
      digitalWrite(LED_G3, color.g);
      digitalWrite(LED_B3, color.b);
      break;
  }
}

/// \brief Sets the color for the data board LEDs using rgb values
/// \param idx - LED to change color
/// \param r - value of red 
/// \param g - value of green
/// \param b - value of blue
void setColor(int idx, bool r, bool g, bool b)
{
  switch (idx) {
    case 1:
      digitalWrite(LED_R1, r);
      digitalWrite(LED_G1, g);
      digitalWrite(LED_B1, b);
      break;
    case 2:
      digitalWrite(LED_R2, r);
      digitalWrite(LED_G2, g);
      digitalWrite(LED_B2, b);
      break;
    case 3:
      digitalWrite(LED_R3, r);
      digitalWrite(LED_G3, g);
      digitalWrite(LED_B3, b);
      break;
  }
}

/// \brief Sets the pins for the LEDs as output
void ledSetup()
{
  //   pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LED_R1, OUTPUT);
  pinMode(LED_R2, OUTPUT);
  pinMode(LED_R3, OUTPUT);
  pinMode(LED_G1, OUTPUT);
  pinMode(LED_G2, OUTPUT);
  pinMode(LED_G3, OUTPUT);
  pinMode(LED_B1, OUTPUT);
  pinMode(LED_B2, OUTPUT);
  pinMode(LED_B3, OUTPUT);
}
