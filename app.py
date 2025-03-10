import asyncio
import time

from api import Stork


async def main():
    file_path = "emails.txt"
    with open(file_path, 'r') as file:
        for line in file:
            # 按分隔符 "----" 分割每行内容
            parts = line.strip().split('----')
            if len(parts) == 4:
                ip = parts[0]
                email = parts[1]
                password = parts[2]
                referral_code = parts[3]
                print(f"邮箱: {email}, 密码: {password}, 推荐码: {referral_code}")
                stork = Stork(ip, email, password, referral_code)
                stork.register()
                time.sleep(5)
                # stork.send_verify_code()
                # time.sleep(5)
                await stork.confirm_email()
            else:
                print(f"无效的行: {line.strip()}")

if __name__ == '__main__':
    asyncio.run(main())