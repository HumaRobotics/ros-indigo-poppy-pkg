# ros-indigo-poppy-pkg
ROS Indigo package for Poppy robots

This package contains:
- one Python scripts that create a PoppyHumanoid object and exposes the motors registers values and the primitives
- one script to use ROS over network through Rest API: 

###To install: ###

Assuming you have ros indigo installed and a catkin workspace set up at <path/to/catkin_ws>

    cd <path/to/catkin_ws>/src
    git clone https://github.com/HumaRobotics/ros-indigo-poppy-pkg.git poppy_pkg
    cd ..
    catkin_make
    source devel/setup.bash

###Launch inside the robot: ###

In terminal 1:

    roscore
    
In terminal 2:

    rosrun poppy_pkg poppy_node.py
    
In terminal 3:

    rostopic list

You should see all topics created by the poppy node, for example
- 'poppy/register/< register name >/read' for registers that you can read. Each message contains the values for all motors.
- 'poppy/register/< register name >/write' for registers where you can write. Example command line to set the head motors not compliant: rostopic pub -1 /poppy/register/compliant/write std_msgs/Float32MultiArray [[["head_z",0,0],["head_y",0,0]],0] [0,0]
- 'poppy/primitive/< primitive name >/start' to start a primitive. Message content not used, so you can use an empty one: rostopic pub -1 /poppy/primitive/arms_copy_motion/start std_msgs/String ""
- 'poppy/primitive/< primitive name >/stop' same as primitive start topic but for stop

###Use rest API###

Do the installation inside yoru computer and not inside the robot !

Inside the robot, launch the http services:

    poppy-services poppy-humanoid --http --no-browser
    
In your computer, over the same local network:

    rosrun poppy_pkg poppy_over_rest_node.py
    
Messages are the same as poppy_node ones. Warning, this is slower.

###TODO: ###

- useful functions: alias usage, easy compliant
- adapt to a configuration
- add primitive to rest node