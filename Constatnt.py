import ast
import socket
DESERT = 0
SEA = 1
LUMBER = 2
BRICK = 3
ORE = 4
WOOL = 5
GRAIN = 6
VILLAGE = 7
CITY = 8
ROAD = 9
DEV_CARD = 10
RED = 120
BLUE = 121
ORANGE = 122
WHITE = 123
KNIGHT = 15
VICTORY_POINT = 16
MONOPOLY = 17
ROADS_BUILD = 18
YEAR_OF_PLENTY = 19
THREE_TO_ONE = 20
PHASE_FIRST_ROLL = 0
PHASE_FIRST_VILLAGE = 1
PHASE_SECOND_VILLAGE = 2
PHASE_INGAME = 3
TILES_NUMBERS = 2*[i for i in range(3, 7)] + 2*[i for i in range(8, 12)] + [2, 12, 0]
TILES_RESOURCES = [DESERT] + 4*[WOOL, GRAIN, LUMBER] + 3*[BRICK, ORE]
RESOURCE_TO_STR = {LUMBER:'lumber', BRICK:'brick', ORE:'ore', WOOL:'wool', GRAIN:'grain'}
RESOURCE_TO_INT = {'lumber': LUMBER, 'brick':BRICK, 'ore':ORE, 'wool':WOOL, 'grain':GRAIN}
GIVE = True
TAKE = False
EMPTY_PROPOSE = {GIVE:{ORE: 0, LUMBER:0, WOOL:0, BRICK:0, GRAIN:0}, TAKE:{ORE: 0, LUMBER:0, WOOL:0, BRICK:0, GRAIN:0}}

def convert_to_int_dict(string_dict):
    dict_obj = string_dict
    if type(string_dict) == type(""):
        dict_obj = ast.literal_eval(string_dict)
    int_dict = {int(key): int(value) for key, value in dict_obj.items()}
    return int_dict

def convert_to_bool_dict(string_dict):
    dict_obj = string_dict
    if type(string_dict) == type(""):
        dict_obj = ast.literal_eval(string_dict)
    int_dict = {int(key): bool(value) for key, value in dict_obj.items()}
    return int_dict

def convert_to_int_list_of_lists(string_list):
    list_obj = string_list
    if type(string_list) == type(""):
        list_obj = ast.literal_eval(string_list)
    int_list = [[int(item) for item in sublist] for sublist in list_obj]
    return int_list

def padding(num: int):
    return (10-len(str(num)))*'0' + str(num)

def send_message(client: socket.socket, message):
    length_prefix = f"${padding(len(message))}$"  # Prefix with length of the message
    toSend = length_prefix + message
    client.sendall(toSend.encode('utf-8'))

def get_message(client, printMessage = False) -> str:
    if printMessage:
        data = client.recv(2**18).decode('utf-8')
        print(len(data))
        return data[12:]
    length_prefix = client.recv(12).decode('utf-8')  # Read the length prefix
    if not length_prefix:
        raise ConnectionError("Socket connection broken")
    message_length = int(length_prefix[1:-1])
    buffer = ''
    while len(buffer) < message_length:
        data = client.recv(4096).decode('utf-8')
        if not data:
            raise ConnectionError("Socket connection broken")
        buffer += data
    return buffer
