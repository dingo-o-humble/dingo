import os

from launch import LaunchDescription
from launch.substitutions import Command, LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.conditions import IfCondition
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    dingo_control_directory = get_package_share_directory("dingo_control")
    xacro_path = os.path.join(
        get_package_share_directory("dingo_description"), "urdf", "dingo.urdf.xacro"
    )

    if os.getenv("DINGO_OMNI", 0):
        control_yaml = os.path.join(
            dingo_control_directory, "config", "control_omni.yaml"
        )
    else:
        control_yaml = os.path.join(
            dingo_control_directory, "config", "control_diff.yaml"
        )

    twist_mux_yaml = os.path.join(dingo_control_directory, "config", "twist_mux.yaml")

    physical_robot = LaunchConfiguration("physical_robot")
    use_sim_time = LaunchConfiguration("use_sim_time")

    robot_description_parameter = {
        "robot_description": Command(
            ["xacro", " ", xacro_path, " ", "physical_robot:=", physical_robot]
        )
    }

    # Declare the launch arguments
    declare_physical_robot_cmd = DeclareLaunchArgument(
        "physical_robot",
        default_value="true",
        description="Physical robot if true, simulation if false",
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Whether or not to use simulation time",
    )

    # Specify the actions
    controller_manager_node = Node(
        condition=IfCondition(physical_robot),
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description_parameter, control_yaml],
        output={
            "stdout": "screen",
            "stderr": "screen",
        },
    )

    spawn_dd_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["dingo_velocity_controller"],
        output="screen",
    )

    spawn_jsb_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["dingo_joint_broadcaster"],
        output="screen",
    )

    # declare_twist_mux_node = Node(
    #     package="twist_mux",
    #     executable="twist_mux",
    #     output="screen",
    #     remappings={("/cmd_vel_out", "/dingo_velocity_controller/cmd_vel_unstamped")},
    #     parameters=[twist_mux_yaml, {"use_sim_time": use_sim_time}],
    # )

    ld = LaunchDescription()

    # Add any conditioned actions
    ld.add_action(declare_physical_robot_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(controller_manager_node)
    ld.add_action(spawn_dd_controller)
    ld.add_action(spawn_jsb_controller)
    # ld.add_action(declare_twist_mux_node)

    return ld
