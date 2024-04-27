import sys,os
module_path = os.path.abspath(os.path.join('../'))
if module_path not in sys.path:
    sys.path.append(module_path)

from Helper import *
from logging import getLogger
from ecc import *


LOGGER = getLogger(__name__)


OP_CODE_NAMES = {
    0x00: "OP_0",
    0x01: "OP_PUSHBYTES_1",
    0x02: "OP_PUSHBYTES_2",
    0x03: "OP_PUSHBYTES_3",
    0x04: "OP_PUSHBYTES_4",
    0x05: "OP_PUSHBYTES_5",
    0x06: "OP_PUSHBYTES_6",
    0x07: "OP_PUSHBYTES_7",
    0x08: "OP_PUSHBYTES_8",
    0x09: "OP_PUSHBYTES_9",
    0x0a: "OP_PUSHBYTES_10",
    0x0b: "OP_PUSHBYTES_11",
    0x0c: "OP_PUSHBYTES_12",
    0x0d: "OP_PUSHBYTES_13",
    0x0e: "OP_PUSHBYTES_14",
    0x0f: "OP_PUSHBYTES_15",
    0x10: "OP_PUSHBYTES_16",
    0x11: "OP_PUSHBYTES_17",
    0x12: "OP_PUSHBYTES_18",
    0x13: "OP_PUSHBYTES_19",
    0x14: "OP_PUSHBYTES_20",
    0x15: "OP_PUSHBYTES_21",
    0x16: "OP_PUSHBYTES_22",
    0x17: "OP_PUSHBYTES_23",
    0x18: "OP_PUSHBYTES_24",
    0x19: "OP_PUSHBYTES_25",
    0x1a: "OP_PUSHBYTES_26",
    0x1b: "OP_PUSHBYTES_27",
    0x1c: "OP_PUSHBYTES_28",
    0x1d: "OP_PUSHBYTES_29",
    0x1e: "OP_PUSHBYTES_30",
    0x1f: "OP_PUSHBYTES_31",
    0x20: "OP_PUSHBYTES_32",
    0x21: "OP_PUSHBYTES_33",
    0x22: "OP_PUSHBYTES_34",
    0x23: "OP_PUSHBYTES_35",
    0x24: "OP_PUSHBYTES_36",
    0x25: "OP_PUSHBYTES_37",
    0x26: "OP_PUSHBYTES_38",
    0x27: "OP_PUSHBYTES_39",
    0x28: "OP_PUSHBYTES_40",
    0x29: "OP_PUSHBYTES_41",
    0x2a: "OP_PUSHBYTES_42",
    0x2b: "OP_PUSHBYTES_43",
    0x2c: "OP_PUSHBYTES_44",
    0x2d: "OP_PUSHBYTES_45",
    0x2e: "OP_PUSHBYTES_46",
    0x2f: "OP_PUSHBYTES_47",
    0x30: "OP_PUSHBYTES_48",
    0x31: "OP_PUSHBYTES_49",
    0x32: "OP_PUSHBYTES_50",
    0x33: "OP_PUSHBYTES_51",
    0x34: "OP_PUSHBYTES_52",
    0x35: "OP_PUSHBYTES_53",
    0x36: "OP_PUSHBYTES_54",
    0x37: "OP_PUSHBYTES_55",
    0x38: "OP_PUSHBYTES_56",
    0x39: "OP_PUSHBYTES_57",
    0x3a: "OP_PUSHBYTES_58",
    0x3b: "OP_PUSHBYTES_59",
    0x3c: "OP_PUSHBYTES_60",
    0x3d: "OP_PUSHBYTES_61",
    0x3e: "OP_PUSHBYTES_62",
    0x3f: "OP_PUSHBYTES_63",
    0x40: "OP_PUSHBYTES_64",
    0x41: "OP_PUSHBYTES_65",
    0x42: "OP_PUSHBYTES_66",
    0x43: "OP_PUSHBYTES_67",
    0x44: "OP_PUSHBYTES_68",
    0x45: "OP_PUSHBYTES_69",
    0x46: "OP_PUSHBYTES_70",
    0x47: "OP_PUSHBYTES_71",
    0x48: "OP_PUSHBYTES_72",
    0x49: "OP_PUSHBYTES_73",
    0x4a: "OP_PUSHBYTES_74",
    0x4b: "OP_PUSHBYTES_75",
    0x4c: "OP_PUSHDATA1",
    0x4d: "OP_PUSHDATA2",
    0x4e: "OP_PUSHDATA4",
    0x4f: "OP_PUSHNUM_NEG1",
    0x50: "OP_RESERVED",
    0x51: "OP_PUSHNUM_1",
    0x52: "OP_PUSHNUM_2",
    0x53: "OP_PUSHNUM_3",
    0x54: "OP_PUSHNUM_4",
    0x55: "OP_PUSHNUM_5",
    0x56: "OP_PUSHNUM_6",
    0x57: "OP_PUSHNUM_7",
    0x58: "OP_PUSHNUM_8",
    0x59: "OP_PUSHNUM_9",
    0x5a: "OP_PUSHNUM_10",
    0x5b: "OP_PUSHNUM_11",
    0x5c: "OP_PUSHNUM_12",
    0x5d: "OP_PUSHNUM_13",
    0x5e: "OP_PUSHNUM_14",
    0x5f: "OP_PUSHNUM_15",
    0x60: "OP_PUSHNUM_16",
    0x61: "OP_NOP",
    0x62: "OP_VER",
    0x63: "OP_IF",
    0x64: "OP_NOTIF",
    0x65: "OP_VERIF",
    0x66: "OP_VERNOTIF",
    0x67: "OP_ELSE",
    0x68: "OP_ENDIF",
    0x69: "OP_VERIFY",
    0x6a: "OP_RETURN",
    0x6b: "OP_TOALTSTACK",
    0x6c: "OP_FROMALTSTACK",
    0x6d: "OP_2DROP",
    0x6e: "OP_2DUP",
    0x6f: "OP_3DUP",
    0x70: "OP_2OVER",
    0x71: "OP_2ROT",
    0x72: "OP_2SWAP",
    0x73: "OP_IFDUP",
    0x74: "OP_DEPTH",
    0x75: "OP_DROP",
    0x76: "OP_DUP",
    0x77: "OP_NIP",
    0x78: "OP_OVER",
    0x79: "OP_PICK",
    0x7a: "OP_ROLL",
    0x7b: "OP_ROT",
    0x7c: "OP_SWAP",
    0x7d: "OP_TUCK",
    0x7e: "OP_CAT",
    0x7f: "OP_SUBSTR",
    0x80: "OP_LEFT",
    0x81: "OP_RIGHT",
    0x82: "OP_SIZE",
    0x83: "OP_INVERT",
    0x84: "OP_AND",
    0x85: "OP_OR",
    0x86: "OP_XOR",
    0x87: "OP_EQUAL",
    0x88: "OP_EQUALVERIFY",
    0x89: "OP_RESERVED1",
    0x8a: "OP_RESERVED2",
    0x8b: "OP_1ADD",
    0x8c: "OP_1SUB",
    0x8d: "OP_2MUL",
    0x8e: "OP_2DIV",
    0x8f: "OP_NEGATE",
    0x90: "OP_ABS",
    0x91: "OP_NOT",
    0x92: "OP_0NOTEQUAL",
    0x93: "OP_ADD",
    0x94: "OP_SUB",
    0x95: "OP_MUL",
    0x96: "OP_DIV",
    0x97: "OP_MOD",
    0x98: "OP_LSHIFT",
    0x99: "OP_RSHIFT",
    0x9a: "OP_BOOLAND",
    0x9b: "OP_BOOLOR",
    0x9c: "OP_NUMEQUAL",
    0x9d: "OP_NUMEQUALVERIFY",
    0x9e: "OP_NUMNOTEQUAL",
    0x9f: "OP_LESSTHAN",
    0xa0: "OP_GREATERTHAN",
    0xa1: "OP_LESSTHANOREQUAL",
    0xa2: "OP_GREATERTHANOREQUAL",
    0xa3: "OP_MIN",
    0xa4: "OP_MAX",
    0xa5: "OP_WITHIN",
    0xa6: "OP_RIPEMD160",
    0xa7: "OP_SHA1",
    0xa8: "OP_SHA256",
    0xa9: "OP_HASH160",
    0xaa: "OP_HASH256",
    0xab: "OP_CODESEPARATOR",
    0xac: "OP_CHECKSIG",
    0xad: "OP_CHECKSIGVERIFY",
    0xae: "OP_CHECKMULTISIG",
    0xaf: "OP_CHECKMULTISIGVERIFY",
    0xb0: "OP_NOP1",
    0xb1: "OP_CLTV",
    0xb2: "OP_CSV",
    0xb3: "OP_NOP4",
    0xb4: "OP_NOP5",
    0xb5: "OP_NOP6",
    0xb6: "OP_NOP7",
    0xb7: "OP_NOP8",
    0xb8: "OP_NOP9",
    0xb9: "OP_NOP10",
    0xba: "OP_CHECKSIGADD",
    0xbb: "OP_RETURN_187",
    0xbc: "OP_RETURN_188",
    0xbd: "OP_RETURN_189",
    0xbe: "OP_RETURN_190",
    0xbf: "OP_RETURN_191",
    0xc0: "OP_RETURN_192",
    0xc1: "OP_RETURN_193",
    0xc2: "OP_RETURN_194",
    0xc3: "OP_RETURN_195",
    0xc4: "OP_RETURN_196",
    0xc5: "OP_RETURN_197",
    0xc6: "OP_RETURN_198",
    0xc7: "OP_RETURN_199",
    0xc8: "OP_RETURN_200",
    0xc9: "OP_RETURN_201",
    0xca: "OP_RETURN_202",
    0xcb: "OP_RETURN_203",
    0xcc: "OP_RETURN_204",
    0xcd: "OP_RETURN_205",
    0xce: "OP_RETURN_206",
    0xcf: "OP_RETURN_207",
    0xd0: "OP_RETURN_208",
    0xd1: "OP_RETURN_209",
    0xd2: "OP_RETURN_210",
    0xd3: "OP_RETURN_211",
    0xd4: "OP_RETURN_212",
    0xd5: "OP_RETURN_213",
    0xd6: "OP_RETURN_214",
    0xd7: "OP_RETURN_215",
    0xd8: "OP_RETURN_216",
    0xd9: "OP_RETURN_217",
    0xda: "OP_RETURN_218",
    0xdb: "OP_RETURN_219",
    0xdc: "OP_RETURN_220",
    0xdd: "OP_RETURN_221",
    0xde: "OP_RETURN_222",
    0xdf: "OP_RETURN_223",
    0xe0: "OP_RETURN_224",
    0xe1: "OP_RETURN_225",
    0xe2: "OP_RETURN_226",
    0xe3: "OP_RETURN_227",
    0xe4: "OP_RETURN_228",
    0xe5: "OP_RETURN_229",
    0xe6: "OP_RETURN_230",
    0xe7: "OP_RETURN_231",
    0xe8: "OP_RETURN_232",
    0xe9: "OP_RETURN_233",
    0xea: "OP_RETURN_234",
    0xeb: "OP_RETURN_235",
    0xec: "OP_RETURN_236",
    0xed: "OP_RETURN_237",
    0xee: "OP_RETURN_238",
    0xef: "OP_RETURN_239",
    0xf0: "OP_RETURN_240",
    0xf1: "OP_RETURN_241",
    0xf2: "OP_RETURN_242",
    0xf3: "OP_RETURN_243",
    0xf4: "OP_RETURN_244",
    0xf5: "OP_RETURN_245",
    0xf6: "OP_RETURN_246",
    0xf7: "OP_RETURN_247",
    0xf8: "OP_RETURN_248",
    0xf9: "OP_RETURN_249",
    0xfa: "OP_RETURN_250",
    0xfb: "OP_RETURN_251",
    0xfc: "OP_RETURN_252",
    0xfd: "OP_RETURN_253",
    0xfe: "OP_RETURN_254",
    0xff: "OP_INVALIDOPCODE"
}






