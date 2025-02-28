import win32api
import win32file
import struct
import ctypes
from ctypes import wintypes

# 定义需要的常量
IOCTL_STORAGE_QUERY_PROPERTY = 0x2D1400
IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS = 0x00560000
StorageDeviceProperty = 0
PropertyStandardQuery = 0


# 定义存储属性查询结构
class STORAGE_PROPERTY_QUERY(ctypes.Structure):
    _fields_ = [
        ('PropertyId', wintypes.DWORD),
        ('QueryType', wintypes.DWORD),
        ('AdditionalParameters', ctypes.c_byte * 1)
    ]


def get_drive_info(drive_letter):
    drive_path = f"{drive_letter}:\\"
    volume_name = f"\\\\.\\{drive_letter}:"

    # 获取卷信息
    volume_info = win32api.GetVolumeInformation(drive_path)
    volume_serial_number = volume_info[1]

    # 打开卷
    hVolume = win32file.CreateFile(
        volume_name,
        win32file.GENERIC_READ,
        win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
        None,
        win32file.OPEN_EXISTING,
        0,
        None
    )

    # 获取磁盘编号
    disk_extents = win32file.DeviceIoControl(
        hVolume,
        IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS,
        None,
        4096
    )
    disk_number = struct.unpack('I', disk_extents[8:12])[0]

    # 获取物理磁盘信息
    physical_drive_path = f"\\\\.\\PhysicalDrive{disk_number}"
    hPhysicalDrive = win32file.CreateFile(
        physical_drive_path,
        win32file.GENERIC_READ,
        win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
        None,
        win32file.OPEN_EXISTING,
        0,
        None
    )

    # 创建并填充STORAGE_PROPERTY_QUERY结构
    query = STORAGE_PROPERTY_QUERY()
    query.PropertyId = StorageDeviceProperty
    query.QueryType = PropertyStandardQuery

    # 获取存储设备描述符
    buffer_size = 512
    buffer = ctypes.create_string_buffer(buffer_size)
    bytes_returned = wintypes.DWORD()

    ctypes.windll.kernel32.DeviceIoControl(
        hPhysicalDrive.handle,
        IOCTL_STORAGE_QUERY_PROPERTY,
        ctypes.byref(query),
        ctypes.sizeof(query),
        buffer,
        buffer_size,
        ctypes.byref(bytes_returned),
        None
    )

    raw_bytes=buffer.raw
    # 解析设备描述符
    bus_type = buffer[12]
    vendor_id = ctypes.string_at(buffer[16:24]).decode('ascii').rstrip('\x00')
    product_id = ctypes.string_at(buffer[24:32]).decode('ascii').rstrip('\x00')

    # 关闭句柄
    win32file.CloseHandle(hPhysicalDrive)
    win32file.CloseHandle(hVolume)

    return {
        'DriveLetter': drive_letter,
        'VolumeId': volume_serial_number,
        'DiskNumber': disk_number,
        'BusType': bus_type,
        'Model': f"{vendor_id.strip()} {product_id.strip()}".strip()
    }


# 使用示例
drive_letter = 'C'  # 可以根据需要更改驱动器字母
drive_info = get_drive_info(drive_letter)
print(f"Drive Letter: {drive_info['DriveLetter']}")
print(f"Volume ID: {drive_info['VolumeId']}")
print(f"Disk Number: {drive_info['DiskNumber']}")
print(f"Bus Type: {drive_info['BusType']}")
print(f"Model: {drive_info['Model']}")
