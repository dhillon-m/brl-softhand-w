import time

##################################
# Useful for any servo operation #
##################################

def checksum(packet):
    """
    Calculate the checksum for a given packet.
    :param packet: List of integers representing the packet
    :return: Checksum value
    """
    return (~sum(packet[2:])) & 0xFF


def read_servo_moving(ser, servo_id):
    """
    Check if a specific servo is currently moving.
    :param ser: Open serial port
    :param servo_id: ID of the servo to check
    :return: True if the servo is moving, False if not, None if an error occurs
    """
    ser.reset_input_buffer()
    packet = [0xFF, 0xFF, servo_id, 0x04, 0x02, 0x42, 0x01]
    packet.append((~sum(packet[2:])) & 0xFF)
    ser.write(bytearray(packet))
    response = ser.read(7)
    if len(response) == 7 and response[0] == 0xFF and response[1] == 0xFF:
        moving = response[5]
        return moving == 1
    return None


def wait_for_servo(ser, servo_ids=[1, 2, 3, 4], check_interval=0.1, timeout=10):
    """
    Wait until all specified servos have stopped moving.
    :param ser: Open serial port
    :param servo_ids: List of servo IDs to check
    :param check_interval: Time in seconds between checks
    :param timeout: Maximum time to wait in seconds
    :return: True if all servos are stopped, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        all_stopped = True
        for servo_id in servo_ids:
            moving = read_servo_moving(ser, servo_id)
            if moving is None:
                return False
            if moving:
                all_stopped = False
        if all_stopped:
            return True
        time.sleep(check_interval)
        
    print("Timeout reached before all servos stopped.")
    return False


def move_servo(ser, servo_id, position):
    """
    Move a specific servo to the given position.
    :param ser: Open serial port
    :param servo_id: ID of the servo to move
    :param position: Position value to move the servo to (0-4095)
    """
    pos_l = position & 0xFF         # Low byte of position
    pos_h = (position >> 8) & 0xFF  # High byte of position
    
    packet = [0xFF, 0xFF, servo_id, 0x05, 0x03, 0x2A, pos_l, pos_h]
    packet.append(checksum(packet))
    
    ser.write(bytearray(packet))



###########################
# Useful for hand control #
###########################

# !!WARNING!!: The positions below must be adjusted for your specific hand
# Use the Feetech software to find the correct positions for your servos

def close_hand(ser):
    """
    Close the hand.
    :param ser: Open serial port
    """
    move_servo(ser, servo_id=2, position=2200) # Position of extensor servo when hand is closed
    time.sleep(0.05)
    move_servo(ser, servo_id=3, position=2100) # Position of flexor servo when hand is closed
    time.sleep(0.05)
    wait_for_servo(ser, servo_ids=[2, 3])


def open_hand(ser):
    """
    Open the hand.
    :param ser: Open serial port
    """
    move_servo(ser, servo_id=3, position=1070) # Position of flexor servo when hand is open
    time.sleep(0.05)
    move_servo(ser, servo_id=2, position=700) # Position of extensor servo when hand is open
    time.sleep(0.05)
    wait_for_servo(ser, servo_ids=[2, 3])



##############################
# Specific for the SoftWrist #
##############################

def move_wrist(ser, flexion_angle, ulnar_angle):
    """
    Move the wrist to the specified positions.
    :param ser: Open serial port
    :param flexion_angle: Position value for wrist flexion/extension (servo 1)
    :param ulnar_angle: Position value for ulnar/radial deviation (servo 2)
    """
    # Joint mapping
    flexion_deg_per_pos = 360 / (1.8 * (4095 - 0))
    flexion_min_angle = (0 - 2048) * flexion_deg_per_pos
    flexion_max_angle = (4095 - 2048) * flexion_deg_per_pos
    
    ulnar_deg_per_pos = 360 / (3.05 * (3100 - 1200))
    ulnar_min_angle = (1200 - 2150) * ulnar_deg_per_pos
    ulnar_max_angle = (3100 - 2150) * ulnar_deg_per_pos
    
    # Convert wrist angles to servo positions
    flexion_pos = int(round(2048 + (flexion_angle / flexion_deg_per_pos)))
    flexion_pos = max(1500, min(4095, flexion_pos))

    ulnar_pos = int(round(2150 + (ulnar_angle / ulnar_deg_per_pos)))
    ulnar_pos = max(1200, min(3100, ulnar_pos))
    
    # Move servos to the calculated positions
    move_servo(ser, servo_id=1, position=flexion_pos)
    time.sleep(0.05)
    move_servo(ser, servo_id=4, position=ulnar_pos)
    time.sleep(0.05)
    wait_for_servo(ser, servo_ids=[1, 4])


def home_hand(ser):
    """
    Move the hand to the home position.
    :param ser: Open serial port
    """
    open_hand(ser)
    move_wrist(ser, flexion_angle=0, ulnar_angle=0)
    wait_for_servo(ser, servo_ids=[1, 2, 3, 4])