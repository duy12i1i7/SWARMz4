#!/usr/bin/env python3
import sys
import subprocess
import time
import math
import re


def get_value_from_model(command, target_index):
    """
    Chạy lệnh gz model và trích xuất giá trị cần (target_index: 0->roll, 1->pitch, 2->yaw)
    từ dòng chứa RPY của block "Pose [ XYZ (m) ] [ RPY (rad) ]:" (loại trừ phần "Inertial").
    """
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi chạy lệnh: {' '.join(command)}")
        return None

    output = result.stdout
    lines = output.splitlines()
    for i, line in enumerate(lines):
        if "Pose [ XYZ (m) ] [ RPY (rad) ]:" in line and "Inertial" not in line:
            # Dòng sau chứa tọa độ, dòng kế tiếp chứa các giá trị RPY
            if i + 2 < len(lines):
                rpy_line = lines[i + 2].strip().strip("[]")
                parts = rpy_line.split()
                if len(parts) >= 3:
                    try:
                        value = float(parts[target_index])
                        return value
                    except ValueError:
                        print("Không chuyển đổi được giá trị RPY sang số thực.")
                        return None
    return None

def get_pitch(warship_id):
    # Lấy pitch từ link gun: pitch ở vị trí index 1 của RPY
    cmd = ["gz", "model", "-m", warship_id, "--link", "gun"]
    return get_value_from_model(cmd, target_index=1)

def get_yaw(warship_id):
    # Lấy yaw từ link gr: yaw ở vị trí index 2 của RPY
    cmd = ["gz", "model", "-m", warship_id, "--link", "trusted"]
    return get_value_from_model(cmd, target_index=2)

def publish_command(model, j, data_value):
    """
    Gửi lệnh publish đến topic đã cho với giá trị data_value.
    """
    topic = f"/model/{model}/joint/{j}/cmd_vel"
    # Chuỗi payload dùng để thực thi (không có dấu nháy đơn)
    payload_for_execution = f"data: {data_value}"
    # Chuỗi payload dùng để in ra (có dấu nháy đơn như mong muốn)
    payload_for_print = f"'data: {data_value}'"
    
    # Xây dựng lệnh với payload thực thi không có dấu nháy đơn
    cmd = ["gz", "topic", "-t", topic, "-m", "gz.msgs.Double", "-p", payload_for_execution]
    print(f"Thực thi lệnh: {' '.join(['gz', 'topic', '-t', topic, '-m', 'gz.msgs.Double', '-p', payload_for_print])}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"Lỗi khi gửi lệnh cho topic {topic}")


def adjust_axis(get_current, model, j, speed, target_value, axis_name, tolerance=0.5, max_retries=10):  # Giảm tolerance và thêm max_retries
    print(f"--- Điều chỉnh {axis_name} đến mục tiêu: {target_value} ---")
    retry_count = 0
    
    while retry_count < max_retries:
        current_value = get_current(model)
        if current_value is None:
            print(f"Không lấy được giá trị hiện tại của {axis_name}. Thử lại")
            retry_count += 1
            time.sleep(0.5)  # Thêm delay
            continue

        diff = target_value - current_value
        print(f"{axis_name} hiện tại = {current_value:.6f} | Hiệu lệch = {diff:.6f}")

        if abs(diff) < tolerance:
            publish_command(model, j, 0.0)
            print(f"{axis_name} đã đạt mục tiêu.")
            return True  # Thêm return value
        else:    
            data = speed if diff > 0 else -speed
            publish_command(model, j, data)
            time.sleep(0.1)  # Thêm delay để tránh quá tải
        
            retry_count += 1

    print(f"Không thể đạt mục tiêu {axis_name} sau {max_retries} lần thử")
    return False  # Thêm return value

def yaw_pitch_to_vector(yaw, pitch):
    # Công thức chuyển đổi cơ bản từ yaw, pitch sang vector đơn vị
    vx = math.cos(pitch) * math.cos(yaw)
    vy = math.cos(pitch) * math.sin(yaw)
    vz = math.sin(pitch)
    return [vx, vy, vz]

def cleanup(model):
    """Dừng tất cả chuyển động"""
    publish_command(model, "j1", 0.0)
    publish_command(model, "j2", 0.0)
    print("Đã dừng tất cả động cơ")

def main():
    if len(sys.argv) != 5:
        print("Usage: python3 cannon.py [warship_name] [target_yaw] [target_pitch] [rotation_speed]")
        sys.exit(1)
    elif (float(sys.argv[2]) > 1.5 or float(sys.argv[2]) < -1.57):
    	print("out of yaw degree")
    	sys.exit(1)
    elif (float(sys.argv[3]) < 0 or float(sys.argv[3]) > 3.14):
    	print("out of pitch degree")
    	sys.exit(1)
    elif (float(sys.argv[4]) < 0 or float(sys.argv[4]) > 1):
    	print("out of rotation speed")
    	sys.exit(1)
    try:
        target_warship = sys.argv[1]
        target_yaw = float(sys.argv[2])
        target_pitch = float(sys.argv[3])
        cn_speed = float(sys.argv[4])
        success_pitch = adjust_axis(get_pitch, target_warship, "j1", cn_speed, target_pitch, "Pitch")
        success_yaw = adjust_axis(get_yaw, target_warship, "j2", cn_speed, target_yaw, "Yaw")

        if success_pitch and success_yaw:
                print("done")
                sys.exit(0)  # Thoát với mã thành công
        else:
                print("failed")
                sys.exit(2)  # Thoát với mã lỗi

    except ValueError:
        print("Vui lòng nhập 4 giá trị số cho"+ValueError)
        sys.exit(1)

    finally:
        cleanup(target_warship)
    

if __name__ == '__main__':
    main()
