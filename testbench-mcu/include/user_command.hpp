#ifndef __USER_COMMAND_H__
#define __USER_COMMAND_H__

#include <Arduino.h>

#include <memory>
#include <rdscom.hpp>
#include <vector>

/// @brief Base class for user commands sent from the GUI to the Teensy.
/// This abstract class defines the interface for a command.
class UserCommand {
   public:
    UserCommand();
    virtual ~UserCommand();

    /// @brief Resets the command to its initial state.
    void reset();

    /// @brief Starts the command.
    void start();

    /// @brief Updates the command.
    void update();

    /// @brief Ends the command.
    void end();

    /// @brief Checks whether the command is done.
    /// @return true if the command is complete.
    virtual bool isDone() = 0;

    /// @brief Checks if the command is parallelizable.
    /// @return true if the command can be run in parallel.
    bool isParralelizable();

    /// @brief Checks if the command has started.
    /// @return true if the command has started.
    bool hasStarted();

    /// @brief Checks if the command has ended.
    /// @return true if the command has ended.
    bool hasEnded();

   protected:
    bool _parralelizable;      ///< Whether the command is parallelizable.
    std::uint32_t _startTime;  ///< Time when the command started.
    std::uint32_t _endTime;    ///< Time when the command ended.

    /// @brief Called during reset.
    virtual void onReset() = 0;

    /// @brief Called when starting the command.
    virtual void onStart() = 0;

    /// @brief Called on command update.
    virtual void onUpdate() = 0;

    /// @brief Called when ending the command.
    virtual void onEnd() = 0;

   private:
    bool _hasStarted;  ///< Flag indicating if the command has started.
    bool _hasEnded;    ///< Flag indicating if the command has ended.
};

/// @brief A buffer that manages user commands.
/// This class collects user commands and executes them in slices.
class UserCommandBuffer {
   public:
    struct ExecutionStats {
        std::uint32_t time;     ///< Execution time.
        std::uint8_t executed;  ///< Number of executed commands.
        bool success;           ///< Whether the execution
    };

    /// @brief Constructor.
    UserCommandBuffer();

    /// @brief Adds a command to the buffer.
    /// @param command Shared pointer to a UserCommand.
    void addCommand(std::shared_ptr<UserCommand> command);

    /// @brief Clears the command buffer.
    void clear();

    /// @brief Resets all commands in the buffer.
    void reset();

    /// @brief Continues executing the current slice of commands.
    void tick();

    /// @brief Executes the current slice of commands.
    void startExecution();

    /// @brief Registers a callback to be called when execution is complete.
    /// @param callback The callback to register.
    void onExecutionComplete(std::function<void(ExecutionStats)> callback);

    /// @brief Registers a callback to be called when calibration is complete.
    /// @param callback The callback to register.
    void onCalibrationComplete(std::function<void()> callback);

    /// @brief Calibrates the finger.
    void calibrateFinger();

   private:
    /// @brief Nested class representing a slice of commands.
    class CommandSlice {
       public:
        /// @brief Constructs a command slice.
        /// @param start Starting index.
        /// @param end Ending index.
        CommandSlice(std::size_t start, std::size_t end);

        /// @brief Gets the starting index.
        /// @return The start index.
        std::size_t start() const;

        /// @brief Gets the ending index.
        /// @return The end index.
        std::size_t end() const;

        /// @brief Gets the number of commands in the slice.
        /// @return The slice size.
        std::size_t size() const;

        /// @brief Returns an empty command slice.
        /// @return An empty CommandSlice.
        static CommandSlice empty();

        /// @brief Checks if the given slice is empty.
        /// @param slice The CommandSlice to check.
        /// @return true if the slice is empty.
        static bool isEmpty(const CommandSlice &slice);

       private:
        std::size_t _start;  ///< Starting index.
        std::size_t _end;    ///< Ending index.
    };

    std::vector<std::shared_ptr<UserCommand>> _commands;  ///< All commands.
    CommandSlice _currentSlice;                           ///< The current command slice.
    std::size_t _numCompletedCommands;                    ///< Number of completed commands.
    bool _isExecuting;                                    ///< Whether the buffer is executing commands.
    std::uint32_t _startTime;                             ///< Time when execution
    bool _isCalibrating;                                  ///< Whether the buffer is calibrating.

    std::vector<std::function<void(ExecutionStats)>> _onExecutionCompleteCallbacks;  ///< Callbacks to call when execution is complete.
    std::vector<std::function<void()>> _onCalibrationCompleteCallbacks;              ///< Callbacks to call when calibration is complete.

    /// @brief Finds the next slice of commands to execute.
    /// @param currentSlice The current command slice.
    /// @return The next CommandSlice.
    CommandSlice findNextSlice(const CommandSlice &currentSlice);

    /// @brief Called continuously while the finger is calibrating.
    void calibrateFingerTick();

    /// @brief Checks if the finger is calibrating.
    /// @return true if the finger is calibrating.
    bool isDoneCalibrating();
};

/// @brief Enumeration for motor control types.
enum FingerControlType : std::uint8_t {
    POSITION = 0,  ///< Position control.
    VELOCITY = 1,  ///< Velocity control.
    TORQUE = 2     ///< Torque control.
};

/// @brief Command to control a motor.
/// This command is used to control motors and is created from rdscom messages.
class FingerControlCommand : public UserCommand {
   public:
    /// @brief Constructs a MotorControlCommand.
    /// @param fingerJoinID The finter joint ID.
    /// @param controlType The type of control.
    /// @param controlValue The value for control.
    /// @param simultaneous Whether the command is simultaneous.
    FingerControlCommand(std::uint8_t fingerJoinID, FingerControlType controlType, float controlValue, bool simultaneous);

    FingerControlCommand() : FingerControlCommand(255, FingerControlType::POSITION, 0.0f, false) {}

    /// @brief Creates a MotorControlCommand from an rdscom message.
    /// @param msg The message containing command data.
    /// @return A Result wrapping the MotorControlCommand.
    static rdscom::Result<FingerControlCommand> fromMessage(const rdscom::Message &msg);

    /// @brief Checks whether the command is done.
    /// @return true if the command has completed.
    bool isDone() override;

    std::uint8_t fingerJoinID() const { return _fingerID; }
    FingerControlType controlType() const { return _controlType; }
    float controlValue() const { return _controlValue; }
    bool simultaneous() const { return _simultaneous; }

   private:
    std::uint8_t _fingerID;          ///< The motor identifier.
    FingerControlType _controlType;  ///< The control type.
    float _controlValue;             ///< The control value.
    bool _simultaneous;              ///< Whether the command is simultaneous.

    // Implementation of virtual methods.
    void onReset() override;
    void onStart() override;
    void onUpdate() override;
    void onEnd() override;
};

#endif  // __USER_COMMAND_H__
