import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_name = 'dif_bot_description'
    xacro_subpath = 'src/description/dif_bot_description.urdf.xacro'

    # Obtener rutas absolutas de instalación
    pkg_share = get_package_share_directory(pkg_name)
    xacro_file = os.path.join(pkg_share, xacro_subpath)
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'urdf_config.rviz')

    # Procesar Xacro a URDF
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # Nodo robot_state_publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw}]
    )

    # Nodo joint_state_publisher_gui
    node_joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )

    # Nodo RViz2 cargando la configuración guardada
    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )

    return LaunchDescription([
        node_robot_state_publisher,
        node_joint_state_publisher_gui,
        node_rviz
    ])
