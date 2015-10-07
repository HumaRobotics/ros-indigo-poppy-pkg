#!/usr/bin/env python


#~ THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#~ WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#~ MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#~ ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#~ WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
#~ OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
#~ CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

#~ https://github.com/pierre-rouanet/pypot/blob/master/REST-APIs.md

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import JointState

import urllib2, json

#~ registers = ["registers", "goal_speed", "compliant", "safe_compliant", "angle_limit", "present_load", "id", "present_temperature", "moving_speed", "torque_limit", "goal_position", "upper_limit", "lower_limit", "name", "present_speed", "present_voltage", "present_position", "model", "compliance_slope", "compliance_margin"]
#~ read_registers = ["goal_speed", "compliant", "present_temperature",  "goal_position",   "present_speed",  "present_position", "id"]
#~ write_registers = ["goal_speed", "compliant", "goal_position"]

global robot_address
robot_address = 'http://poppy.local:8080'

def getRegister(motor, register):
    pos = urllib2.urlopen(robot_address + "/motor/"+motor+"/register/"+register).read()
    pos = json.loads(pos)[register]
    return pos
    
def setRegister(motor, register, data):
    values = json.dumps(data)
    url = robot_address +'/motor/'+motor+'/register/'+register+'/value.json'
    req = urllib2.Request(url, values)
    req.add_header("Content-Type",'application/json')
    response = urllib2.urlopen(req)




def JointStateWrite(data):
    print data
    for i in range(len(data.name)):

        if len(data.effort) > 0:
            setRegister(data.name[i], "torque_limit" , data.effort[i])
            if  data.effort[i] > 0.:
                setRegister(data.name[i], "compliant" , False)
            else:
                setRegister(data.name[i], "compliant" , False)
        if len(data.position) > 0:
            setRegister(data.name[i], "goal_position" , data.position[i])
        if len(data.velocity) > 0:
            setRegister(data.name[i], "goal_speed" , data.velocity[i])

        
        
def usePrimitive(data, args):

    if args[1] == "start":
        url = robot_address +'/primitive/'+args[0]+'/start.json'
    else:
        url = robot_address +'/primitive/'+args[0]+'/stop.json'

    pos = urllib2.urlopen(url).read()
    
        

def poppy_node_rest():
    rospy.init_node('poppy_node', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    
    ip = rospy.get_param(rospy.get_name()+'/ip','poppy.local')
    port = rospy.get_param(rospy.get_name()+'/port','8888')
    
    global robot_address
    robot_address = 'http://'+ip+':'+str(port)
    print "connecting to "+robot_address
    
    motorList = urllib2.urlopen(robot_address +"/motor/list.json").read()
    motorList = json.loads(motorList)["motors"]
    
    #set motors info as params
    for m in motorList:

        rospy.set_param(rospy.get_name()+'/motor/'+m+'/id', getRegister(m, "id"))
        rospy.set_param(rospy.get_name()+'/motor/'+m+'/model', getRegister(m, "model"))
        #~ rospy.set_param(rospy.get_name()+'/motor/'+m.name+'/direct', m.direct)
        #~ rospy.set_param(rospy.get_name()+'/motor/'+m.name+'/offset', m.offset)
        rospy.set_param(rospy.get_name()+'/motor/'+m+'/upper_limit', getRegister(m, "upper_limit"))
        rospy.set_param(rospy.get_name()+'/motor/'+m+'/lower_limit', getRegister(m, "lower_limit"))
        
    #create publishers for motors present_position, present_speed, present_load and goal_position and goal_speed and max_torque
    pubs = {}

    pubs[rospy.get_name()+'/motors/read_present'] = rospy.Publisher(rospy.get_name()+'/motors/read_present', JointState, queue_size=10)
    pubs[rospy.get_name()+'/motors/read_goal'] = rospy.Publisher(rospy.get_name()+'/motors/read_goal', JointState, queue_size=10)

     #subscribe to topic to change the goal_position, goal_speed and compliance
    rospy.Subscriber(rospy.get_name()+'/motors/write', JointState, JointStateWrite)   
    
    primitivesList = urllib2.urlopen(robot_address +"/primitive/list.json").read()
    primitivesList = json.loads(primitivesList)["primitives"]
    
    for p in primitivesList:
        rospy.Subscriber(rospy.get_name()+'/primitive/'+p+'/start', String, usePrimitive, callback_args=[p, "start"])   
        rospy.Subscriber(rospy.get_name()+'/primitive/'+p+'/stop', String, usePrimitive, callback_args=[p, "stop"])  
    
    while not rospy.is_shutdown():
            
        msg = JointState()
        msg.name = []
        msg.position = []
        msg.velocity = []
        msg.effort = []

        for m in motorList:           
            msg.name.append(m)
            msg.position.append(getRegister(m, "present_position"))
            msg.velocity.append(getRegister(m, "present_speed"))
            msg.effort.append(getRegister(m, "present_load"))

        pubs[rospy.get_name()+'/motors/read_present'].publish(msg)
        
        
        msg = JointState()
        msg.name = []
        msg.position = []
        msg.velocity = []
        msg.effort = []

        for m in motorList:           
            msg.name.append(m)
            msg.position.append(getRegister(m, "goal_position"))
            msg.velocity.append(getRegister(m, "goal_speed"))
            msg.effort.append(getRegister(m, "torque_limit"))

        pubs[rospy.get_name()+'/motors/read_goal'].publish(msg)

        rate.sleep()


if __name__ == '__main__':
    try:
       poppy_node_rest()
    except rospy.ROSInterruptException:
        pass
