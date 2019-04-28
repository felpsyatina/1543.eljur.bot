import user_req

if __name__ == '__main__':
    try:
        while True:
            inp = input()
            ans = user_req.parse_message_from_user({
                "src": "vk", "id": 1, "first_name": "Пахан", "last_name": "Дуров", "text": inp
            })
            print(ans)
    except KeyboardInterrupt:
        pass
