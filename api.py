import json
from loguru import logger

import requests
from imap_utils import check_email_for_link, check_if_email_valid
from config import PASSWORD, imap_server


class Stork(object):

    def __init__(self, ip, email, password, referrer):
        self.ip = ip
        self.email = email
        # 邮箱密码
        self.password = password
        self.referrer = referrer
        self.url = "https://cognito-idp.ap-northeast-1.amazonaws.com/"
        self.client_id = "5msns4n49hmg3dftp2tp1t2iuh"

    def register(self):
        payload = json.dumps({
            "Username": self.email,
            "Password": PASSWORD,
            "UserAttributes": [
                {
                    "Name": "email",
                    "Value": self.email
                },
                {
                    "Name": "custom:referral_code",
                    "Value": self.referrer
                }
            ],
            "ClientId": self.client_id
        })
        # 定义请求头
        headers = {
            # ":authority": "cognito-idp.ap-northeast-1.amazonaws.com",
            # ":method": "POST",
            # ":path": "/",
            # ":scheme": "https",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "no-store",
            "content-type": "application/x-amz-json-1.1",
            "origin": "https://app.stork.network",
            "priority": "u=1, i",
            "referer": "https://app.stork.network/",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "x-amz-target": "AWSCognitoIdentityProviderService.SignUp",
            "x-amz-user-agent": "aws-amplify/6.12.1 auth/1 framework/2 Authenticator ui-react/6.9.0"
        }

        logger.info(f"Registering user {self.email} with referrer {self.referrer}")
        response = requests.request("POST", self.url, headers=headers, data=payload)
        if response.status_code == 200:
            logger.info(f"Registration successful: {response.text}")
            register_response = json.loads(response.text)
            if "UserSub" in register_response:
                # 说明注册成功
                self.report_register_info(self.ip, self.email, register_response["UserSub"], "false")
        else:
            logger.error(f"Failed to register user {self.email}: {response.text}")

    def send_verify_code(self):
        payload = json.dumps({
            "Username": self.email,
            "ClientId": self.client_id
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", self.url, headers=headers, data=payload)
        if response.status_code == 200:
            logger.info(f"Verification code sent: {response.text}")
        else:
            logger.error(f"Failed to send verification code: {response.text}")

    async def confirm_email(self):
        if await check_if_email_valid(imap_server, self.email, self.password):
            verify_code = await check_email_for_link(imap_server, self.email, self.password, link_pattern=r'\b\d{6}\b')
            logger.info(f"Verification code: {verify_code}")
            if verify_code:
                payload = json.dumps({
                    "Username": self.email,
                    "ConfirmationCode": verify_code,
                    "ClientId": self.client_id
                })
                # 定义请求头
                headers = {
                    # ":authority": "cognito-idp.ap-northeast-1.amazonaws.com",
                    # ":method": "POST",
                    # ":path": "/",
                    # ":scheme": "https",
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate, br, zstd",
                    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "cache-control": "no-store",
                    "content-type": "application/x-amz-json-1.1",
                    "origin": "https://app.stork.network",
                    "priority": "u=1, i",
                    "referer": "https://app.stork.network/",
                    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"macOS"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "cross-site",
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                    "x-amz-target": "AWSCognitoIdentityProviderService.ConfirmSignUp",
                    "x-amz-user-agent": "aws-amplify/6.12.1 auth/1 framework/2 Authenticator ui-react/6.9.0"
                }
                response = requests.request("POST", self.url, headers=headers, data=payload)
                if response.status_code == 200:
                    logger.info(f"Email confirmed: {response.text}")
                    self.report_register_info(self.ip, self.email, None, "true")
                else:
                    logger.error(f"Failed to confirm email: {response.text}")
            else:
                logger.error(f"Failed to confirm email: ConfirmationCode not found")

    def report_register_info(self, ip, email, user_sub, confirmed):
        pass

    def get_public_ip(self):
        try:
            # 使用外部服务获取公网 IP
            response = requests.get('https://api.ipify.org?format=json')
            response.raise_for_status()  # 检查请求是否成功
            ip_data = response.json()
            return ip_data['ip']
        except requests.RequestException as e:
            return f"无法获取公网 IP: {e}"