#include "user_command.hpp"

#include "message_definitions.hpp"

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

void UserCommandBuffer::tick() {
    if (_isCalibrating) {
        std::cout << "Calibrating finger" << std::endl;
        calibrateFingerTick();
        if (isDoneCalibrating()) {
            _isCalibrating = false;
        }

        for (auto &callback : _onCalibrationCompleteCallbacks) {
            callback();
        }

        return;
    }

    if (_isExecuting == false) {
        return;
    }

    if (CommandSlice::isEmpty(_currentSlice)) {
        _currentSlice = findNextSlice(_currentSlice);
    }

    if (CommandSlice::isEmpty(_currentSlice)) {
        _isExecuting = false;
        return;
    }

    for (std::size_t i = _currentSlice.start(); i < _currentSlice.end(); i++) {
        if (!_commands[i]->hasStarted()) {
            _commands[i]->start();
        }

        if (!_commands[i]->isDone()) {
            _commands[i]->update();
        } else {
            _commands[i]->end();
            _numCompletedCommands++;
        }
    }

    if (_numCompletedCommands == _currentSlice.size()) {
        _currentSlice = CommandSlice::empty();
        _numCompletedCommands = 0;

        ExecutionStats stats = {
            .time = millis() - _startTime,
            .executed = static_cast<std::uint8_t>(_currentSlice.size()),
            .success = true,
        };

        for (auto &callback : _onExecutionCompleteCallbacks) {
            callback(stats);
        }

        _isExecuting = false;
    }
}

void UserCommandBuffer::onExecutionComplete(std::function<void(ExecutionStats)> callback) {
    _onExecutionCompleteCallbacks.push_back(callback);
}

void UserCommandBuffer::onCalibrationComplete(std::function<void()> callback) {
    _onCalibrationCompleteCallbacks.push_back(callback);
}

void UserCommandBuffer::calibrateFinger() {
    _isCalibrating = true;
}

void UserCommandBuffer::startExecution() {
    if (_isExecuting) {
        std::cerr << "Command buffer is already executing" << std::endl;
        return;
    }

    this->_startTime = millis();

    _isExecuting = true;
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

void UserCommandBuffer::calibrateFingerTick() {

}

bool UserCommandBuffer::isDoneCalibrating() {
    return true;
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

    if (start >= _commands.size()) {
        return CommandSlice::empty();
    }

    for (std::size_t i = currentSlice.end(); i < _commands.size(); i++) {
        if (!_commands[i]->isParralelizable()) {
            end = i + 1;
            break;
        }
    }

    return CommandSlice(start, end);
}

/**------------------------------------------------------------------------
 *                    FingerControlCommand Implementation
 *------------------------------------------------------------------------**/

FingerControlCommand::FingerControlCommand(std::uint8_t fingerJoinID, FingerControlType controlType, float controlValue, bool simultaneous)
    : _fingerID(fingerJoinID), _controlType(controlType), _controlValue(controlValue), _simultaneous(simultaneous) {
}

rdscom::Result<FingerControlCommand> FingerControlCommand::fromMessage(const rdscom::Message &msg) {
    // check that the message is the right prototoype
    if (msg.data().type().identifier() != msgs::motorControlProto().identifier()) {
        return rdscom::Result<FingerControlCommand>::errorResult("Invalid prototype");
    }

    bool error = rdscom::check(
        rdscom::defaultErrorCallback(std::cerr),
        msg.getField<std::uint8_t>("motor_id"),
        msg.getField<std::uint8_t>("control_mode"),
        msg.getField<float>("control_value"),
        msg.getField<std::uint8_t>("simultaneous"));

    if (error) {
        return rdscom::Result<FingerControlCommand>::errorResult("Error parsing message fields");
    }

    std::uint8_t fingerJoinID = msg.getField<std::uint8_t>("motor_id").value();
    FingerControlType controlType = static_cast<FingerControlType>(msg.getField<std::uint8_t>("control_mode").value());
    float controlValue = msg.getField<float>("control_value").value();
    bool simultaneous = msg.getField<std::uint8_t>("simultaneous").value() != 0;

    return rdscom::Result<FingerControlCommand>::ok(FingerControlCommand(fingerJoinID, controlType, controlValue, simultaneous));
}

bool FingerControlCommand::isDone() {
    return true;
}

void FingerControlCommand::onReset() {
    // Implement reset behavior if needed.
}

void FingerControlCommand::onStart() {
}

void FingerControlCommand::onUpdate() {
    // Implement update behavior if needed.
    std::cout << "FingerControlCommand update\n";
}

void FingerControlCommand::onEnd() {
    // Implement end behavior if needed.
}
