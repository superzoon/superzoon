
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
    # ����һ��ͨ��
    transport = paramiko.Transport(('hostname', 22))
    transport.connect(username='root', password='123')

    ssh = paramiko.SSHClient()
    ssh._transport = transport

    stdin, stdout, stderr = ssh.exec_command('df -h')
    print(stdout.read().decode('utf-8'))

    ssh = ssh.invoke_shell()
    ssh.send('cd CTS/android-cts-10_r2-linux_x86-arm/android-cts/tools ; ls')
    buff = ssh.recv(999)
    print(buff)

    transport.close()
def test2():
    # ����˽����Կ�ļ�λ��
    private = paramiko.RSAKey.from_private_key_file('/Users/ch/.ssh/id_rsa')
    # ʵ����SSHClient
    client = paramiko.SSHClient()
    # �Զ���Ӳ��ԣ����������������������Կ��Ϣ���������ӣ���ô���ٱ���know_hosts�ļ��м�¼���������޷�����
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ����SSH����ˣ����û��������������֤
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
connect()��ʵ��Զ�̷���������������֤�����ڸ÷���ֻ��hostname�Ǳش�������

���ò���
hostname ���ӵ�Ŀ������
port=SSH_PORT ָ���˿�
username=None ��֤���û���
password=None ��֤���û�����
pkey=None ˽Կ��ʽ���������֤
key_filename=None һ���ļ������ļ��б�ָ��˽Կ�ļ�
timeout=None ��ѡ��tcp���ӳ�ʱʱ��
allow_agent=True, �Ƿ��������ӵ�ssh����Ĭ��ΪTrue ����
look_for_keys=True �Ƿ���~/.ssh������˽Կ�ļ���Ĭ��ΪTrue ����
compress=False, �Ƿ��ѹ��
����

set_missing_host_key_policy()������Զ�̷�����û����know_hosts�ļ��м�¼ʱ��Ӧ�Բ��ԡ�Ŀǰ֧�����ֲ��ԣ�

�������ӵ�Զ������û�б���������Կ��HostKeys����ʱ�Ĳ��ԣ�Ŀǰ֧�����֣�
 
AutoAddPolicy �Զ������������������Կ������HostKeys���󣬲�����load_system_host_key�����á����½���ssh����ʱ����Ҫ������yes��no����ȷ��
WarningPolicy ���ڼ�¼һ��δ֪��������Կ��python���档�����ܣ������Ϻ�AutoAddPolicy���ƣ����ǻ���ʾ��������
RejectPolicy �Զ��ܾ�δ֪������������Կ������load_system_host_key�����á���ΪĬ��ѡ��
exec_command()����Զ�̷�����ִ��Linux����ķ�����

open_sftp()���ڵ�ǰssh�Ự�Ļ����ϴ���һ��sftp�Ự���÷����᷵��һ��SFTPClient����

# ����SSHClient�����open_sftp()����������ֱ�ӷ���һ�����ڵ�ǰ���ӵ�sftp���󣬿��Խ����ļ����ϴ��Ȳ���.
 
sftp = client.open_sftp()
sftp.put('test.txt','text.txt')
'''