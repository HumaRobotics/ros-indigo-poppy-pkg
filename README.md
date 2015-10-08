# ros-indigo-poppy-pkg
ROS Indigo package for Poppy robots

This package contains:
- one Python scripts that creates a PoppyHumanoid object and exposes the motors registers values and the primitives
- two Python scripts to use Poppy over network through Rest API (HTTP or ZMQ)

## Installation

Assuming you have ros indigo installed and a catkin workspace set up at <path/to/catkin_ws>

    cd <path/to/catkin_ws>/src
    git clone https://github.com/HumaRobotics/ros-indigo-poppy-pkg.git poppy_pkg
    cd ..
    catkin_make
    source devel/setup.bash

In the poppy_pkg/launch/poppy-node.launch, set the *creature* parameter to your creature's name (poppy-humanoid, poppy-torso or poppy-ergo-jr) or to th epath to your config file.

## Launch inside the robot:

In terminal 1:

    roslaunch poppy_pkg poppy-node.launch
    
In terminal 2:

    rostopic list

You should see all topics created by the poppy node, for example
- 'poppy/motors/read_present' (sensor_msgs/JointState) contain the motors current position, speed and load.
- 'poppy/motors/read_goal' (sensor_msgs/JointState) contain the motors goal position, speed and the current max_torque value (between 0 and 100).
- 'poppy/motors/write' (sensor_msgs/JointState) allows you to set the goal position, speed and max_torque values. Compliance of the motors are set to False if max_torque is not zero. Example of command line publication: rostopic pub -1 /poppy_node/motors/write sensor_msgs/JointState [0,0,'test'] ['head_z','head_y'] [20,-10] [] [100,100]

- 'poppy/primitive/< primitive name >/start' to start a primitive. Message content not used, so you can use an empty one: rostopic pub -1 /poppy/primitive/arms_copy_motion/start std_msgs/String " "
- 'poppy/primitive/< primitive name >/stop' same as primitive start topic but for stop

If you do a 

    rosparam list
    
You get the IDs, model, and setup (orientation, offset, limit angles) of each motor.


If you want to command several poppy creatures at the same type, simply start two nodes with different name parameters.

## Use rest API

Do the ROS installation and follow the installation step on your computer and not inside the robot !

### HTTP

Inside the robot, launch the http services:

    poppy-services poppy-humanoid --http --no-browser
    
In the poppy-HTTP.launch file, set your robot's IP and the HTTP server port (8080 by default). In your computer, over the same local network:

    roslaunch poppy_pkg poppy-HTTP.launch
    
### ZMQ

Be sure you have the zmq library installed (or *pip install pyzmq*)

Inside the robot, launch the http services:

    import zmq

    from  pypot.server import ZMQRobotServer

    robot = ... #create your robot from a config file or using the PoppyHumanoid lib

    server = ZMQRobotServer(robot,"0.0.0.0", 6768) 

    # We launch the server inside a thread
    threading.Thread(target=lambda: server.run()).start()
    print "ready"
        
In the poppy-ZMQ.launch file, set your robot's IP and the HTTP server port (6768 on the previous example). In your computer, over the same local network:

    roslaunch poppy_pkg poppy-ZMQ.launch

Topics and messages are the same as poppy_node ones. Warning, HTTP is slower than ZMQ, itself slower than having ROS directly on the robot.

