# -- coding: utf-8 --
from Crypto.Cipher import AES
from Crypto import Random

# AES根据16位对齐
BS = 16

# 转成utf8编码
def unicode_to_utf8(s):
    if isinstance(s, unicode):
        s = s.encode("utf-8")
    return s


# 补充字符,最少1个
def pad(s):
    length = len(s)
    add = BS - length % BS
    byte = chr(BS - length % BS)
    return s + (add * byte)


# 去除补充字符
def unpad(s):
    length = len(s)
    byte = s[length - 1:]
    add = ord(byte)
    return s[:-add]

def keyGen():
    return Random.new().read(AES.block_size)


# class
class AESCipher:
    # 初始化
    def __init__(self, key):
        self.key = key

    # 加密
    def encrypt(self, raw):
        raw = unicode_to_utf8(raw)
        raw = pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.key)
        return cipher.encrypt(raw)

    # 解密
    def decrypt(self, enc):
        cipher = AES.new(self.key, AES.MODE_CBC, self.key)
        return unpad(cipher.decrypt(enc))


if __name__ == '__main__':
    # 注意key是16字节长
    key = "f2c85e0140a47415"

    # 初始化
    aes = AESCipher(Random.new().read(AES.block_size))
    print Random.new().read(AES.block_size)
    print AES.block_size

    s1 = "hello world"
    s2 = "带鱼拯救世界"
    s3 = "~!@#$%^&"
    s4 = u"~！@#￥%……&带鱼拯救world"

    en1 = aes.encrypt(s1)
    de1 = aes.decrypt(en1)

    en2 = aes.encrypt(s2)
    de2 = aes.decrypt(en2)

    en3 = aes.encrypt(s3)
    de3 = aes.decrypt(en3)

    en4 = aes.encrypt(s4)
    de4 = aes.decrypt(en4)

    print 's1:', de1
    print 's2:', de2
    print 's3:', de3
    print 's4:', de4
