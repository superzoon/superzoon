from smb.SMBConnection import *
import os

class SMBClient(object):
    '''
    smb���ӿͻ���
    '''
    user_name = ''
    passwd = ''
    ip = ''
    prot = None

    status = False
    samba = None

    def __init__(self, user_name, passwd, ip, port=139):
        self.user_name = user_name
        self.passwd = passwd
        self.ip = ip
        self.port = port

    def connect(self):
        try:
            self.samba = SMBConnection(self.user_name, self.passwd, '', '', use_ntlm_v2=True)
            self.samba.connect(self.ip, self.port)
            self.status = self.samba.auth_result
        except:
            self.samba.close()

    def disconnect(self):
        if self.status:
            self.samba.close()

    def all_file_names_in_dir(self, service_name, dir_name):
        '''
        �г��ļ����������ļ���
        :param service_name:
        :param dir_name:
        :return:
        '''
        f_names = list()
        for e in self.samba.listPath(service_name, dir_name):
            # if len(e.filename) > 3: ���᷵��һЩ.���ļ�����Ҫ���ˣ�
            if e.filename[0] != '.':
                f_names.append(e.filename)
        return f_names


    def download(self, f_names, service_name, smb_dir, local_dir):
        '''
        �����ļ�
        :param f_names:�ļ���
        :param service_name:��������smb�е��ļ�������
        :param smb_dir: smb�ļ���
        :param local_dir: �����ļ���
        :return:
        '''
        assert isinstance(f_names, list)
        for f_name in f_names:
            f = open(os.path.join(local_dir, f_name), 'w')
            self.samba.retrieveFile(service_name, os.path.join(smb_dir, f_name), f)
            f.close()

    def upload(self, service_name, smb_dir, file_name):
        '''
        �ϴ��ļ�
        :param f_names:�ļ���
        :param service_name:��������smb�е��ļ�������
        :param smb_dir: smb�ļ���
        :param local_dir: �����ļ���
        :return:
        '''
        self.samba.storeFile(service_name, smb_dir, file_name)

    def createDir(self, service_name, path):
        """
        �����ļ���
        :param service_name:
        :param path:
        :return:
        """
        try:
            self.samba.createDirectory(service_name, path)
        except OperationFailure:
            pass