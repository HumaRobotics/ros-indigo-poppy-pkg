#!/usr/bin/env python


#~ https://github.com/pierre-rouanet/pypot/blob/master/REST-APIs.md

import rospy
from std_msgs.msg import String, Float32MultiArray, MultiArrayDimension

import zmq, json

#~ registers = ["registers", "goal_speed", "compliant", "safe_compliant", "angle_limit", "present_load", "id", "present_temperature", "moving_speed", "torque_limit", "goal_position", "upper_limit", "lower_limit", "name", "present_speed", "present_voltage", "present_position", "model", "compliance_slope", "compliance_margin"]
read_registers = ["goal_speed", "compliant", "present_temperature",  "goal_position",   "present_speed",  "present_position", "id"]
write_registers = ["goal_speed", "compliant", "goal_position"]

robot_address = 'http://poppy.local:6768'

socket = None

def setRegister(data, register):
    
    #~ r = data._connection_header['topic']
    #~ r= r.replace("/poppy/register/", "")
    #~ r = r.replace("/write", "")
    #~ print "register ",r
    
    register = register[0]
    
    for i in range(0, len(data.layout.dim)):
        m = data.layout.dim[i].label
        print "motor ",m
        v = data.data[i]
        if register == "compliant":
            v = v!= 0.
            #~ pass
        #~ else:
            #~ v = str(v)
        print "value ",v
        
        #~ url = robot_address +'/motor/'+m+'/register/'+register+'/value.json'
        
        c = zmq.Context()
        socket = c.socket(zmq.REQ)
        socket.connect ("tcp://poppy.local:6768")
        
        
        req = {"robot": {"set_register_value": {"motor": m, "register": register, "value": str(v)}}}
        socket.send_json(req)
        print socket.recv_json()

        #~ values = json.dumps(v)

        #~ req = urllib2.Request(url, values)
        #~ req.add_header("Content-Type",'application/json')
        #~ response = urllib2.urlopen(req)

        
#~ def usePrimitive(data, args):

    #~ p = getattr(poppy, args[0])
    #~ if args[1] == "start":
        #~ p.start()
    #~ else:
        #~ p.stop()

def poppy_node_rest():
    rospy.init_node('poppy_node', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    
    c = zmq.Context()
    socket = c.socket(zmq.REQ)
    socket.connect ("tcp://poppy.local:6768")
    
    
    req = {"robot": {"get_motors_list": {"alias": "motors"}}}
    socket.send_json(req)
    motorList = socket.recv_json()
    
    #~ pubs = {}
    #~ for m in motorList:
        #~ pubs[m] = rospy.Publisher('poppy/motor/'+m+'/read', Float32MultiArray, queue_size=10)
 
    pubs = {}
    for r in read_registers:
        pubs[r] = rospy.Publisher('poppy/register/'+r+'/read', Float32MultiArray, queue_size=10)

        
    for r in write_registers:
        rospy.Subscriber('poppy/register/'+r+'/write', Float32MultiArray, setRegister, callback_args=[r])
    
    while not rospy.is_shutdown():
        for r in read_registers:
        
            msg = Float32MultiArray()
            msg.data = []
            
            for m in motorList:
                req = {"robot": {"get_register_value": {"motor": m, "register": r}}}
                socket.send_json(req)
                pos = socket.recv_json()
                        
                msg.data.append(pos)
                dimension = MultiArrayDimension()
                dimension.label=m
                msg.layout.dim.append(dimension)
            
            
            pubs[r].publish(msg)

        rate.sleep()


if __name__ == '__main__':
    try:
       poppy_node_rest()
    except rospy.ROSInterruptException:
        pass
