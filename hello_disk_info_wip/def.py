import win32file
import ctypes
from ctypes import wintypes

# 定义需要的常量
IOCTL_STORAGE_QUERY_PROPERTY = 0x2D1400
StorageDeviceProperty = 0


# 定义结构体
class STORAGE_PROPERTY_QUERY(ctypes.Structure):
    _fields_ = [
        ('PropertyId', wintypes.DWORD),
        ('QueryType', wintypes.DWORD),
        ('AdditionalParameters', ctypes.c_byte * 1)
    ]


class STORAGE_DEVICE_DESCRIPTOR(ctypes.Structure):
    _fields_ = [
        ('Version', wintypes.DWORD),
        ('Size', wintypes.DWORD),
        ('DeviceType', ctypes.c_byte),
        ('DeviceTypeModifier', ctypes.c_byte),
        ('RemovableMedia', wintypes.BOOLEAN),
        ('CommandQueueing', wintypes.BOOLEAN),
        ('VendorIdOffset', wintypes.DWORD),
        ('ProductIdOffset', wintypes.DWORD),
        ('ProductRevisionOffset', wintypes.DWORD),
        ('SerialNumberOffset', wintypes.DWORD),
        ('BusType', wintypes.DWORD),
        ('RawPropertiesLength', wintypes.DWORD),
        ('RawDeviceProperties', ctypes.c_byte * 1)
    ]


def get_drive_info(drive_letter):
    drive_path = f"\\\\.\\{drive_letter}:"

    # 打开驱动器
    handle = win32file.CreateFile(
        drive_path,
        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
        win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
        None,
        win32file.OPEN_EXISTING,
        0,
        None
    )

    # 获取原始句柄值
    handle_value = ctypes.c_void_p(int(handle)).value

    # 准备查询
    query = STORAGE_PROPERTY_QUERY()
    query.PropertyId = StorageDeviceProperty
    query.QueryType = 0  # PropertyStandardQuery

    # 定义输出参数
    bytes_returned = wintypes.DWORD()
    descriptor_size = wintypes.DWORD()

    # 首先获取需要的缓冲区大小
    ctypes.windll.kernel32.DeviceIoControl(
        handle_value,
        IOCTL_STORAGE_QUERY_PROPERTY,
        ctypes.byref(query),
        ctypes.sizeof(query),
        ctypes.byref(descriptor_size),
        ctypes.sizeof(descriptor_size),
        ctypes.byref(bytes_returned),
        None
    )

    # 分配缓冲区并获取设备描述符
    buffer = ctypes.create_string_buffer(descriptor_size.value)
    ctypes.windll.kernel32.DeviceIoControl(
        handle_value,
        IOCTL_STORAGE_QUERY_PROPERTY,
        ctypes.byref(query),
        ctypes.sizeof(query),
        buffer,
        descriptor_size,
        ctypes.byref(bytes_returned),
        None
    )

    # 将缓冲区转换为 STORAGE_DEVICE_DESCRIPTOR 结构
    descriptor = STORAGE_DEVICE_DESCRIPTOR.from_buffer(buffer)

    # 获取字符串信息
    def get_string(offset):
        if offset:
            return ctypes.string_at(buffer[offset:]).decode('ascii').rstrip('\x00')
        return ''

    info = {
        'VendorId': get_string(descriptor.VendorIdOffset),
        'ProductId': get_string(descriptor.ProductIdOffset),
        'ProductRevision': get_string(descriptor.ProductRevisionOffset),
        'SerialNumber': get_string(descriptor.SerialNumberOffset),
        'BusType': descriptor.BusType
    }

    win32file.CloseHandle(handle)
    return info


# 使用示例
drive_letter = 'C'
info = get_drive_info(drive_letter)
for key, value in info.items():
    print(f"{key}: {value}")