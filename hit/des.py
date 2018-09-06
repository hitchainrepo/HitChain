# -- coding: utf-8 --
import binascii
from pyDes import des, CBC, PAD_PKCS5


def keyGen():
    import random
    import string
    salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    return salt

class DESCipher:
    def __init__(self, key):
        self.secret_key = key

    def des_encrypt(self,s):
        """
        DES 加密
        :param s: 原始字符串
        :return: 加密后字符串，16进制
        """
        iv = self.secret_key
        k = des(self.secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        en = k.encrypt(s, padmode=PAD_PKCS5)
        return binascii.b2a_hex(en)


    def des_descrypt(self,s):
        """
        DES 解密
        :param s: 加密后的字符串，16进制
        :return:  解密后的字符串
        """
        iv = self.secret_key
        k = des(self.secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
        return de

