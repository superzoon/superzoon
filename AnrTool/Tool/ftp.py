import paramiko

transport =paramiko.Transport(('192.168.43.140',22))
transport.connect(username='pi',password='raspberrypi')
sftp = paramiko.SFTPClient.from_transport(transport)
sftp.put('text1', '/home/pi/python_code/python_ssh/socketsever.py')
# sftp.get('remove_path', 'local_path')
transport.close()

'''
SFTPCLient��Ϊһ��sftp�Ŀͻ��˶��󣬸���ssh����Э���sftp�Ự��ʵ��Զ���ļ����������ϴ������ء�Ȩ�ޡ�״̬ 
from_transport(cls,t) ����һ������ͨ��SFTP�ͻ���ͨ��
put(localpath, remotepath, callback=None, confirm=True) �������ļ��ϴ��������� ����confirm���Ƿ����stat()��������ļ�״̬������ls -l�Ľ��
get(remotepath, localpath, callback=None) �ӷ����������ļ�������
mkdir() �ڷ������ϴ���Ŀ¼
remove() �ڷ�������ɾ��Ŀ¼
rename() �ڷ�������������Ŀ¼
stat() �鿴�������ļ�״̬
listdir() �г�������Ŀ¼�µ��ļ�
'''