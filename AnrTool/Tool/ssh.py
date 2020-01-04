
import paramiko


def sshclient_execmd(hostname, port, username, password, execmd):
    # paramiko.util.log_to_file("paramiko.log")
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(hostname=hostname, port=port, username=username, password=password)
    stdin, stdout, stderr = s.exec_command(execmd)
    stdin.write("Y")  # Generally speaking, the first connection, need a simple interaction.
    print
    stdout.read()
    s.close()

def test1():
    # 创建一个通道
    transport = paramiko.Transport(('hostname', 22))
    transport.connect(username='root', password='123')

    ssh = paramiko.SSHClient()
    ssh._transport = transport

    stdin, stdout, stderr = ssh.exec_command('df -h')
    print(stdout.read().decode('utf-8'))

    transport.close()
def test2():
    # 配置私人密钥文件位置
    private = paramiko.RSAKey.from_private_key_file('/Users/ch/.ssh/id_rsa')
    # 实例化SSHClient
    client = paramiko.SSHClient()
    # 自动添加策略，保存服务器的主机名和密钥信息，如果不添加，那么不再本地know_hosts文件中记录的主机将无法连接
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接SSH服务端，以用户名和密码进行认证
    client.connect(hostname='10.0.0.1', port=22, username='root', pkey=private)

def main():
    hostname = '10.***.***.**'
    port = 22
    username = 'root'
    password = '******'
    execmd = "free"

    sshclient_execmd(hostname, port, username, password, execmd)


if __name__ == "__main__":
    main()
'''
connect()：实现远程服务器的连接与认证，对于该方法只有hostname是必传参数。

常用参数
hostname 连接的目标主机
port=SSH_PORT 指定端口
username=None 验证的用户名
password=None 验证的用户密码
pkey=None 私钥方式用于身份验证
key_filename=None 一个文件名或文件列表，指定私钥文件
timeout=None 可选的tcp连接超时时间
allow_agent=True, 是否允许连接到ssh代理，默认为True 允许
look_for_keys=True 是否在~/.ssh中搜索私钥文件，默认为True 允许
compress=False, 是否打开压缩
　　

set_missing_host_key_policy()：设置远程服务器没有在know_hosts文件中记录时的应对策略。目前支持三种策略：

设置连接的远程主机没有本地主机密钥或HostKeys对象时的策略，目前支持三种：
 
AutoAddPolicy 自动添加主机名及主机密钥到本地HostKeys对象，不依赖load_system_host_key的配置。即新建立ssh连接时不需要再输入yes或no进行确认
WarningPolicy 用于记录一个未知的主机密钥的python警告。并接受，功能上和AutoAddPolicy类似，但是会提示是新连接
RejectPolicy 自动拒绝未知的主机名和密钥，依赖load_system_host_key的配置。此为默认选项
exec_command()：在远程服务器执行Linux命令的方法。

open_sftp()：在当前ssh会话的基础上创建一个sftp会话。该方法会返回一个SFTPClient对象。

# 利用SSHClient对象的open_sftp()方法，可以直接返回一个基于当前连接的sftp对象，可以进行文件的上传等操作.
 
sftp = client.open_sftp()
sftp.put('test.txt','text.txt')
'''