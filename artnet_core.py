#!/usr/bin/env python3
# ArtNet Core - 核心功能类

import socket
import threading
import time
import json
import os

# ArtNetProtocol 类
class ArtNetProtocol:
    """ArtNet协议实现类"""
    
    # ArtNet数据包常量
    ARTNET_HEADER = b'Art-Net\x00'
    OPCODE_DMX = 0x5000  # DMX数据数据包操作码
    
    def __init__(self):
        """初始化ArtNet协议实例"""
        pass
    
    def get_port_address(self, net, subnet, universe):
        """
        计算端口地址
        
        Args:
            net (int): 网络号 (0-127)
            subnet (int): 子网号 (0-15)
            universe (int): 宇宙号 (0-15)
            
        Returns:
            int: 16位端口地址
        """
        # 端口地址格式: [7位Net][4位Sub-Net][4位Universe]
        return ((net & 0x7F) << 8) | ((subnet & 0x0F) << 4) | (universe & 0x0F)
    
    def build_dmx_packet(self, net, subnet, universe, dmx_data):
        """
        构建DMX数据数据包
        
        Args:
            net (int): 网络号 (0-127)
            subnet (int): 子网号 (0-15)
            universe (int): 宇宙号 (0-15)
            dmx_data (list): DMX通道数据列表，长度为512，每个元素为0-255
            
        Returns:
            bytes: 完整的ArtNet DMX数据包
        """
        # 确保dmx_data长度为512
        dmx_data_512 = [0] * 512
        for i in range(min(len(dmx_data), 512)):
            dmx_data_512[i] = dmx_data[i] & 0xFF
        
        # 计算端口地址
        port_address = self.get_port_address(net, subnet, universe)
        
        # 构建数据包
        packet = bytearray()
        
        # 添加ArtNet头部
        packet.extend(self.ARTNET_HEADER)
        
        # 添加操作码 (小端序)
        packet.extend(self.OPCODE_DMX.to_bytes(2, byteorder='little'))
        
        # 添加协议版本 (14)
        packet.extend((14).to_bytes(2, byteorder='big'))
        
        # 添加序列号 (0)
        packet.append(0)
        
        # 添加物理端口 (0)
        packet.append(0)
        
        # 添加端口地址 (小端序)
        packet.extend(port_address.to_bytes(2, byteorder='little'))
        
        # 添加数据长度 (512, 大端序)
        packet.extend((512).to_bytes(2, byteorder='big'))
        
        # 添加DMX数据
        for value in dmx_data_512:
            packet.append(value)
        
        return bytes(packet)
    
    def parse_packet(self, data):
        """
        解析ArtNet数据包
        
        Args:
            data (bytes): 接收到的数据包
            
        Returns:
            dict: 解析后的数据包信息，包括操作码、端口地址、DMX数据等
        """
        if len(data) < 18:
            return None
        
        # 检查头部
        if data[:8] != self.ARTNET_HEADER:
            return None
        
        # 解析操作码
        opcode = int.from_bytes(data[8:10], byteorder='little')
        
        # 解析协议版本
        version = int.from_bytes(data[10:12], byteorder='big')
        
        # 解析序列号
        sequence = data[12]
        
        # 解析物理端口
        physical = data[13]
        
        # 解析端口地址
        port_address = int.from_bytes(data[14:16], byteorder='little')
        
        # 解析数据长度
        length = int.from_bytes(data[16:18], byteorder='big')
        
        # 解析DMX数据
        dmx_data = list(data[18:18+length])
        
        # 从端口地址中提取Net、Subnet、Universe
        net = (port_address >> 8) & 0x7F
        subnet = (port_address >> 4) & 0x0F
        universe = port_address & 0x0F
        
        return {
            'opcode': opcode,
            'version': version,
            'sequence': sequence,
            'physical': physical,
            'port_address': port_address,
            'net': net,
            'subnet': subnet,
            'universe': universe,
            'length': length,
            'dmx_data': dmx_data
        }
    
    def validate_address(self, net, subnet, universe):
        """
        验证地址参数是否有效
        
        Args:
            net (int): 网络号
            subnet (int): 子网号
            universe (int): 宇宙号
            
        Returns:
            bool: 地址是否有效
        """
        return (0 <= net <= 127) and (0 <= subnet <= 15) and (0 <= universe <= 15)
    
    def format_address(self, net, subnet, universe):
        """
        格式化地址为字符串
        
        Args:
            net (int): 网络号
            subnet (int): 子网号
            universe (int): 宇宙号
            
        Returns:
            str: 格式化的地址字符串
        """
        if not self.validate_address(net, subnet, universe):
            return "无效地址"
        return f"{net}.{subnet}.{universe}"

