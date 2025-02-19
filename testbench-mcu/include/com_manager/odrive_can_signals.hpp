#ifndef ODRIVE_CAN_SIGNALS_H
#define ODRIVE_CAN_SIGNALS_H

#include "teensy_can.h"

//  Number of drives for heartbeat messages
#define NUM_DRIVES 1

//-----------------------------------------------------------------
// END-EFFECTOR MESSAGES
//-----------------------------------------------------------------

// CAN Signals for End-Effector Position
MakeSignedCANSignal(float, 0, 32, 0.0001, 0) end_eff_pos_0_tx{};
MakeSignedCANSignal(float, 32, 32, 0.0001, 0) end_eff_pos_1_tx{};


// Transmit Signals for End-Effector Velocity
MakeSignedCANSignal(float, 0, 32, 0.0001, 0) end_eff_vel_0_tx{};
MakeSignedCANSignal(float, 32, 32, 0.0001, 0) end_eff_vel_1_tx{};


// Receive Signals for End-Effector Position
MakeSignedCANSignal(float, 0, 32, 0.0001, 0) end_eff_pos_0_rx{};
MakeSignedCANSignal(float, 32, 32, 0.0001, 0) end_eff_pos_1_rx{};


// Receive Signals for End-Effector Velocity
MakeSignedCANSignal(float, 0, 32, 0.0001, 0) end_eff_vel_0_rx{};
MakeSignedCANSignal(float, 32, 32, 0.0001, 0) end_eff_vel_1_rx{};


//-----------------------------------------------------------------
// HEARTBEAT MESSAGES (Scaled for NUM_DRIVES drives)
//-----------------------------------------------------------------

// For each drive, define heartbeat signals
#if NUM_DRIVES >= 1
MakeUnsignedCANSignal(bool, 4 + 0*3 + 0, 1, 1, 0) odrive0_heartbeat_active_tx{};
MakeUnsignedCANSignal(bool, 4 + 0*3 + 1, 1, 1, 0) encoder0_active_tx{};
MakeUnsignedCANSignal(bool, 4 + 0*3 + 2, 1, 1, 0) motor0_tx{};
#endif
#if NUM_DRIVES >= 2
MakeUnsignedCANSignal(bool, 4 + 1*3 + 0, 1, 1, 0) odrive1_heartbeat_active_tx{};
MakeUnsignedCANSignal(bool, 4 + 1*3 + 1, 1, 1, 0) encoder1_active_tx{};
MakeUnsignedCANSignal(bool, 4 + 1*3 + 2, 1, 1, 0) motor1_tx{};
#endif
#if NUM_DRIVES >= 3
MakeUnsignedCANSignal(bool, 4 + 2*3 + 0, 1, 1, 0) odrive2_heartbeat_active_tx{};
MakeUnsignedCANSignal(bool, 4 + 2*3 + 1, 1, 1, 0) encoder2_active_tx{};
MakeUnsignedCANSignal(bool, 4 + 2*3 + 2, 1, 1, 0) motor2_tx{};
#endif

MakeUnsignedCANSignal(bool, (4 + NUM_DRIVES * 3), 1, 1, 0) mirror_system_active_tx{};


#if NUM_DRIVES >= 1
MakeUnsignedCANSignal(bool, 4 + 0*3 + 0, 1, 1, 0) odrive0_heartbeat_active_rx{};
MakeUnsignedCANSignal(bool, 4 + 0*3 + 1, 1, 1, 0) encoder0_active_rx{};
MakeUnsignedCANSignal(bool, 4 + 0*3 + 2, 1, 1, 0) motor0_rx{};
#endif
#if NUM_DRIVES >= 2
MakeUnsignedCANSignal(bool, 4 + 1*3 + 0, 1, 1, 0) odrive1_heartbeat_active_rx{};
MakeUnsignedCANSignal(bool, 4 + 1*3 + 1, 1, 1, 0) encoder1_active_rx{};
MakeUnsignedCANSignal(bool, 4 + 1*3 + 2, 1, 1, 0) motor1_rx{};
#endif
#if NUM_DRIVES >= 3
MakeUnsignedCANSignal(bool, 4 + 2*3 + 0, 1, 1, 0) odrive2_heartbeat_active_rx{};
MakeUnsignedCANSignal(bool, 4 + 2*3 + 1, 1, 1, 0) encoder2_active_rx{};
MakeUnsignedCANSignal(bool, 4 + 2*3 + 2, 1, 1, 0) motor2_rx{};
#endif

MakeUnsignedCANSignal(bool, (4 + NUM_DRIVES * 3), 1, 1, 0) mirror_system_active_rx{};


#endif // ODRIVE_CAN_SIGNALS_H
