
class ApplicationContext:
    # Class-level attributes (initially None)
    mcu_com = None
    app_interface = None
    error_manager = None

    @staticmethod
    def initialize(args):
        """Initialize the ApplicationContext exactly once."""
        if (
            ApplicationContext.mcu_com is not None
            or ApplicationContext.app_interface is not None
        ):
            raise Exception("ApplicationContext already initialized")
        
        from interface.error_manager import ErrorManager
        from interface.app import AppInterface
        from com.mcu_com import MCUCom


        ApplicationContext.mcu_com = MCUCom(args.port, args.baudrate)
        ApplicationContext.app_interface = AppInterface()
        ApplicationContext.error_manager = ErrorManager()

    @staticmethod
    def tick():
        """Call tick on both MCUCom and AppInterface."""
        if (
            ApplicationContext.mcu_com is None
            or ApplicationContext.app_interface is None
        ):
            raise Exception("ApplicationContext not initialized")
        ApplicationContext.mcu_com.tick()
        ApplicationContext.app_interface.tick()