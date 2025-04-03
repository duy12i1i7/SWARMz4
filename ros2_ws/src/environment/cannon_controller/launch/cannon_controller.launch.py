from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='cannon_controller',
            executable='cannon_controller',
            name='cannon_controller',
            parameters=[
                {
                    'sources': ['flag_ship_1', 'flag_ship_2'],  # Danh sách các chiến hạm
                    'cannon_script_path': 'launch_scripts/cannon.py',  # Đường dẫn tương đối từ working_dir
                    'working_dir': '~/SWARMz4'  # Thay bằng đường dẫn thực tế
                }
            ]
        )
    ])
