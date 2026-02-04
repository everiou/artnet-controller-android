#!/usr/bin/env python3
# ArtNet Controller Android - Kivy版本

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.lang import Builder

from artnet_core import ArtNetProtocol, NetworkManager, DMXController, EffectEngine

import threading
import time

# Kivy界面定义
Builder.load_string('''
<MainScreen>:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    
    # 标题
    Label:
        text: 'ArtNet Controller Pro Plus'
        font_size: '20sp'
        bold: True
        size_hint_y: None
        height: '40dp'
    
    # 状态信息
    Label:
        text: root.status_text
        font_size: '14sp'
        size_hint_y: None
        height: '30dp'
    
    # ArtNet设置
    GridLayout:
        cols: 2
        spacing: 5
        size_hint_y: None
        height: '120dp'
        
        Label:
            text: 'Net:'
            font_size: '14sp'
        TextInput:
            id: net_input
            text: '0'
            input_filter: 'int'
            multiline: False
            font_size: '14sp'
        
        Label:
            text: 'Subnet:'
            font_size: '14sp'
        TextInput:
            id: subnet_input
            text: '0'
            input_filter: 'int'
            multiline: False
            font_size: '14sp'
        
        Label:
            text: 'Universe:'
            font_size: '14sp'
        TextInput:
            id: universe_input
            text: '0'
            input_filter: 'int'
            multiline: False
            font_size: '14sp'
        
        Label:
            text: 'Target IP:'
            font_size: '14sp'
        TextInput:
            id: target_ip_input
            text: '255.255.255.255'
            multiline: False
            font_size: '14sp'
    
    # 发送控制
    BoxLayout:
        spacing: 10
        size_hint_y: None
        height: '50dp'
        
        ToggleButton:
            id: send_button
            text: '开始发送' if not self.state else '停止发送'
            on_state: root.toggle_sending(self.state)
            font_size: '14sp'
        
        Button:
            text: '重置通道'
            on_release: root.reset_channels()
            font_size: '14sp'
    
    # 通道控制
    BoxLayout:
        orientation: 'vertical'
        spacing: 5
        
        GridLayout:
            cols: 4
            spacing: 5
            size_hint_y: None
            height: '40dp'
            
            Label:
                text: '通道范围:'
                font_size: '14sp'
            TextInput:
                id: start_channel_input
                text: '1'
                input_filter: 'int'
                multiline: False
                font_size: '14sp'
            Label:
                text: '-'
                font_size: '14sp'
            TextInput:
                id: end_channel_input
                text: '512'
                input_filter: 'int'
                multiline: False
                font_size: '14sp'
        
        GridLayout:
            cols: 3
            spacing: 5
            size_hint_y: None
            height: '60dp'
            
            Label:
                text: '通道值: {:.0f}'.format(root.channel_value)
                font_size: '14sp'
            Slider:
                id: value_slider
                min: 0
                max: 255
                value: root.channel_value
                on_value: root.update_channel_value(self.value)
            Button:
                text: '应用'
                on_release: root.apply_channel_values()
                font_size: '14sp'
    
    # 效果控制
    BoxLayout:
        orientation: 'vertical'
        spacing: 5
        
        GridLayout:
            cols: 2
            spacing: 5
            size_hint_y: None
            height: '40dp'
            
            Label:
                text: '效果类型:'
                font_size: '14sp'
            Spinner:
                id: effect_spinner
                values: ('chase', 'pulse', 'strobe')
                text: 'chase'
                font_size: '14sp'
        
        GridLayout:
            cols: 2
            spacing: 5
            size_hint_y: None
            height: '40dp'
            
            Label:
                text: '方向:'
                font_size: '14sp'
            Spinner:
                id: direction_spinner
                values: ('forward', 'backward', 'bounce')
                text: 'forward'
                font_size: '14sp'
        
        GridLayout:
            cols: 3
            spacing: 5
            size_hint_y: None
            height: '60dp'
            
            Label:
                text: '速度: {:.0f}'.format(root.speed_value)
                font_size: '14sp'
            Slider:
                id: speed_slider
                min: 1
                max: 100
                value: root.speed_value
                on_value: root.update_speed_value(self.value)
            Button:
                text: '运行效果'
                on_release: root.run_effect()
                font_size: '14sp'
        
        Button:
            text: '停止效果'
            on_release: root.stop_effect()
            font_size: '14sp'
            size_hint_y: None
            height: '40dp'
    
    # 录制控制
    BoxLayout:
        spacing: 10
        size_hint_y: None
        height: '50dp'
        
        ToggleButton:
            id: record_button
            text: '开始录制' if not self.state else '停止录制'
            on_state: root.toggle_recording(self.state)
            font_size: '14sp'
        
        Button:
            text: '保存录制'
            on_release: root.save_recorded_data()
            font_size: '14sp'
        
        Button:
            text: '播放录制'
            on_release: root.play_recorded_data()
            font_size: '14sp'
''')

