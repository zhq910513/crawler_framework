# -*- coding: utf-8 -*-

import json
import os
import platform
import socket
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

import psutil

from plugins.log import logger


class DeviceInfo:
    """跨平台系统信息获取类"""

    def __init__(self):
        """初始化系统信息获取器"""
        self.os_type = platform.system().lower()  # windows, linux, darwin(mac)
        self.os_bit = platform.architecture()[0]  # 32bit or 64bit
        self._init_time = datetime.now()
        self._check_platform()

    def _check_platform(self) -> None:
        """检查并记录平台信息"""
        logger.info(f"当前操作系统: {self.os_type}, 位数: {self.os_bit}")
        if self.os_type not in ['windows', 'linux', 'darwin']:
            logger.warning(f"未经完全测试的操作系统: {self.os_type}")

    def get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息（跨平台）"""
        try:
            base_info = {
                'physical_count': psutil.cpu_count(logical=False) or 2,
                'logical_count': psutil.cpu_count() or 4,
                'architecture': platform.machine(),
                'processor': platform.processor()
            }

            # Windows特定信息
            if self.os_type == 'windows':
                try:
                    import wmi
                    w = wmi.WMI()
                    processor = w.Win32_Processor()[0]
                    base_info.update({
                        'name': processor.Name,
                        'manufacturer': processor.Manufacturer,
                        'max_clock_speed': processor.MaxClockSpeed
                    })
                except ImportError:
                    logger.debug("WMI模块未安装，无法获取详细CPU信息")
                except Exception as e:
                    logger.debug(f"获取Windows CPU详细信息失败: {e}")

            # Linux特定信息
            elif self.os_type == 'linux':
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        cpu_info = f.readlines()

                    cpu_fields = {}
                    for line in cpu_info:
                        if ':' in line:
                            key, value = line.split(':')
                            cpu_fields[key.strip()] = value.strip()

                    base_info.update({
                        'model_name': cpu_fields.get('model name', ''),
                        'cpu_mhz': cpu_fields.get('cpu MHz', ''),
                        'cache_size': cpu_fields.get('cache size', '')
                    })
                except Exception as e:
                    logger.debug(f"无法读取/proc/cpuinfo: {e}")

            # 添加通用CPU使用率信息
            base_info.update({
                'usage_percent': psutil.cpu_percent(interval=1),
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
                'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            })

            return base_info

        except Exception as e:
            logger.error(f"获取CPU信息失败: {e}")
            return {}

    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息（跨平台）"""
        try:
            memory_info = {
                'virtual_memory': psutil.virtual_memory()._asdict(),
                'swap_memory': psutil.swap_memory()._asdict()
            }

            # Windows特定信息
            if self.os_type == 'windows':
                try:
                    import wmi
                    w = wmi.WMI()
                    for memory in w.Win32_PhysicalMemory():
                        memory_info.update({
                            'manufacturer': memory.Manufacturer,
                            'speed': memory.Speed,
                            'memory_type': memory.MemoryType
                        })
                except ImportError:
                    logger.debug("WMI模块未安装，无法获取详细内存信息")
                except Exception as e:
                    logger.debug(f"获取Windows内存详细信息失败: {e}")

            # Linux特定信息
            elif self.os_type == 'linux':
                try:
                    with open('/proc/meminfo', 'r') as f:
                        mem_info = f.readlines()

                    mem_fields = {}
                    for line in mem_info:
                        if ':' in line:
                            key, value = line.split(':')
                            mem_fields[key.strip()] = value.strip()

                    memory_info['detailed'] = mem_fields
                except Exception as e:
                    logger.debug(f"无法读取/proc/meminfo: {e}")

            return memory_info

        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return {}

    def get_disk_info(self) -> Dict[str, Any]:
        """获取磁盘信息（跨平台）"""
        try:
            disk_info = {
                'partitions': {},
                'io_counters': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {}
            }

            # 获取分区信息
            for partition in psutil.disk_partitions(all=True):
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info['partitions'][partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    }
                except Exception:
                    continue

            # Windows特定信息
            if self.os_type == 'windows':
                try:
                    import wmi
                    w = wmi.WMI()
                    disk_info['physical_disks'] = []
                    for disk in w.Win32_DiskDrive():
                        disk_info['physical_disks'].append({
                            'caption': disk.Caption,
                            'size': disk.Size,
                            'interface_type': disk.InterfaceType
                        })
                except ImportError:
                    logger.debug("WMI模块未安装，无法获取详细磁盘信息")
                except Exception as e:
                    logger.debug(f"获取Windows磁盘详细信息失败: {e}")

            # Linux特定信息
            elif self.os_type == 'linux':
                try:
                    disk_info['block_devices'] = []
                    for device in os.listdir('/sys/block'):
                        with open(f'/sys/block/{device}/size') as f:
                            size = int(f.read().strip()) * 512  # 扇区数 * 512字节
                        disk_info['block_devices'].append({
                            'device': device,
                            'size': size
                        })
                except Exception as e:
                    logger.debug(f"无法读取块设备信息: {e}")

            return disk_info

        except Exception as e:
            logger.error(f"获取磁盘信息失败: {e}")
            return {}

    def get_network_info(self) -> Dict[str, Any]:
        """获取网络信息（跨平台）"""
        try:
            network_info = {
                'hostname': socket.gethostname(),
                'interfaces': {},
                'io_counters': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
            }

            # 获取IP地址
            try:
                network_info['ip_address'] = socket.gethostbyname(socket.gethostname())
            except Exception:
                network_info['ip_address'] = '127.0.0.1'

            # 获取MAC地址
            network_info['mac_address'] = ':'.join(
                ['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                 for elements in range(0, 2 * 6, 2)][::-1]
            )

            # 获取网络接口信息
            for interface, addresses in psutil.net_if_addrs().items():
                network_info['interfaces'][interface] = [addr._asdict() for addr in addresses]

            # Windows特定信息
            if self.os_type == 'windows':
                try:
                    import wmi
                    w = wmi.WMI()
                    network_info['adapters'] = []
                    for adapter in w.Win32_NetworkAdapter():
                        if adapter.PhysicalAdapter:
                            network_info['adapters'].append({
                                'name': adapter.Name,
                                'adapter_type': adapter.AdapterType,
                                'manufacturer': adapter.Manufacturer,
                                'mac_address': adapter.MACAddress
                            })
                except ImportError:
                    logger.debug("WMI模块未安装，无法获取详细网络信息")
                except Exception as e:
                    logger.debug(f"获取Windows网络详细信息失败: {e}")

            # Linux特定信息
            elif self.os_type == 'linux':
                try:
                    network_info['routing_table'] = []
                    with open('/proc/net/route') as f:
                        for line in f.readlines()[1:]:
                            fields = line.strip().split()
                            network_info['routing_table'].append({
                                'interface': fields[0],
                                'destination': fields[1],
                                'gateway': fields[2]
                            })
                except Exception as e:
                    logger.debug(f"无法读取路由表信息: {e}")

            return network_info

        except Exception as e:
            logger.error(f"获取网络信息失败: {e}")
            return {}

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息（跨平台）"""
        try:
            system_info = {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'hostname': socket.gethostname(),
                'python_version': platform.python_version(),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
                'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Windows特定信息
            if self.os_type == 'windows':
                try:
                    import wmi
                    w = wmi.WMI()
                    os_info = w.Win32_OperatingSystem()[0]
                    system_info.update({
                        'os_name': os_info.Caption,
                        'os_architecture': os_info.OSArchitecture,
                        'os_manufacturer': os_info.Manufacturer,
                        'system_directory': os_info.SystemDirectory,
                        'windows_directory': os_info.WindowsDirectory
                    })
                except ImportError:
                    logger.debug("WMI模块未安装，无法获取详细系统信息")
                except Exception as e:
                    logger.debug(f"获取Windows系统详细信息失败: {e}")

            # Linux特定信息
            elif self.os_type == 'linux':
                try:
                    # 获取Linux发行版信息
                    if os.path.exists('/etc/os-release'):
                        with open('/etc/os-release') as f:
                            os_info = {}
                            for line in f:
                                if '=' in line:
                                    key, value = line.rstrip().split('=', 1)
                                    os_info[key] = value.strip('"')
                        system_info['os_info'] = os_info

                    # 获取内核信息
                    with open('/proc/version') as f:
                        system_info['kernel_version'] = f.read().strip()

                except Exception as e:
                    logger.debug(f"无法读取系统详细信息: {e}")

            return system_info

        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {}

    def get_process_info(self, pid: Optional[int] = None) -> Dict[str, Any]:
        """获取进程信息（跨平台）"""
        try:
            if pid:
                process = psutil.Process(pid)
                process_info = {
                    'pid': process.pid,
                    'name': process.name(),
                    'status': process.status(),
                    'cpu_percent': process.cpu_percent(),
                    'memory_percent': process.memory_percent(),
                    'create_time': datetime.fromtimestamp(process.create_time()).strftime("%Y-%m-%d %H:%M:%S"),
                    'username': process.username(),
                    'cmdline': process.cmdline()
                }

                # Windows特定信息
                if self.os_type == 'windows':
                    try:
                        import wmi
                        w = wmi.WMI()
                        for p in w.Win32_Process(ProcessId=pid):
                            process_info.update({
                                'priority': p.Priority,
                                'thread_count': p.ThreadCount,
                                'handle_count': p.HandleCount
                            })
                    except ImportError:
                        logger.debug("WMI模块未安装，无法获取详细进程信息")
                    except Exception as e:
                        logger.debug(f"获取Windows进程详细信息失败: {e}")

                return process_info
            else:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'status']):
                    processes.append(proc.info)
                return {'processes': processes}

        except Exception as e:
            logger.error(f"获取进程信息失败: {e}")
            return {}

    def get_all_info(self) -> Dict[str, Any]:
        """获取所有系统信息（跨平台）"""
        return {
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'os_type': self.os_type,
            'os_bit': self.os_bit
        }

    def monitor_resources(self, interval: int = 1) -> Dict[str, Any]:
        """监控系统资源（跨平台）"""
        try:
            resources = {
                'cpu_percent': psutil.cpu_percent(interval=interval),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': {},
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # 获取磁盘使用率
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    resources['disk_usage'][partition.device] = usage.percent
                except Exception:
                    continue

            # Windows特定监控
            if self.os_type == 'windows':
                try:
                    import wmi
                    w = wmi.WMI()
                    resources['windows_specific'] = {
                        'processor_queue_length': len(w.Win32_PerfRawData_PerfOS_Processor()),
                        'system_up_time': w.Win32_PerfRawData_PerfOS_System()[0].SystemUpTime
                    }
                except ImportError:
                    logger.debug("WMI模块未安装，无法获取Windows特定监控信息")
                except Exception as e:
                    logger.debug(f"获取Windows监控详细信息失败: {e}")

            # Linux特定监控
            elif self.os_type == 'linux':
                try:
                    with open('/proc/loadavg') as f:
                        load = f.read().split()
                        resources['linux_specific'] = {
                            'load_avg_1min': float(load[0]),
                            'load_avg_5min': float(load[1]),
                            'load_avg_15min': float(load[2])
                        }
                except Exception as e:
                    logger.debug(f"无法读取Linux负载信息: {e}")

            return resources

        except Exception as e:
            logger.error(f"监控系统资源失败: {e}")
            return {}

    def save_info_to_file(self, filename: str = 'system_info.json') -> None:
        """将系统信息保存到文件"""
        try:
            info = self.get_all_info()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=4, ensure_ascii=False)
            logger.info(f"系统信息已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存系统信息失败: {e}")
