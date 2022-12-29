from dps.arduino.serial_demo import main


class Motor():
    def move_once(self):
        main()


class DummyMotor():
    def move_once(self):
        pass


if __name__ == '__main__':
    motor = Motor()
    motor.move_once()
