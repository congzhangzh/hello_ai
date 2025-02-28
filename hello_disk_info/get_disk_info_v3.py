import win32api

# 查询逻辑驱动器的卷信息
drive_letter = 'C:'
volume_info = win32api.GetVolumeInformation(drive_letter + '\\')

print(f"Volume Label: {volume_info[0]}")
print(f"File System: {volume_info[4]}")
print(f"Serial Number: {volume_info[1]}")