# this function will give the funciton object from the string 
def get_function_by_name(func_name):
    # Check if the function exists in the global namespace
    if func_name in globals() and callable(globals()[func_name]):
        return globals()[func_name]
    else:
        return None


all_opcodes_used : {  'OP_ELSE',   'OP_ENDIF'}



## definitions of all functions used -> 

def OP_CLTV(stack, locktime, sequence):
    if sequence == 0xffffffff:
        return False
    if len(stack) < 1:
        return False
    element = decode_num(stack[-1])
    if element < 0:
        return False
    if element < 500000000 and locktime > 500000000:
        return False
    if locktime < element:
        return False
    return True



def OP_CSV(stack, version, sequence):
    if sequence & (1 << 31) == (1 << 31):
        return False
    if len(stack) < 1:
        return False
    element = decode_num(stack[-1])
    if element < 0:
        return False
    if element & (1 << 31) == (1 << 31):
        if version < 2:
            return False
        elif sequence & (1 << 31) == (1 << 31):
            return False
        elif element & (1 << 22) != sequence & (1 << 22):
            return False
        elif element & 0xffff > sequence & 0xffff:
            return False
    return True



def OP_GREATERTHAN(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    if element2 > element1:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

def OP_SWAP(stack):
    if len(stack) < 2:
        return False
    stack.append(stack.pop(-2))
    return True

def OP_OVER(stack):
    if len(stack) < 2:
        return False
    stack.append(stack[-2])
    return True

def OP_IFDUP(stack):
    if len(stack) < 1:
        return False
    if decode_num(stack[-1]) != 0:
        stack.append(stack[-1])
    return True

def OP_SIZE(stack):
    if len(stack) < 1:
        return False
    stack.append(encode_num(len(stack[-1])))
    return True

def OP_ROT(stack):
    if len(stack) < 3:
        return False
    stack.append(stack.pop(-3))
    return True


def OP_NOTIF(stack, items):
    if len(stack) < 1:
        return False
    # go through and re-make the items array based on the top stack element
    true_items = []
    false_items = []
    current_array = true_items
    found = False
    num_endifs_needed = 1
    while len(items) > 0:
        item = items.pop(0)
        if item in (99, 100):
            # nested if, we have to go another endif
            num_endifs_needed += 1
            current_array.append(item)
        elif num_endifs_needed == 1 and item == 103:
            current_array = false_items
        elif item == 104:
            if num_endifs_needed == 1:
                found = True
                break
            else:
                num_endifs_needed -= 1
                current_array.append(item)
        else:
            current_array.append(item)
    if not found:
        return False
    element = stack.pop()
    if decode_num(element) == 0:
        items[:0] = true_items
    else:
        items[:0] = false_items
    return True



def OP_SHA256(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    stack.append(hashlib.sha256(element).digest())
    return True

def OP_DROP(stack):
    if len(stack) < 1:
        return False
    stack.pop()
    return True

def OP_DEPTH(stack):
    stack.append(encode_num(len(stack)))
    return True



def OP_0(stack):
    stack.append(encode_num(0))
    return True


def OP_PUSHNUM(stack,pushnum_cmd):
    
    elements= pushnum_cmd.split("_")
    no = int(elements[2])
    stack.append(encode_num(no))
    return True

def OP_PUSHDATA1(stack):
    return True

def OP_PUSHDATA2(stack):
    return True


def OP_PUSHBYTES(stack):
    return True



def OP_DUP(stack):
    if len(stack) < 1:
        return False
    stack.append(stack[-1])
    return True


def OP_CHECKSIG(stack, z):

    
    # check that there are at least 2 elements on the stack
    if len(stack) < 2:
        return False
    # the top element of the stack is the SEC pubkey
    sec_pubkey = stack.pop()
    # the next element of the stack is the DER signature
    # take off the last byte of the signature as that's the hash_type
    der_signature = stack.pop()[:-1]
    # parse the serialized pubkey and signature into objects
    try:
        point= S256Point.parse(bytes.fromhex(sec_pubkey))
        sig= Signature.parse(bytes.fromhex(der_signature[:-2]))
    except (ValueError, SyntaxError) as e:
        LOGGER.info(e)
        return False
    # verify the signature using S256Point.verify()
    # push an encoded 1 or 0 depending on whether the signature verified
    if point.verify(z,sig):
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def OP_CHECKMULTISIG(stack, z):
    if len(stack) < 1:
        return False
    n = decode_num(stack.pop())
    if len(stack) < n + 1:
        return False
    sec_pubkeys = []
    for _ in range(n):
        sec_pubkeys.append(stack.pop())
    m = decode_num(stack.pop())
    if len(stack) < m + 1:
        return False
    der_signatures = []
    for _ in range(m):
        # signature is assumed to be using SIGHASH_ALL
        der_signatures.append(stack.pop()[:-1])
    # OP_CHECKMULTISIG bug
    stack.pop()
    try:
        # parse all the points
        points = [S256Point.parse(sec) for sec in sec_pubkeys]
        # parse all the signatures
        sigs = [Signature.parse(der) for der in der_signatures]
        # loop through the signatures
        for sig in sigs:
            # if we have no more points, signatures are no good
            if len(points) == 0:
                LOGGER.info("signatures no good or not in right order")
                return False
            # we loop until we find the point which works with this signature
            while points:
                # get the current point from the list of points
                point = points.pop(0)
                # we check if this signature goes with the current point
                if point.verify(z, sig):
                    break
        # the signatures are valid, so push a 1 to the stack
        stack.append(encode_num(1))
    except (ValueError, SyntaxError):
        return False
    return True


def OP_HASH160(stack):
    # check that there's at least 1 element on the stack
    if len(stack) < 1:
        return False
    # pop off the top element from the stack
    element = stack.pop()
    # push a hash160 of the popped off element to the stack
    h160 = HASH160(bytes.fromhex(element))
    stack.append(h160)
    return True

def OP_CHECKSIGVERIFY(stack, z):
    return OP_CHECKSIG(stack, z) and OP_VERIFY(stack)


def OP_EQUALVERIFY(stack):
    return OP_EQUAL(stack) and OP_VERIFY(stack)


def OP_EQUAL(stack):
    if len(stack) < 2:
        return False
    element1 = stack.pop()
    element2 = stack.pop()
    if element1 == element2:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True



def OP_VERIFY(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    if decode_num(element) == 0:
        return False
    return True

def OP_RETURN(stack):
    return False

def OP_IF(stack, items):
    if len(stack) < 1:
        return False
    # go through and re-make the items array based on the top stack element
    true_items = []
    false_items = []
    current_array = true_items
    found = False
    num_endifs_needed = 1
    while len(items) > 0:
        item = items.pop(0)
        if item in (99, 100):
            # nested if, we have to go another endif
            num_endifs_needed += 1
            current_array.append(item)
        elif num_endifs_needed == 1 and item == 103:
            current_array = false_items
        elif item == 104:
            if num_endifs_needed == 1:
                found = True
                break
            else:
                num_endifs_needed -= 1
                current_array.append(item)
        else:
            current_array.append(item)
    if not found:
        return False
    element = stack.pop()
    if decode_num(element) == 0:
        items[:0] = false_items
    else:
        items[:0] = true_items
    return True

