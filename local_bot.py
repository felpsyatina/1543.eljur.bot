import time
import user_req

if __name__ == '__main__':
    try:
        while True:
            inp = input()
            ans = user_req.parse_message_from_user("vk", 1, inp)
            print(ans)
    except KeyboardInterrupt:
        pass
