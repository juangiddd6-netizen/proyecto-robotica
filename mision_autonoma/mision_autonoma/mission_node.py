import math
import os
import threading
import time
import yaml

from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from std_srvs.srv import Trigger


class AutonomousMissionNode(Node):
    def __init__(self):
        super().__init__('autonomous_mission_node')
        default_yaml = os.path.join(
            get_package_share_directory('mision_autonoma'),
            'config',
            'waypoints.yaml'
        )
        self.declare_parameter('waypoints_file', default_yaml)
        self.navigator = BasicNavigator()
        self.mission_active = False
        self.srv = self.create_service(
            Trigger, 'iniciar_mision', self.start_mission_callback
        )
        self.get_logger().info('Nodo listo. Llama al servicio /iniciar_mision para comenzar.')

    def _create_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)
        return pose

    def start_mission_callback(self, request, response):
        if self.mission_active:
            response.success = False
            response.message = 'Ya hay una mision en ejecucion.'
            return response
        yaml_path = self.get_parameter('waypoints_file').get_parameter_value().string_value
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            response.success = False
            response.message = f'Error leyendo YAML: {e}'
            return response

        self.mission_active = True
        threading.Thread(target=self._execute_mission, args=(data,), daemon=True).start()
        response.success = True
        response.message = 'Mision autonoma iniciada.'
        return response

    def _execute_mission(self, data):
        try:
            wps = data.get('waypoints', [])
            if not wps:
                self.get_logger().warn('No hay waypoints en el archivo YAML.')
                return
            goals = [self._create_pose(w['x'], w['y'], w['yaw']) for w in wps]
            self.get_logger().info(f'Iniciando recorrido por {len(goals)} waypoints...')
            self.navigator.followWaypoints(goals)
            last_wp = -1
            while not self.navigator.isTaskComplete():
                fb = self.navigator.getFeedback()
                if fb and fb.current_waypoint != last_wp:
                    last_wp = fb.current_waypoint
                    name = wps[last_wp].get('name', f'WP_{last_wp + 1}')
                    self.get_logger().info(f'Yendo hacia [{last_wp + 1}/{len(goals)}]: {name}')
                time.sleep(0.5)
            res = self.navigator.getResult()
            self.get_logger().info(f'Mision finalizada. Resultado: {res}')
        except Exception as e:
            self.get_logger().error(f'Error durante la mision: {e}')
        finally:
            self.mission_active = False


def main(args=None):
    rclpy.init(args=args)
    node = AutonomousMissionNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
