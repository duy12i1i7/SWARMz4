# SWARMz4: Drone and Ship Battle Challenge

## Description
SWARMz4 is a workspace for a drone and ship battle challenge in a Gazebo simulation. This repository provides scripts to install the necessary tools and dependencies to run the simulation and control the drones.

## Features
- Gazebo simulation environment for drone and ship battles
- Integration with PX4, ROS2, and QGroundControl
- Custom ROS2 packages for game management
- Example packages for drone control

## Installation
To install the project, follow these steps:
1. Clone the repository:
    ```bash
    git clone https://github.com/duy12i1i7/SWARMz4.git
    ```
2. Navigate to the project directory:
    ```bash
    cd SWARMz4
    ```
3. Run the installation script:
    ```bash
    ./install_scripts/install_swarmz.sh
    ```
4. Build the ROS2 workspace
    ```bash
    cd ros2_ws
    colcon build && source install/setup.bash
    ```
5. Download dependencies
    ```bash
    cd ros2_ws && source install/setup.bash
    ros2 launch vrx_gz vrx_environment.launch.py world:=nbpark
    ```
    If the environment is showed on Gazebo, the download process is complete. 


## Usage
To run a game, you need to start the Gazebo simulation with the appropriate number of robots. The SWARMz4 challenge makes two teams of 5 drones and 1 flagship fight each other over a 500 x 250 m field.

### Starting the Simulation
1. Run the launch script:
    ```bash
    source ros2_ws/install/setup.bash
    ./launch_scripts/launch_simulation.sh [HEADLESS] [NUM_DRONES_PER_TEAM] [FIELD_LENGTH] [FIELD_WIDTH] [WORLD] [NUM_SHIPS_PER_TEAM]
    ```
    - `HEADLESS`: Set to `1` for headless mode (default), `0` for GUI mode.
    - `NUM_DRONES_PER_TEAM`: Number of drones per team (default is 5).
    - `FIELD_LENGTH`: Length of the field in meters (default is 500).
    - `FIELD_WIDTH`: Width of the field in meters (default is 250).
    - `WORLD`: Name of the Gazebo world to use (default is `nbpark`).
    - `NUM_SHIPS_PER_TEAM`: Number of ships per team (default is 1).


2. Start a game by running the game master launcher in a different terminal:
    ```bash
    cd SWARMz4/ros2_ws
    source install/setup.bash
    ros2 launch game_master game_master.launch.py
    ```
3. To rotate the cannon and fire the rocket, launching it in the different terminal:
    ```bash
    cd SWARMz4/
    source ros2_ws/install/setup.bash
    python3 launch_scripts/cannon.py [SOURCE] [TARGET_YAW] [TARGET_PITCH]
    ```
    With:
   - SOURCE: Represents the warship
   - TARGET_YAW: Represents the gun muzzle's vertical rotation angle, spanning from –π/2 to π/2.
   - TARGET_PITCH: the rotation angle of the gun BASE, ranging from 0 to 2π.
  
   Or use this topic(maybe get some struggle with this):
   ```bash
   source ros2_ws/install/setup.bash
   ros2 topic pub /flag_ship_1/cannon_control cannon_msgs/msg/CannonControl "{target_yaw: 0.5, target_pitch: 1.57}"
    ```

[![Rotate and Fire](https://img.youtube.com/vi/_z1kW_oepP8/0.jpg)](https://www.youtube.com/watch?v=_z1kW_oepP8)  

4. To control any of warship, you can test engines by publishing a topic to one or both of the thrusters:
```bash
ros2 topic pub /model/{Name_of_warship}/joint/left_engine_propeller_joint/cmd_thrust std_msgs/msg/Float64 "data: 150"
```
using this command you should see your boat going in circles.


[![Control the warship](https://img.youtube.com/vi/Spu8wt_rsx4/0.jpg)](https://www.youtube.com/watch?v=Spu8wt_rsx4)

For more details, read the `Answers.md`
