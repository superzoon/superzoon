import paramiko

transport =paramiko.Transport(('192.168.43.140',22))
transport.connect(username='pi',password='raspberrypi')
sftp = paramiko.SFTPClient.from_transport(transport)
sftp.put('text1', '/home/pi/python_code/python_ssh/socketsever.py')
# sftp.get('remove_path', 'local_path')
transport.close()

'''
SFTPCLient作为一个sftp的客户端对象，根据ssh传输协议的sftp会话，实现远程文件操作，如上传、下载、权限、状态 
from_transport(cls,t) 创建一个已连通的SFTP客户端通道
put(localpath, remotepath, callback=None, confirm=True) 将本地文件上传到服务器 参数confirm：是否调用stat()方法检查文件状态，返回ls -l的结果
get(remotepath, localpath, callback=None) 从服务器下载文件到本地
mkdir() 在服务器上创建目录
remove() 在服务器上删除目录
rename() 在服务器上重命名目录
stat() 查看服务器文件状态
listdir() 列出服务器目录下的文件
'''