# NetworkManager 类
class NetworkManager:
    """网络管理类，处理ArtNet数据包的发送和接收"""
    
    def __init__(self):
        """初始化网络管理器"""
        self.socket = None
        self.listener_thread = None
        self.running = False
        self.callback = None
        self.broadcast_ip = "255.255.255.255"
        self.artnet_port = 6454
    
    def initialize(self):
        """
        初始化网络连接
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 创建UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 绑定到本地端口，以便接收数据包
            self.socket.bind(("", self.artnet_port))
            self.socket.settimeout(0.1)  # 设置超时，避免阻塞
            return True
        except Exception as e:
            print(f"网络初始化失败: {e}")
            self.socket = None
            return False
    
    def send_packet(self, packet, target_ip=None, port=None):
        """
        发送ArtNet数据包
        
        Args:
            packet (bytes): 要发送的数据包
            target_ip (str, optional): 目标IP地址，默认为广播地址
            port (int, optional): 目标端口，默认为ArtNet默认端口
            
        Returns:
            bool: 发送是否成功
        """
        if not self.socket:
            if not self.initialize():
                return False
        
        try:
            ip = target_ip or self.broadcast_ip
            p = port or self.artnet_port
            self.socket.sendto(packet, (ip, p))
            return True
        except Exception as e:
            print(f"发送数据包失败: {e}")
            return False
    
    def start_listener(self, callback=None):
        """
        开始监听传入的ArtNet数据包
        
        Args:
            callback (function, optional): 接收到数据包时的回调函数
        """
        if not self.socket:
            if not self.initialize():
                return
        
        self.callback = callback
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen, daemon=True)
        self.listener_thread.start()
    
    def stop_listener(self):
        """
        停止监听传入的ArtNet数据包
        """
        self.running = False
        if self.listener_thread:
            self.listener_thread.join(timeout=1.0)
            self.listener_thread = None
    
    def _listen(self):
        """
        监听线程的主函数
        """
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)  # 接收数据包
                if self.callback:
                    try:
                        self.callback(data, addr)
                    except Exception as callback_e:
                        if self.running:
                            print(f"回调函数执行失败: {callback_e}")
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:  # 只在运行时打印错误
                    print(f"接收数据包失败: {e}")
                break
    
    def close(self):
        """
        关闭网络连接
        """
        self.stop_listener()
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(f"关闭socket失败: {e}")
            self.socket = None
    
    def set_broadcast_ip(self, ip):
        """
        设置默认广播IP地址
        
        Args:
            ip (str): 广播IP地址
        """
        self.broadcast_ip = ip
    
    def set_artnet_port(self, port):
        """
        设置ArtNet端口
        
        Args:
            port (int): ArtNet端口号
        """
        self.artnet_port = port
    
    def is_connected(self):
        """
        检查网络连接状态
        
        Returns:
            bool: 网络是否已连接
        """
        return self.socket is not None

# DMXController 类
class DMXController:
    """DMX控制器类，管理DMX通道数据"""
    
    def __init__(self, num_channels=512):
        """
        初始化DMX控制器
        
        Args:
            num_channels (int, optional): DMX通道数量，默认为512
        """
        self.num_channels = num_channels
        self.channels = [0] * num_channels  # 初始化所有通道为0
        self.last_update_time = 0
    
    def set_channel(self, channel, value):
        """
        设置单个DMX通道的值
        
        Args:
            channel (int): 通道号 (1-512)
            value (int): 通道值 (0-255)
            
        Returns:
            bool: 设置是否成功
        """
        if 1 <= channel <= self.num_channels:
            index = channel - 1
            if self.channels[index] != value:
                self.channels[index] = value & 0xFF  # 确保值在0-255范围内
                self.last_update_time = self._get_current_time()
            return True
        return False
    
    def set_channels(self, channels, values):
        """
        设置多个DMX通道的值
        
        Args:
            channels (list): 通道号列表
            values (list): 通道值列表
            
        Returns:
            bool: 设置是否成功
        """
        if len(channels) != len(values):
            return False
        
        updated = False
        for channel, value in zip(channels, values):
            if self.set_channel(channel, value):
                updated = True
        
        return updated
    
    def set_channel_range(self, start_channel, end_channel, value):
        """
        设置一个范围内的DMX通道值
        
        Args:
            start_channel (int): 起始通道号
            end_channel (int): 结束通道号
            value (int): 通道值
            
        Returns:
            bool: 设置是否成功
        """
        if 1 <= start_channel <= end_channel <= self.num_channels:
            updated = False
            for channel in range(start_channel, end_channel + 1):
                if self.set_channel(channel, value):
                    updated = True
            return updated
        return False
    
    def get_channel(self, channel):
        """
        获取单个DMX通道的值
        
        Args:
            channel (int): 通道号 (1-512)
            
        Returns:
            int: 通道值，范围0-255；如果通道号无效，返回-1
        """
        if 1 <= channel <= self.num_channels:
            return self.channels[channel - 1]
        return -1
    
    def get_all_channels(self):
        """
        获取所有DMX通道的值
        
        Returns:
            list: 所有通道值的列表
        """
        return self.channels.copy()
    
    def reset_all_channels(self):
        """
        重置所有DMX通道为0
        """
        self.channels = [0] * self.num_channels
        self.last_update_time = self._get_current_time()
    
    def get_channel_count(self):
        """
        获取DMX通道数量
        
        Returns:
            int: 通道数量
        """
        return self.num_channels
    
    def get_last_update_time(self):
        """
        获取最后更新时间
        
        Returns:
            float: 最后更新时间的时间戳
        """
        return self.last_update_time
    
    def _get_current_time(self):
        """
        获取当前时间戳
        
        Returns:
            float: 当前时间戳
        """
        return time.time()
    
    def apply_preset(self, preset):
        """
        应用通道预设
        
        Args:
            preset (dict): 预设字典，格式为 {"通道号": 值} 或 {"通道范围": 值}
            
        Returns:
            bool: 应用是否成功
        """
        updated = False
        
        for key, value in preset.items():
            if isinstance(key, str) and '-' in key:
                # 处理通道范围
                try:
                    start, end = map(int, key.split('-'))
                    if self.set_channel_range(start, end, value):
                        updated = True
                except ValueError:
                    pass
            elif isinstance(key, int):
                # 处理单个通道
                if self.set_channel(key, value):
                    updated = True
        
        return updated
    
    def get_channel_data_for_artnet(self):
        """
        获取用于ArtNet数据包的DMX通道数据
        
        Returns:
            list: DMX通道数据列表，长度为512
        """
        # 创建通道数据的副本，避免线程冲突
        channels_copy = self.channels.copy()
        
        # 确保返回的数据长度为512
        if len(channels_copy) < 512:
            return channels_copy + [0] * (512 - len(channels_copy))
        elif len(channels_copy) > 512:
            return channels_copy[:512]
        return channels_copy

# EffectEngine 类
class EffectEngine:
    """效果引擎类，实现各种灯光效果"""
    
    def __init__(self, dmx_controller):
        """
        初始化效果引擎
        
        Args:
            dmx_controller (DMXController): DMX控制器实例
        """
        self.dmx_controller = dmx_controller
        self.running = False
        self.effect_thread = None
    
    def run_chase_effect(self, speed, direction="forward", pattern="linear", 
                        start_channel=1, end_channel=512, intensity=255):
        """
        运行跑灯效果
        
        Args:
            speed (int): 速度 (1-100)
            direction (str): 方向 (forward, backward, bounce)
            pattern (str): 模式 (linear, random, alternate)
            start_channel (int): 起始通道
            end_channel (int): 结束通道
            intensity (int): 强度 (0-255)
        """
        self.stop_effect()
        self.running = True
        
        # 使用局部变量存储通道范围
        local_start = start_channel
        local_end = end_channel
        
        self.effect_thread = threading.Thread(
            target=self._run_chase,
            args=(speed, direction, pattern, local_start, local_end, intensity),
            daemon=True
        )
        self.effect_thread.start()
    
    def _run_chase(self, speed, direction, pattern, start_channel, end_channel, intensity):
        """
        运行跑灯效果的线程函数
        """
        channels = list(range(start_channel, end_channel + 1))
        delay = (100 - speed) / 100.0  # 速度转换为延迟
        
        while self.running:
            if pattern == "linear":
                if direction == "forward":
                    for ch in channels:
                        if not self.running:
                            break
                        self.dmx_controller.set_channel(ch, intensity)
                        time.sleep(delay)
                        self.dmx_controller.set_channel(ch, 0)
                elif direction == "backward":
                    for ch in reversed(channels):
                        if not self.running:
                            break
                        self.dmx_controller.set_channel(ch, intensity)
                        time.sleep(delay)
                        self.dmx_controller.set_channel(ch, 0)
                elif direction == "bounce":
                    for ch in channels:
                        if not self.running:
                            break
                        self.dmx_controller.set_channel(ch, intensity)
                        time.sleep(delay)
                        self.dmx_controller.set_channel(ch, 0)
                    for ch in reversed(channels[1:-1]):
                        if not self.running:
                            break
                        self.dmx_controller.set_channel(ch, intensity)
                        time.sleep(delay)
                        self.dmx_controller.set_channel(ch, 0)
            elif pattern == "random":
                import random
                random.shuffle(channels)
                for ch in channels:
                    if not self.running:
                        break
                    self.dmx_controller.set_channel(ch, intensity)
                    time.sleep(delay)
                    self.dmx_controller.set_channel(ch, 0)
            elif pattern == "alternate":
                even_channels = [ch for ch in channels if ch % 2 == 0]
                odd_channels = [ch for ch in channels if ch % 2 != 0]
                
                for ch in even_channels:
                    if not self.running:
                        break
                    self.dmx_controller.set_channel(ch, intensity)
                time.sleep(delay)
                for ch in even_channels:
                    if not self.running:
                        break
                    self.dmx_controller.set_channel(ch, 0)
                
                for ch in odd_channels:
                    if not self.running:
                        break
                    self.dmx_controller.set_channel(ch, intensity)
                time.sleep(delay)
                for ch in odd_channels:
                    if not self.running:
                        break
                    self.dmx_controller.set_channel(ch, 0)
    
    def run_pulse_effect(self, speed, intensity=255, start_channel=1, end_channel=512):
        """
        运行脉冲效果
        
        Args:
            speed (int): 速度 (1-100)
            intensity (int): 强度 (0-255)
            start_channel (int): 起始通道
            end_channel (int): 结束通道
        """
        self.stop_effect()
        self.running = True
        
        self.effect_thread = threading.Thread(
            target=self._run_pulse,
            args=(speed, intensity, start_channel, end_channel),
            daemon=True
        )
        self.effect_thread.start()
    
    def _run_pulse(self, speed, intensity, start_channel, end_channel):
        """
        运行脉冲效果的线程函数
        """
        delay = (100 - speed) / 1000.0  # 速度转换为延迟
        
        while self.running:
            # 渐亮
            for i in range(0, intensity + 1, 5):
                if not self.running:
                    break
                self.dmx_controller.set_channel_range(start_channel, end_channel, i)
                time.sleep(delay)
            
            # 渐暗
            for i in range(intensity, -1, -5):
                if not self.running:
                    break
                self.dmx_controller.set_channel_range(start_channel, end_channel, i)
                time.sleep(delay)
    
    def run_strobe_effect(self, speed, intensity=255, start_channel=1, end_channel=512):
        """
        运行频闪效果
        
        Args:
            speed (int): 速度 (1-100)
            intensity (int): 强度 (0-255)
            start_channel (int): 起始通道
            end_channel (int): 结束通道
        """
        self.stop_effect()
        self.running = True
        
        self.effect_thread = threading.Thread(
            target=self._run_strobe,
            args=(speed, intensity, start_channel, end_channel),
            daemon=True
        )
        self.effect_thread.start()
    
    def _run_strobe(self, speed, intensity, start_channel, end_channel):
        """
        运行频闪效果的线程函数
        """
        delay = (100 - speed) / 1000.0  # 速度转换为延迟
        
        while self.running:
            self.dmx_controller.set_channel_range(start_channel, end_channel, intensity)
            time.sleep(delay)
            self.dmx_controller.set_channel_range(start_channel, end_channel, 0)
            time.sleep(delay)
    
    def stop_effect(self):
        """
        停止当前运行的效果
        """
        self.running = False
        if self.effect_thread:
            self.effect_thread.join(timeout=1.0)
            self.effect_thread = None
