from PublicCloudAPI.HuaweiCloud import HuaweiCloudAccount


class PaaSTask:
    def __init__(self, domain: str, dns_account: HuaweiCloudAccount, cdn_cname: str,
                 cdn_account=None, cdn_account_type=None):
        """
        :param domain: 此 CDN 域名
        :param dns_account: 默认为华为云DNS账号，不支持其它公有云
        :param cdn_cname: 此 CDN 的 CNAME 解析值
        :param cdn_account: 此 CDN 的账号 Object。如果不指定，则为None，用于主程序判定是否可以执行公有云API接口函数。
        :param cdn_account_type: 此 CDN 所属的公有云平台。如果不指定，则为None，用于主程序判定是否可以执行公有云API接口函数。
        """

        self.domain = domain
        self.dns_account = dns_account
        self.cdn_cname = cdn_cname

        if cdn_account is not None and cdn_account_type is not None:
            self.cdn_account = cdn_account
            self.cdn_account_type = cdn_account_type
        elif cdn_account is not None and cdn_account_type is None:
            self.cdn_account = None
            self.cdn_account_type = None
        else:
            raise TypeError("cdn_account and cdn_account_type must be both None or both not None")

