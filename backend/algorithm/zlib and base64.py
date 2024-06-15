#zlib 压缩实现
def zlib_compress(data):
    # 定义常量
    WINDOW_SIZE = 32768  # 32KB 的窗口大小
    MIN_MATCH_LENGTH = 3  # 最小匹配长度
    MAX_MATCH_LENGTH = 258  # 最大匹配长度
    
    compressed_data = []
    i = 0
    while i < len(data):
        match_length = 0
        match_distance = 0
        # 搜索最长匹配
        for j in range(max(0, i - WINDOW_SIZE), i):
            length = 0
            while length < MAX_MATCH_LENGTH and i + length < len(data) and data[j + length] == data[i + length]:
                length += 1
            if length > match_length:
                match_length = length
                match_distance = i - j
        if match_length >= MIN_MATCH_LENGTH:
            # 匹配成功,记录 (距离, 长度)
            compressed_data.append((match_distance, match_length))
            i += match_length
        else:
            # 无匹配,记录字面值
            compressed_data.append(data[i])
            i += 1
    return compressed_data

def zlib_decompress(compressed_data):
    decompressed_data = []
    i = 0
    while i < len(compressed_data):
        if isinstance(compressed_data[i], tuple):
            distance, length = compressed_data[i]
            start = len(decompressed_data) - distance
            for j in range(length):
                decompressed_data.append(decompressed_data[start + j])
            i += 1
        else:
            decompressed_data.append(compressed_data[i])
            i += 1
    return ''.join(decompressed_data)


#base64 编码算法
def base64_encode(data):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    encoded_data = []
    padding = 0

    if len(data) % 3 != 0:
        padding = 3 - (len(data) % 3)
        data += '\0' * padding

    for i in range(0, len(data), 3):
        b = (ord(data[i]) << 16) + (ord(data[i+1]) << 8) + ord(data[i+2])
        encoded_data.append(base64_chars[(b >> 18) & 63])
        encoded_data.append(base64_chars[(b >> 12) & 63])
        encoded_data.append(base64_chars[(b >> 6) & 63])
        encoded_data.append(base64_chars[b & 63])

    for i in range(padding):
        encoded_data[-(i + 1)] = '='

    return ''.join(encoded_data)

def base64_decode(data):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    decoded_data = bytearray()
    data = data.rstrip('=')
    
    for i in range(0, len(data), 4):
        b = (base64_chars.index(data[i]) << 18) + (base64_chars.index(data[i+1]) << 12) + \
            (base64_chars.index(data[i+2]) << 6) + base64_chars.index(data[i+3])
        decoded_data.append((b >> 16) & 255)
        decoded_data.append((b >> 8) & 255)
        decoded_data.append(b & 255)
    
    return decoded_data.decode('utf-8')

'''
           压缩算法(zlib_compress)
zlib 压缩算法主要使用 LZ77 算法进行数据压缩。以下是压缩算法的详细步骤和原理:

定义常量:

WINDOW_SIZE:滑动窗口的大小,设置为 32768 字节(32KB)。
MIN_MATCH_LENGTH:最小匹配长度,设置为 3。
MAX_MATCH_LENGTH:最大匹配长度,设置为 258。
初始化变量:

compressed_data:用于存储压缩后的数据。
i:当前数据索引,初始为 0。
遍历输入数据:

初始化 match_length 和 match_distance 为 0。
在窗口内搜索最长匹配:
遍历窗口内的数据,检查与当前数据的匹配长度。
更新 match_length 和 match_distance,记录最长匹配的距离和长度。
记录匹配结果:

如果找到的匹配长度大于或等于 MIN_MATCH_LENGTH,则记录匹配距离和长度,并将索引 i 移动匹配长度。
如果没有找到足够长的匹配,则记录当前字节的字面值,并将索引 i 增加 1。
返回压缩数据:返回 compressed_data,包含字面值和匹配的距离和长度。

         解压缩算法(zlib_decompress)
解压缩算法主要通过识别压缩数据中的字面值和匹配信息,重构原始数据。以下是解压缩算法的详细步骤和原理:

初始化变量:

decompressed_data:用于存储解压后的数据。
i:当前数据索引,初始为 0。
遍历压缩数据:

如果当前元素是元组(表示匹配信息),则获取匹配的距离和长度,从解压后的数据中复制相应的子串,并添加到 decompressed_data。
如果当前元素不是元组(表示字面值),则直接将字面值添加到 decompressed_data。
返回解压数据:将 decompressed_data 转换为字符串并返回。

                Base64 编码算法(base64_encode)
Base64 编码是一种将二进制数据转换为 ASCII 字符串的算法。以下是 Base64 编码的详细步骤和原理:

定义常量:

base64_chars:Base64 字符集。
处理输入数据:

如果输入数据的长度不是 3 的倍数,则补齐 \0 字节。
遍历输入数据:

将每 3 个字节组合成 24 位的二进制数据。
将 24 位数据分成 4 个 6 位的二进制数据,分别转换为 Base64 字符。
将编码结果添加到 encoded_data 列表中。
处理填充字符:

根据补齐的字节数,在编码结果的末尾添加 = 字符。
返回编码结果:将 encoded_data 转换为字符串并返回。

                Base64 解码算法(base64_decode)
Base64 解码是将 Base64 编码的 ASCII 字符串转换回二进制数据。以下是 Base64 解码的详细步骤和原理:

定义常量:

base64_chars:Base64 字符集。
处理输入数据:

去除末尾的 = 填充字符。
遍历输入数据:

将每 4 个 Base64 字符组合成 24 位的二进制数据。
将 24 位数据分成 3 个 8 位的二进制数据,分别转换为原始字节。
返回解码结果:将解码结果转换为字符串并返回。
'''