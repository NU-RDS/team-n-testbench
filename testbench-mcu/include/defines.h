#define CAN_BAUDRATE 1000000

// SYSTEM ID: robot finger - 0, robot thumb - 1, haptic finger - 2, haptic thumb - 3
#define SYSTEM_ID 0
#define ODRIVE0_ID 0
#define ODRIVE1_ID 1

#if SYSTEM_ID == 0 || SYSTEM_ID == 2
#define FINGER
#else
#define THUMB
#endif

#if SYSTEM_ID == 0
#define HEARTBEAT_TX_ID 0x100
#define HEARTBEAT_RX_ID 0x102
#define END_EFFECTOR_POS_TX_ID 0x200
#define END_EFFECTOR_POS_RX_ID 0x202
#define END_EFFECTOR_VEL_TX_ID 0x300
#define END_EFFECTOR_VEL_RX_ID 0x302
// #include "robot_description/robot_finger.hpp"
#elif SYSTEM_ID == 1
#define HEARTBEAT_TX_ID 0x101
#define HEARTBEAT_RX_ID 0x103
#define END_EFFECTOR_POS_TX_ID 0x201
#define END_EFFECTOR_POS_RX_ID 0x203
#define END_EFFECTOR_VEL_TX_ID 0x301
#define END_EFFECTOR_VEL_RX_ID 0x303
// #include "robot_description/robot_thumb.hpp"
#elif SYSTEM_ID == 2
#define HEARTBEAT_TX_ID 0x102
#define HEARTBEAT_RX_ID 0x100
#define END_EFFECTOR_POS_TX_ID 0x202
#define END_EFFECTOR_POS_RX_ID 0x200
#define END_EFFECTOR_VEL_TX_ID 0x302
#define END_EFFECTOR_VEL_RX_ID 0x300
// #include "robot_description/haptic_finger.hpp"
#elif SYSTEM_ID == 3
#define HEARTBEAT_TX_ID 0x103
#define HEARTBEAT_RX_ID 0x101
#define END_EFFECTOR_POS_TX_ID 0x203
#define END_EFFECTOR_POS_RX_ID 0x201
#define END_EFFECTOR_VEL_TX_ID 0x303
#define END_EFFECTOR_VEL_RX_ID 0x301
// #include "robot_description/haptic_thumb.hpp"
#else
#error "Invalid SYSTEM_ID"
#endif

#define ESTOP_PIN 5
#define CLEAR_ERROR_BUTTON 2
#define DEADMAN_SWITCH 3
#define RELAY_PIN_OUTPUT 4 // there are 6 of these apparently
#define TEENSY_HEARTBEAT_TIMEOUT 1000
#define ODRIVE_HEARTBEAT_TIMEOUT 1000
#define LED_R1 41
#define LED_G1 40
#define LED_B1 39

#define LED_R2 38
#define LED_G2 37
#define LED_B2 36

#define LED_R3 35
#define LED_G3 34
#define LED_B3 33

// Debugging settings
#define DEBUG
// #define PROFILE
// #define TESTING

#define DEBUG_PIN 10

#ifdef DEBUG
#define db_print(X) Serial.print(X)
#define db_println(X) Serial.println(X)
#define db_printVal(X)  \
    Serial.print(#X);   \
    Serial.print(": "); \
    Serial.println(X, 8)
#define db_pinHigh() digitalWrite(DEBUG_PIN, HIGH)
#define db_pinLow() digitalWrite(DEBUG_PIN, LOW)
#else
#define db_print(X)
#define db_println(X)
#define db_printVal(X)
#define db_pinHigh()
#define db_pinLow()
#endif

#ifdef PROFILE
#define db_startTiming(X)    \
    Serial.print(#X);        \
    Serial.print(" START "); \
    Serial.println(micros())
#define db_endTiming(X)    \
    Serial.print(#X);      \
    Serial.print(" END "); \
    Serial.println(micros())
#define db_timeFunction(X) \
    db_startTiming(X);     \
    X;                     \
    db_endTiming(X)
#define db_startProfiling() Serial.println("START OF PROFILE")
#else
#define db_startTiming(X)
#define db_endTiming(X)
#define db_timeFunction(X) X
#define db_startProfiling()
#endif
