import rospy
import canopen
import struct
import mani_controller.msg import Joints_data


class ManiController:

    def __init__(self):

        #ROS Node and CAN setup
        self.network = canopen.Network()
        can_interface = rospy.get_param('~can_interface')
        self.network.connect(channel=can_interface, bustype='socketcan')

        rospy.init_node('mani_controller')
        position_publisher = rospy.Publisher('mani_position_read', Joints_data)
        position_subscriber = rospy.Subscriber('mani_position_write', Joints_data, self.can_send)

        self.lates_to_send = Joints_data()

        self.network.subscribe(0xA01, self.can_recv)
        self.network.subscribe(0xA02, self.can_recv)
        self.rate = rospy.Rate(30) # 10hz
        
    def can_recv(self, id, data, timestamp):
        filtered_id = id & 0x00F
        angle = struct.unpack('<f', data)
        self.lates_to_send.joints[id - 1].id = id
        self.lates_to_send.joints[id - 1].angle = angle

    def can_send(self, data):
        for joint in data.joints:
            angle_bytes = struct.pack('<f', joint.angle)
            self.network.send_message(joint.id, angle_bytes)

    def loop(self):
        while not rospy.is_shutdown():
            self.position_publisher.publish(self.lates_to_send)
            self.rate.sleep()

if __name__ == '__main__':
    mani_controller = ManiController()
    mani_controller.loop()
    mani_controller.network.disconnect()
