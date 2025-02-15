#include "user_command.hpp"

/**------------------------------------------------------------------------
 *                           UserCommand Implementation
 *------------------------------------------------------------------------**/

UserCommand::UserCommand()
    : _hasStarted(false), _hasEnded(false), _parralelizable(false), _startTime(0), _endTime(0) {
}

UserCommand::~UserCommand() {
}

void UserCommand::reset() {
    _hasStarted = false;
    _hasEnded = false;
    _startTime = 0;
    _endTime = 0;
    onReset();
}

void UserCommand::start() {
    _hasStarted = true;
    _startTime = millis();
    onStart();
}

void UserCommand::update() {
    onUpdate();
}

void UserCommand::end() {
    _hasEnded = true;
    _endTime = millis();
    onEnd();
}

bool UserCommand::isParralelizable() {
    return _parralelizable;
}

bool UserCommand::hasStarted() {
    return _hasStarted;
}

bool UserCommand::hasEnded() {
    return _hasEnded;
}

/**------------------------------------------------------------------------
 *                           UserCommandBuffer Implementation
 *------------------------------------------------------------------------**/

UserCommandBuffer::UserCommandBuffer() : _currentSlice(CommandSlice::empty()) {
}

void UserCommandBuffer::addCommand(std::shared_ptr<UserCommand> command) {
    _commands.push_back(command);
}

void UserCommandBuffer::executeCurrentCommandSlice() {
    // If the current slice is empty, find the next slice.
    if (_currentSlice.size() == 0 && !CommandSlice::isEmpty(_currentSlice)) {
        _currentSlice = findNextSlice(CommandSlice(0, 0));
    }

    // Start commands in the current slice.
    for (std::size_t i = _currentSlice.start(); i < _currentSlice.end(); i++) {
        if (!_commands[i]->hasStarted()) {
            _commands[i]->start();
        }
    }

    // Update commands until all in the slice are done.
    std::size_t completedCommands = 0;
    while (completedCommands < _currentSlice.size()) {
        for (std::size_t i = _currentSlice.start(); i < _currentSlice.end(); i++) {
            if (!_commands[i]->isDone()) {
                _commands[i]->update();
            } else {
                if (!_commands[i]->hasEnded()) {
                    _commands[i]->end();
                    completedCommands++;
                }
            }
        }
    }

    if (_currentSlice.end() == _commands.size()) {
        _currentSlice = UserCommandBuffer::CommandSlice::empty();
    } else {
        _currentSlice = findNextSlice(_currentSlice);
    }
}

void UserCommandBuffer::executeAllCommandSlices() {
    while (!UserCommandBuffer::CommandSlice::isEmpty(_currentSlice)) {
        executeCurrentCommandSlice();
    }
}

void UserCommandBuffer::clear() {
    _commands.clear();
    _currentSlice = UserCommandBuffer::CommandSlice::empty();
}

void UserCommandBuffer::reset() {
    for (std::size_t i = 0; i < _commands.size(); i++) {
        _commands[i]->reset();
    }
    _currentSlice = UserCommandBuffer::CommandSlice(0, 0);
}

/**------------------------------------------------------------------------
 *           UserCommandBuffer::CommandSlice Implementation
 *------------------------------------------------------------------------**/

UserCommandBuffer::CommandSlice::CommandSlice(std::size_t start, std::size_t end)
    : _start(start), _end(end) {
}

std::size_t UserCommandBuffer::CommandSlice::start() const {
    return _start;
}

std::size_t UserCommandBuffer::CommandSlice::end() const {
    return _end;
}

std::size_t UserCommandBuffer::CommandSlice::size() const {
    return _end - _start;
}

UserCommandBuffer::CommandSlice UserCommandBuffer::CommandSlice::empty() {
    return CommandSlice(10, 0);
}

bool UserCommandBuffer::CommandSlice::isEmpty(const CommandSlice &slice) {
    return slice.start() >= slice.end();
}

UserCommandBuffer::CommandSlice UserCommandBuffer::findNextSlice(const CommandSlice &currentSlice) {
    std::size_t start = currentSlice.end();
    std::size_t end = currentSlice.end();

    for (std::size_t i = currentSlice.end(); i < _commands.size(); i++) {
        if (!_commands[i]->isParralelizable()) {
            end = i;
            break;
        }
    }

    return CommandSlice(start, end);
}

/**------------------------------------------------------------------------
 *                    MotorControlCommand Implementation
 *------------------------------------------------------------------------**/

MotorControlCommand::MotorControlCommand(std::uint8_t motorId, MotorControlType controlType, float controlValue, bool simultaneous)
    : _motorId(motorId), _controlType(controlType), _controlValue(controlValue), _simultaneous(simultaneous) {
}

rdscom::Result<MotorControlCommand> MotorControlCommand::fromMessage(const rdscom::Message &msg) {
    bool error = rdscom::check(
        rdscom::defaultErrorCallback(std::cerr),
        msg.getField<std::uint8_t>("motor_id"),
        msg.getField<std::uint8_t>("control_mode"),
        msg.getField<float>("control_value"),
        msg.getField<std::uint8_t>("simultaneous"));

    if (error) {
        return rdscom::Result<MotorControlCommand>::errorResult("Error parsing message fields");
    }

    std::uint8_t motorId = msg.getField<std::uint8_t>("motor_id").value();
    MotorControlType controlType = static_cast<MotorControlType>(msg.getField<std::uint8_t>("control_mode").value());
    float controlValue = msg.getField<float>("control_value").value();
    bool simultaneous = msg.getField<std::uint8_t>("simultaneous").value() != 0;

    return rdscom::Result<MotorControlCommand>::ok(MotorControlCommand(motorId, controlType, controlValue, simultaneous));
}

bool MotorControlCommand::isDone() {
    return millis() - _startTime > 1000;
}

void MotorControlCommand::onReset() {
    // Implement reset behavior if needed.
}

void MotorControlCommand::onStart() {
    // Implement start behavior if needed.
}

void MotorControlCommand::onUpdate() {
    // Implement update behavior if needed.
}

void MotorControlCommand::onEnd() {
    // Implement end behavior if needed.
}
