# SoftHand Model-W

**A 3D-printed, anthropomorphic, underactuated robot hand with an integrated wrist and carpal tunnel**

[![arXiv](https://img.shields.io/badge/arXiv-2604.00738-b31b1b.svg)](https://arxiv.org/abs/2604.00738)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Servos](https://img.shields.io/badge/servos-Feetech%20STS3215-orange)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Dhillon B. Merritt, Christopher J. Ford, Haoran Li, Malia Smith, Zhixing Chen, Efi Psomopoulou\*, Nathan F. Lepora\*  
*Bristol Robotics Laboratory, University of Bristol* · \*Equal contribution

This repository contains the Python control code for the **SoftHand Model-W (SoftHand-W)**. The SoftHand-W is a 3D-printed hand based on the Pisa/IIT SoftHand. It adds an antagonistic tendon mechanism and a **2-DoF tendon-driven wrist**. Four servos drive it:

- **Fingers:** active flexion and extension of all five fingers.
- **Wrist:** active flexion/extension and radial/ulnar deviation of the palm.

The hand keeps the synergistic, self-adaptive grasping of the SoftHand family.

📄 **Paper:** [arXiv:2604.00738](https://arxiv.org/abs/2604.00738)

---

## Contents

- [Highlights](#highlights)
- [Hardware](#hardware)
- [Software](#software)
- [Getting started](#getting-started)
- [Library reference](#library-reference)
- [Experiments](#experiments)
- [Citation](#citation)
- [Acknowledgements](#acknowledgements)
- [License](#license)

## Highlights

- **Underactuated and anthropomorphic.** Five fingers move together through adaptive synergies, driven by antagonistic flexor and extensor tendons.
- **2-DoF wrist** in a serial rotational-rotational layout:
  - **±90°** flexion/extension
  - **±30°** radial/ulnar deviation
- **Carpal-tunnel tendon routing.** The finger tendons pass through the wrist inside PTFE sheaths that work like Bowden cables. This means:
  - Moving the wrist doesn't make the fingers flex.
  - The motors can sit in the forearm, which keeps weight away from the hand.
- **Human-scale.** The hand is 164.6 mm from the base of the palm to the middle fingertip, which is within the 5th–95th percentile of adult hands.
- **Low-cost and easy to build.** It uses printed PLA, off-the-shelf servos and common hardware.

## Hardware

| Component       | Details                                                                              |
| --------------- | ------------------------------------------------------------------------------------ |
| Actuators       | 4 × Feetech STS3215 serial bus servos (19.5 kg·cm at 7.4 V)                          |
| Servo interface | Feetech URT-1 controller, USB to PC                                                  |
| Structure       | PLA (FDM); small precision parts in resin (SLA); CNC-milled aluminium parts          |
| Tendons         | Nylon thread, routed through PTFE tubing (carpal tunnel)                             |
| Fasteners       | M2 screws and bearings. Tendons are anchored with an M2 bolt and washers, not knots. |
| Hand size       | 164.6 mm tall; each finger 81.6 mm long                                              |
| Wrist size      | 54.5 mm (H) × 69.3 mm (W) × 41 mm (D)                                                |
| Robot arm       | Tested on a Universal Robots UR5                                                     |

### Servo IDs

The code assumes the following servo IDs:

| ID | Function                       |
| -- | ------------------------------ |
| 1  | Wrist flexion / extension      |
| 2  | Finger extensor                |
| 3  | Finger flexor                  |
| 4  | Wrist radial / ulnar deviation |

### Wrist kinematics

Distal Denavit–Hartenberg parameters of the wrist:

| Joint | Motion                   | a (mm) | α   | d | θ  |
| ----- | ------------------------ | ------ | --- | - | -- |
| 1     | Ulnar / radial deviation | 34     | π/2 | 0 | θ₁ |
| 2     | Flexion / extension      | 48     | 0   | 0 | θ₂ |

## Software

| File                                     | Purpose                                                                                                                           |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [`softhand_w_lib.py`](softhand_w_lib.py) | Servo control library: raw Feetech packet commands, hand open/close, wrist angle control and tool centre point (TCP) calculation |
| [`test_script.py`](test_script.py)       | Cube-stacking experiment on a UR5. It logs joint angles and pose to CSV and plots the results.                                   |

Wrist control is **open loop and proportional**. A requested angle is turned into a servo position by multiplying it by a constant gain and offsetting it from a calibrated centre value. Because the wrist moves the hand, the tool centre point also moves. `test_script.py` can run a background thread that recomputes the robot's TCP from the current wrist angles.

## Getting started

### Requirements

- Python 3.10+
- [`pyserial`](https://pypi.org/project/pyserial/), `numpy`, `matplotlib`
- For the UR5 experiments only: the Common Robot Interface (`cri`) package, which provides `SyncRobot`, `AsyncRobot` and `RTDEController`.

```sh
pip install pyserial numpy matplotlib
```

### Calibrate your hand

> ⚠️ **The servo positions in `softhand_w_lib.py` belong to one particular build.** Tendon length and how the horns are mounted differ between builds. Using these positions without checking them can over-tension the tendons.

1. Use the Feetech debugging software to find the open and closed positions of the flexor servo (ID 3) and the extensor servo (ID 2).
2. Update the values in `open_hand()` and `close_hand()`.
3. Check the wrist centre values in `move_wrist()` and `get_wrist_angles()`: `2048` for flexion and `2150` for deviation. Also check the travel limits.

### Minimal example

```python
import serial
import softhand_w_lib as swl

ser = serial.Serial("COM5", baudrate=1_000_000, timeout=0.1)  # change to your port

swl.home_hand(ser)                                   # open hand, centre wrist
swl.close_hand(ser)
swl.wait_for_servo(ser, servo_ids=[2, 3])

swl.move_wrist(ser, flexion_angle=45, ulnar_angle=0) # degrees
swl.wait_for_servo(ser, servo_ids=[1, 4])
print(swl.get_wrist_angles(ser))                     # (flexion°, ulnar°)

swl.open_hand(ser)
ser.close()
```

## Library reference

| Function                                                  | Description                                                                          |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `move_servo(ser, servo_id, position)`                     | Sends a raw position command (0–4095).                                                |
| `read_servo_position(ser, servo_id)`                      | Reads the servo's current position, or returns `None` on error.                       |
| `read_servo_moving(ser, servo_id)`                        | Returns `True` if the servo is moving.                                                |
| `wait_for_servo(ser, servo_ids, check_interval, timeout)` | Waits until every listed servo has stopped.                                           |
| `open_hand(ser)` / `close_hand(ser)`                      | Drives the antagonistic flexor/extensor pair, in the right order.                     |
| `move_wrist(ser, flexion_angle, ulnar_angle)`             | Moves the wrist to the given angles in degrees. Positions are clamped to safe limits. |
| `get_wrist_angles(ser)`                                   | Reads the current wrist angles in degrees.                                            |
| `compute_tcp_from_wrist(flexion_angle, ulnar_angle)`      | Returns the TCP pose `[x, y, z, ax, ay, az]` for a 285 mm hand offset.                |
| `home_hand(ser)`                                          | Opens the hand, centres the wrist and waits for all servos to stop.                   |

Every serial access goes through one shared re-entrant lock, `swl.serial_lock`, so the library can be called from several threads, for example a logger and a TCP updater. Scripts should use this lock rather than creating their own.

## Experiments

The SoftHand-W was mounted on a UR5 and tested on two reorientation tasks. Each task was run with the wrist actuated and with it held fixed.

| Task                                               | Without wrist | With wrist             |
| -------------------------------------------------- | ------------- | ---------------------- |
| **Disc rotation** (90 mm disc, rotated 90°): time  | 66 s          | **47 s** (~29% faster) |
| **Disc rotation**: configuration changes           | 2             | **1**                  |
| **Cube stacking** (six 50 mm cubes): cubes stacked | 5 / 6         | **6 / 6**              |
| **Cube stacking**: max travel of UR5 joint 4       | baseline      | **~36% less**          |

Using the wrist cut down how much the arm had to move to compensate, made the tasks faster, and made some pick-and-place moves possible that couldn't be done otherwise.

To rerun the cube-stacking task:

1. Set the serial port (`COM5`) and the UR5 IP address in `test_script.py`.
2. Check the cube and placement poses for your workspace.
3. Run `python test_script.py`. Logged data goes to `stack_no_wrist.csv`, and plots of joint angles and the end-effector path are shown at the end.

## Citation

If you use this work, please cite:

```bibtex
@article{merritt2026softhandw,
  title   = {SoftHand Model-W: A 3D-Printed, Anthropomorphic, Underactuated Robot Hand with Integrated Wrist and Carpal Tunnel},
  author  = {Merritt, Dhillon B. and Ford, Christopher J. and Li, Haoran and Smith, Malia and Chen, Zhixing and Psomopoulou, Efi and Lepora, Nathan F.},
  journal = {arXiv preprint arXiv:2604.00738},
  year    = {2026}
}
```

## Acknowledgements

This work was supported by the Advanced Research + Invention Agency (ARIA) under the grant *"Democratising Co-Design of Hardware and Control for Robot Dexterity"*.

The design builds on the Pisa/IIT SoftHand and the BRL SoftHand line, including the [MagProprio SoftHand](https://github.com/robotdexterity/MIT-x-BRL-Robot-Hand-with-Proprioception).

## License

The code in this repository is released under the [MIT License](LICENSE).
