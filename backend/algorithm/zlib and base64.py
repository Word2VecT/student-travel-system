#zlib ѹ��ʵ��
def zlib_compress(data):
    # ���峣��
    WINDOW_SIZE = 32768  # 32KB �Ĵ��ڴ�С
    MIN_MATCH_LENGTH = 3  # ��Сƥ�䳤��
    MAX_MATCH_LENGTH = 258  # ���ƥ�䳤��
    
    compressed_data = []
    i = 0
    while i < len(data):
        match_length = 0
        match_distance = 0
        # �����ƥ��
        for j in range(max(0, i - WINDOW_SIZE), i):
            length = 0
            while length < MAX_MATCH_LENGTH and i + length < len(data) and data[j + length] == data[i + length]:
                length += 1
            if length > match_length:
                match_length = length
                match_distance = i - j
        if match_length >= MIN_MATCH_LENGTH:
            # ƥ��ɹ�,��¼ (����, ����)
            compressed_data.append((match_distance, match_length))
            i += match_length
        else:
            # ��ƥ��,��¼����ֵ
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


#base64 �����㷨
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
           ѹ���㷨(zlib_compress)
zlib ѹ���㷨��Ҫʹ�� LZ77 �㷨��������ѹ����������ѹ���㷨����ϸ�����ԭ��:

���峣��:

WINDOW_SIZE:�������ڵĴ�С,����Ϊ 32768 �ֽ�(32KB)��
MIN_MATCH_LENGTH:��Сƥ�䳤��,����Ϊ 3��
MAX_MATCH_LENGTH:���ƥ�䳤��,����Ϊ 258��
��ʼ������:

compressed_data:���ڴ洢ѹ��������ݡ�
i:��ǰ��������,��ʼΪ 0��
������������:

��ʼ�� match_length �� match_distance Ϊ 0��
�ڴ����������ƥ��:
���������ڵ�����,����뵱ǰ���ݵ�ƥ�䳤�ȡ�
���� match_length �� match_distance,��¼�ƥ��ľ���ͳ��ȡ�
��¼ƥ����:

����ҵ���ƥ�䳤�ȴ��ڻ���� MIN_MATCH_LENGTH,���¼ƥ�����ͳ���,�������� i �ƶ�ƥ�䳤�ȡ�
���û���ҵ��㹻����ƥ��,���¼��ǰ�ֽڵ�����ֵ,�������� i ���� 1��
����ѹ������:���� compressed_data,��������ֵ��ƥ��ľ���ͳ��ȡ�

         ��ѹ���㷨(zlib_decompress)
��ѹ���㷨��Ҫͨ��ʶ��ѹ�������е�����ֵ��ƥ����Ϣ,�ع�ԭʼ���ݡ������ǽ�ѹ���㷨����ϸ�����ԭ��:

��ʼ������:

decompressed_data:���ڴ洢��ѹ������ݡ�
i:��ǰ��������,��ʼΪ 0��
����ѹ������:

�����ǰԪ����Ԫ��(��ʾƥ����Ϣ),���ȡƥ��ľ���ͳ���,�ӽ�ѹ��������и�����Ӧ���Ӵ�,����ӵ� decompressed_data��
�����ǰԪ�ز���Ԫ��(��ʾ����ֵ),��ֱ�ӽ�����ֵ��ӵ� decompressed_data��
���ؽ�ѹ����:�� decompressed_data ת��Ϊ�ַ��������ء�

                Base64 �����㷨(base64_encode)
Base64 ������һ�ֽ�����������ת��Ϊ ASCII �ַ������㷨�������� Base64 �������ϸ�����ԭ��:

���峣��:

base64_chars:Base64 �ַ�����
������������:

����������ݵĳ��Ȳ��� 3 �ı���,���� \0 �ֽڡ�
������������:

��ÿ 3 ���ֽ���ϳ� 24 λ�Ķ��������ݡ�
�� 24 λ���ݷֳ� 4 �� 6 λ�Ķ���������,�ֱ�ת��Ϊ Base64 �ַ���
����������ӵ� encoded_data �б��С�
��������ַ�:

���ݲ�����ֽ���,�ڱ�������ĩβ��� = �ַ���
���ر�����:�� encoded_data ת��Ϊ�ַ��������ء�

                Base64 �����㷨(base64_decode)
Base64 �����ǽ� Base64 ����� ASCII �ַ���ת���ض��������ݡ������� Base64 �������ϸ�����ԭ��:

���峣��:

base64_chars:Base64 �ַ�����
������������:

ȥ��ĩβ�� = ����ַ���
������������:

��ÿ 4 �� Base64 �ַ���ϳ� 24 λ�Ķ��������ݡ�
�� 24 λ���ݷֳ� 3 �� 8 λ�Ķ���������,�ֱ�ת��Ϊԭʼ�ֽڡ�
���ؽ�����:��������ת��Ϊ�ַ��������ء�
'''