import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    dif_pkg = get_package_share_directory('dif_bot_description')
    mis_pkg = get_package_share_directory('mision_autonoma')
    nav_pkg = get_package_share_directory('nav2_bringup')

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(dif_pkg, 'launch', 'sim.launch.py')),
        launch_arguments={'use_ros2_control': 'false', 'publish_odom_tf': 'false'}.items()
    )

    ekf = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[os.path.join(mis_pkg, 'config', 'ekf.yaml')],
        remappings=[('odometry/filtered', '/odom_filtered')]
    )

    nav2 = TimerAction(period=4.0, actions=[
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav_pkg, 'launch', 'bringup_launch.py')),
            launch_arguments={
                'use_sim_time': 'true',
                'map': os.path.join(mis_pkg, 'maps', 'mapa_proyecto.yaml'),
                'params_file': os.path.join(mis_pkg, 'config', 'nav2_params.yaml')
            }.items()
        )
    ])

    rviz = TimerAction(period=6.0, actions=[
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.join(nav_pkg, 'rviz', 'nav2_default_view.rviz')],
            parameters=[{'use_sim_time': True}],
            output='screen'
        )
    ])

    mission = TimerAction(period=7.0, actions=[
        Node(
            package='mision_autonoma',
            executable='mission_node',
            parameters=[{'use_sim_time': True}],
            output='screen'
        )
    ])

    return LaunchDescription([sim, ekf, nav2, rviz, mission])
