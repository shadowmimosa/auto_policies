import json
import time
from loguru import logger
from urllib.request import urlopen
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.vpc.v20170312 import vpc_client, models

from config import secret_id, secret_key, group_id

LOCAL_IP = '0.0.0.0'

# logger.remove()
logger.add('info.log', format='{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}', encoding='utf-8')


def get_local_ip():
    return urlopen('http://ip.42.pl/short').read().decode('utf-8')


class TencentServer():
    def __init__(self,
                 group_id,
                 region='ap-beijing',
                 endpoint='vpc.tencentcloudapi.com') -> None:
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = endpoint
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self.client = vpc_client.VpcClient(cred, region, clientProfile)
        self.group_id = group_id

    def query(self):
        req = models.DescribeSecurityGroupPoliciesRequest()
        params = {'SecurityGroupId': self.group_id}
        req.from_json_string(json.dumps(params))
        resp = self.client.DescribeSecurityGroupPolicies(req)

        return resp.to_json_string()

    def update(self):
        local_ip = get_local_ip()
        req = models.ModifySecurityGroupPoliciesRequest()
        params = {
            'SecurityGroupPolicySet': {
                'Ingress': [{
                    'CidrBlock': local_ip,
                    'Action': 'ACCEPT'
                }]
            },
            'SecurityGroupId': self.group_id
        }
        req.from_json_string(json.dumps(params))
        resp = self.client.ModifySecurityGroupPolicies(req)
        logger.info(resp.to_json_string())


def polling():
    global LOCAL_IP

    while True:
        current_ip = get_local_ip()
        if current_ip == LOCAL_IP:
            time.sleep(60)
            continue

        logger.info('IP 改变，修改安全组')
        TencentServer(group_id).update()
        logger.info('安全组修改成功')

        LOCAL_IP = get_local_ip()


if __name__ == "__main__":
    polling()
