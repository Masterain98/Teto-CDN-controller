import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cdn.v20180606 import cdn_client, models

from log_printer import class_log_printer


class QCloudAccount:
    def __init__(self, SecretId, SecretKey):
        self.SecretId = SecretId
        self.SecretKey = SecretKey
        self.cred = credential.Credential(self.SecretId, self.SecretKey)

    @class_log_printer
    def describe_traffic_packages(self):
        try:
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cdn.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = cdn_client.CdnClient(self.cred, "", clientProfile)

            req = models.DescribeTrafficPackagesRequest()
            params = {

            }
            req.from_json_string(json.dumps(params))

            resp = client.DescribeTrafficPackages(req)
            return json.loads(str(resp))
        except TencentCloudSDKException as err:
            print(err)
            return None

    @class_log_printer
    def list_enabled_traffic_packages(self):
        return_list = []
        all_packages = self.describe_traffic_packages()
        for package in all_packages["TrafficPackages"]:
            if package["Status"] == "enabled":
               return_list.append(package)
        return return_list

    @class_log_printer
    def get_remaining_traffic(self):
        bytes_total = 0
        bytes_used = 0
        bytes_remaining = 0
        available_packages = self.list_enabled_traffic_packages()
        for package in available_packages:
            bytes_total += package["Bytes"]
            bytes_used += package["BytesUsed"]
        bytes_remaining = bytes_total - bytes_used
        bytes_remaining_percentage = round(bytes_remaining / bytes_total, 4) * 100
        return {"bytes_total": bytes_total, "bytes_used": bytes_used, "bytes_remaining": bytes_remaining,
                "bytes_remaining_percentage": bytes_remaining_percentage}

    @class_log_printer
    def get_remaining_traffic_percentage(self):
        return self.get_remaining_traffic()["bytes_remaining_percentage"]

    @class_log_printer
    def create_refresh_directory_task(self, task_list: list):
        try:
            # 实例化一个http选项，可选的，没有特殊需求可以跳过
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cdn.tencentcloudapi.com"

            # 实例化一个client选项，可选的，没有特殊需求可以跳过
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 实例化要请求产品的client对象,clientProfile是可选的
            client = cdn_client.CdnClient(self.cred, "", clientProfile)

            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.PurgePathCacheRequest()
            params = {
                "Paths": task_list,
                "FlushType": "flush"
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个PurgePathCacheResponse的实例，与请求对象对应
            resp = client.PurgePathCache(req)
            # 输出json格式的字符串回包
            return resp.to_json_string()

        except TencentCloudSDKException as err:
            print(err)
            return None

    @class_log_printer
    def create_refresh_file_task(self, task_list: list):
        try:
            # 实例化一个http选项，可选的，没有特殊需求可以跳过
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cdn.tencentcloudapi.com"

            # 实例化一个client选项，可选的，没有特殊需求可以跳过
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 实例化要请求产品的client对象,clientProfile是可选的
            client = cdn_client.CdnClient(self.cred, "", clientProfile)

            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.PurgeUrlsCacheRequest()
            params = {
                "Urls": task_list,
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个PurgeUrlsCacheResponse的实例，与请求对象对应
            resp = client.PurgeUrlsCache(req)
            # 输出json格式的字符串回包
            return resp.to_json_string()

        except TencentCloudSDKException as err:
            print(err)
            return None
