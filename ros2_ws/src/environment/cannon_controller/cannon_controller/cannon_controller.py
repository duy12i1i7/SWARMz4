import rclpy
from rclpy.node import Node
from cannon_msgs.msg import CannonControl
import subprocess
from os.path import expanduser

class CannonController(Node):
    def __init__(self):
        super().__init__('cannon_controller')
        
        # Declare parameters
        self.declare_parameter('sources', ['flag_ship_1'])
        self.declare_parameter('cannon_script_path', 'launch_scripts/cannon.py')
        self.declare_parameter('working_dir', expanduser('~/SWARMz4'))
        
        # Get parameters
        sources = self.get_parameter('sources').value
        self.cannon_script = self.get_parameter('cannon_script_path').value
        self.working_dir = expanduser(self.get_parameter('working_dir').value)
        
        # Create subscribers for each source
        for source in sources:
            self.create_subscription(
                CannonControl,
                f'/{source}/cannon_control',
                self.create_callback(source),
                10
            )
            self.get_logger().info(f"Subscribed to /{source}/cannon_control")
    
    def create_callback(self, source):
        def callback(msg):
            self.get_logger().info(f"Command for {source}: YAW={msg.target_yaw}, PITCH={msg.target_pitch}, SPEED={msg.cannon_speed}")
            
            # Execute the cannon script
            try:
                subprocess.run(
                    [
                        'python3',
                        self.cannon_script,
                        source,
                        str(msg.target_yaw),
                        str(msg.target_pitch),
                        str(msg.cannon_speed)
                    ],
                    cwd=self.working_dir,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                self.get_logger().error(f"Failed to execute script: {e}")
        return callback

def main(args=None):
    rclpy.init(args=args)
    node = CannonController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
