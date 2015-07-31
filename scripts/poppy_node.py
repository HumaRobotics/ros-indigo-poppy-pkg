#!/usr/bin/env python


import rospy
from std_msgs.msg import String, Float32MultiArray, MultiArrayDimension
from std_srvs.srv import Empty, EmptyResponse

from poppy_humanoid import PoppyHumanoid

poppy = PoppyHumanoid()


read_registers = ["goal_speed", "compliant", "present_temperature",  "goal_position",   "present_speed",  "present_position", "id"]
write_registers = ["goal_speed", "compliant", "goal_position"]


def setRegister(data, register):

    register = register[0]
    
    for i in range(0, len(data.layout.dim)):
        motorName = data.layout.dim[i].label

        v = data.data[i]
        if register == "compliant":
            v = v!= 0.
        m = getattr(poppy, motorName)
        setattr(m, register, v)
        
        
def usePrimitive(data, args):

    p = getattr(poppy, args[0])
    if args[1] == "start":
        p.start()
    else:
        p.stop()


def poppy_node():
    rospy.init_node('poppy_node')
    rate = rospy.Rate(10) 
    
    for r in write_registers:
        rospy.Subscriber('poppy/register/'+r+'/write', Float32MultiArray, setRegister, callback_args=[r])   

    services = {}
    for p in poppy.primitives:
        rospy.Subscriber('poppy/primitive/'+p.name+'/start', String, usePrimitive, callback_args=[p.name, "start"])   
        rospy.Subscriber('poppy/primitive/'+p.name+'/stop', String, usePrimitive, callback_args=[p.name, "stop"])   
 
    pubs = {}
    for r in read_registers:
        pubs[r] = rospy.Publisher('poppy/register/'+r+'/read', Float32MultiArray, queue_size=10)

    while not rospy.is_shutdown():
        for r in read_registers:

            msg = Float32MultiArray()
            msg.data = []

            for m in poppy.motors:           
                msg.data.append(getattr(m, r))
                dimension = MultiArrayDimension()
                dimension.label= m.name
                msg.layout.dim.append(dimension)
            
            pubs[r].publish(msg)

        rate.sleep()

if __name__ == '__main__':
    try:
        poppy_node()
    except rospy.ROSInterruptException:
        pass
