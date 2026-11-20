import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_share = get_package_share_directory('dif_bot_description')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')
    xacro_file = os.path.join(pkg_share, 'src', 'description', 'dif_bot_description6.urdf.xacro')
    world_file = os.path.join(pkg_share, 'worlds', 'arena_world.sdf')

    use_ros2_control = LaunchConfiguration('use_ros2_control')
    publish_odom_tf = LaunchConfiguration('publish_odom_tf')

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file, ' use_ros2_control:=', use_ros2_control]),
        value_type=str
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'dif_bot', '-x', '0.0', '-y', '0.0', '-z', '0.2'],
        output='screen'
    )

    bridge_sensors = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
        ],
        output='screen'
    )

    bridge_gz_diff = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        condition=UnlessCondition(use_ros2_control),
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        output='screen'
    )

    bridge_gz_tf = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        condition=IfCondition(PythonExpression(["'", use_ros2_control, "' == 'false' and '", publish_odom_tf, "' == 'true'"])),
        arguments=['/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_ros2_control', default_value='false'),
        DeclareLaunchArgument('publish_odom_tf', default_value='true'),
        gz_sim, rsp, spawn, bridge_sensors, bridge_gz_diff, bridge_gz_tf
    ])