class MainScreen(Screen):
    # 属性定义
    channel_value = NumericProperty(0)
    speed_value = NumericProperty(50)
    status_text = StringProperty('就绪')
    
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        
        # 初始化核心组件
        self.artnet_protocol = ArtNetProtocol()
        self.network_manager = NetworkManager()
        self.dmx_controller = DMXController()
        self.effect_engine = EffectEngine(self.dmx_controller)
        
        # 发送线程控制
        self.sending = False
        self.send_thread = None
        self.last_send_time = 0
        
        # 录制数据
        self.recorded_data = []
        self.recording = False
        
        # 初始化网络
        try:
            if self.network_manager.initialize():
                self.status_text = "网络: 已初始化"
                # 启动网络监听
                self.network_manager.start_listener(callback=self.on_artnet_packet_received)
            else:
                self.status_text = "网络: 初始化失败"
        except Exception as e:
            self.status_text = f"网络: 初始化错误 - {str(e)}"
    
    def toggle_sending(self, state):
        """切换发送状态"""
        if state == 'down':
            self.start_sending()
        else:
            self.stop_sending()
    
    def start_sending(self):
        """开始发送ArtNet数据包"""
        if not self.sending:
            self.sending = True
            self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
            self.send_thread.start()
            self.status_text = "发送中..."
    
    def stop_sending(self):
        """停止发送ArtNet数据包"""
        self.sending = False
        if self.send_thread:
            self.send_thread.join(timeout=1.0)
            self.send_thread = None
        self.status_text = "就绪"
    
    def _send_loop(self):
        """发送数据包的循环"""
        while self.sending:
            try:
                # 获取设置值（只在需要时获取，减少UI访问）
                net = int(self.ids.net_input.text) if self.ids.net_input.text else 0
                subnet = int(self.ids.subnet_input.text) if self.ids.subnet_input.text else 0
                universe = int(self.ids.universe_input.text) if self.ids.universe_input.text else 0
                target_ip = self.ids.target_ip_input.text or "255.255.255.255"
                
                # 构建数据包
                dmx_data = self.dmx_controller.get_channel_data_for_artnet()
                packet = self.artnet_protocol.build_dmx_packet(net, subnet, universe, dmx_data)
                
                # 发送数据包
                start_time = time.time()
                if self.network_manager.send_packet(packet, target_ip):
                    # 限制发送频率，确保稳定的50Hz
                    elapsed = time.time() - start_time
                    sleep_time = max(0.02 - elapsed, 0.001)  # 最小0.001秒
                    time.sleep(sleep_time)
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"发送错误: {e}")
                time.sleep(0.1)
    
    def update_channel_value(self, value):
        """更新通道值"""
        self.channel_value = value
    
    def update_speed_value(self, value):
        """更新速度值"""
        self.speed_value = value
    
    def apply_channel_values(self):
        """应用通道值"""
        try:
            start_channel = int(self.ids.start_channel_input.text) if self.ids.start_channel_input.text else 1
            end_channel = int(self.ids.end_channel_input.text) if self.ids.end_channel_input.text else 512
            value = int(self.channel_value)
            
            self.dmx_controller.set_channel_range(start_channel, end_channel, value)
            self.status_text = f"已应用通道值 {value} 到通道 {start_channel}-{end_channel}"
        except Exception as e:
            self.status_text = f"错误: {str(e)}"
    
    def reset_channels(self):
        """重置所有通道为0"""
        self.dmx_controller.reset_all_channels()
        self.status_text = "已重置所有通道"
    
    def run_effect(self):
        """运行效果"""
        try:
            effect_type = self.ids.effect_spinner.text
            direction = self.ids.direction_spinner.text
            speed = int(self.speed_value)
            start_channel = int(self.ids.start_channel_input.text) if self.ids.start_channel_input.text else 1
            end_channel = int(self.ids.end_channel_input.text) if self.ids.end_channel_input.text else 512
            intensity = int(self.channel_value)
            
            if effect_type == 'chase':
                self.effect_engine.run_chase_effect(
                    speed=speed,
                    direction=direction,
                    pattern="linear",
                    start_channel=start_channel,
                    end_channel=end_channel,
                    intensity=intensity
                )
            elif effect_type == 'pulse':
                self.effect_engine.run_pulse_effect(
                    speed=speed,
                    intensity=intensity,
                    start_channel=start_channel,
                    end_channel=end_channel
                )
            elif effect_type == 'strobe':
                self.effect_engine.run_strobe_effect(
                    speed=speed,
                    intensity=intensity,
                    start_channel=start_channel,
                    end_channel=end_channel
                )
            
            self.status_text = f"运行效果: {effect_type}"
        except Exception as e:
            self.status_text = f"错误: {str(e)}"
    
    def stop_effect(self):
        """停止效果"""
        self.effect_engine.stop_effect()
        self.status_text = "已停止效果"
    
    def toggle_recording(self, state):
        """切换录制状态"""
        if state == 'down':
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """开始录制"""
        self.recorded_data = []
        self.recording = True
        self.status_text = "录制中..."
        
        # 开始录制线程
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()
    
    def stop_recording(self):
        """停止录制"""
        self.recording = False
        if hasattr(self, 'record_thread'):
            self.record_thread.join(timeout=1.0)
        self.status_text = f"已停止录制，记录了 {len(self.recorded_data)} 帧"
    
    def _record_loop(self):
        """录制循环"""
        while self.recording:
            timestamp = time.time()
            channels = self.dmx_controller.get_all_channels()
            self.recorded_data.append((timestamp, channels))
            time.sleep(0.05)  # 20Hz
    
    def save_recorded_data(self):
        """保存录制数据"""
        if not self.recorded_data:
            self.status_text = "没有录制数据"
            return
        
        try:
            import json
            import os
            
            # 创建保存目录
            os.makedirs('recordings', exist_ok=True)
            
            # 生成文件名
            filename = f"recordings/recording_{int(time.time())}.json"
            
            # 转换数据格式
            data_to_save = []
            start_time = self.recorded_data[0][0]
            for timestamp, channels in self.recorded_data:
                data_to_save.append({
                    'time': timestamp - start_time,
                    'channels': channels
                })
            
            # 保存文件
            with open(filename, 'w') as f:
                json.dump(data_to_save, f)
            
            self.status_text = f"已保存录制数据到 {filename}"
        except Exception as e:
            self.status_text = f"保存错误: {str(e)}"
    
    def play_recorded_data(self):
        """播放录制数据"""
        if not self.recorded_data:
            self.status_text = "没有录制数据"
            return
        
        self.status_text = "播放中..."
        
        # 开始播放线程
        play_thread = threading.Thread(target=self._playback_loop, daemon=True)
        play_thread.start()
    
    def _playback_loop(self):
        """播放循环"""
        if not self.recorded_data:
            return
        
        start_time = time.time()
        for i, (timestamp, channels) in enumerate(self.recorded_data):
            # 计算延迟
            target_time = start_time + (timestamp - self.recorded_data[0][0])
            current_time = time.time()
            if current_time < target_time:
                time.sleep(target_time - current_time)
            
            # 设置通道值
            for j, value in enumerate(channels):
                self.dmx_controller.set_channel(j + 1, value)
            
            # 检查是否要停止
            if not self.sending:
                break
        
        self.status_text = "播放完成"
    
    def on_artnet_packet_received(self, data, addr):
        """处理接收到的ArtNet数据包"""
        try:
            packet_info = self.artnet_protocol.parse_packet(data)
            if packet_info:
                # 可以在这里处理接收到的数据包
                pass
        except Exception as e:
            print(f"解析数据包错误: {e}")
    
    def on_stop(self):
        """应用停止时的清理"""
        self.stop_sending()
        self.effect_engine.stop_effect()
        self.network_manager.close()

class ArtNetControllerApp(App):
    """ArtNet控制器应用"""
    
    def build(self):
        """构建应用"""
        return MainScreen()

if __name__ == '__main__':
    ArtNetControllerApp().run()
