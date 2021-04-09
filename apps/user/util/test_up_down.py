# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_file
from qiniu import Zone, set_default
import random
from qiniu import Auth, put_data, BucketManager

# 指定固定域名的zone,不同区域uphost域名见下文档
# https://developer.qiniu.com/kodo/manual/1671/region-endpoint
# 未指定或上传错误，sdk会根据token自动查询对应的上传域名
zone = Zone(
    up_host='http://up-z2.qiniup.com',
    up_host_backup='http://upload-z2.qiniup.com',
    io_host='http://iovip-z2.qbox.me',
    scheme='http')
set_default(default_zone=zone)

def upload_qiniu(filestorage):
    # 需要填写 Access Key 和 Secret Key
    # https://portal.qiniu.com/user/key
    access_key = 'r5pmxxVGpZPYqKjOvuYRo2gWWF0ejLq5O3i66e9A'
    secret_key = 'Gl8VuDSdRS0yop2l7xVEAk8uv7PIw-eQQ1_r4lm4'

    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'myareazxy'
    # 上传后保存的文件名
    filename = filestorage.filename
    # print(filename)
    ran = random.randint(1, 1000)
    suffix = filename.rsplit('.')[-1]
    key = filename.rsplit('.')[0] + '_' + str(ran) + '.' + suffix
    # print(key)
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_data(token, key, filestorage.read())
    return ret, info

def delete_qiniu(filename):
    # 需要填写你的 Access Key 和 Secret Key
    access_key = 'r5pmxxVGpZPYqKjOvuYRo2gWWF0ejLq5O3i66e9A'
    secret_key = 'Gl8VuDSdRS0yop2l7xVEAk8uv7PIw-eQQ1_r4lm4'
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'myareazxy'
    # 初始化BucketManager
    bucket = BucketManager(q)
    # key就是要删除的文件的名字
    key = filename
    ret, info = bucket.delete(bucket_name, key)
    return info
