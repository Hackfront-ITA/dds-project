from secrets import token_bytes

from blspy import AugSchemeMPL, PrivateKey, G1Element, G2Element

SK_SEED_SIZE = 64
scheme = AugSchemeMPL

def tss_gen_private_key(seed=None) -> PrivateKey:
    if seed == None:
        seed = token_bytes(SK_SEED_SIZE)

    return scheme.key_gen(seed)

def tss_get_public_key(private_key: PrivateKey) -> G1Element:
    return private_key.get_g1()

def tss_share_sign(message: str, sk: PrivateKey) -> str:
    message = bytes(message, 'utf8')
    result = scheme.sign(sk, message)

    return str(result)

def tss_share_verify(message: str, vk: G1Element, partial_sig: str) -> bool:
    message = bytes(message, 'utf8')
    partial_sig = G2Element.from_bytes(bytes.fromhex(partial_sig))

    return scheme.verify(vk, message, partial_sig)

def tss_combine(partial_sigs: list[str]) -> str:
    tmp = [ None ] * len(partial_sigs)

    for i in range(0, len(partial_sigs)):
        tmp[i] = G2Element.from_bytes(bytes.fromhex(partial_sigs[i]))

    result = scheme.aggregate(tmp)

    return str(result)

def tss_verify(messages: list[str], pk: list[G1Element], threshold_sig: str) -> bool:
    threshold_sig = G2Element.from_bytes(bytes.fromhex(threshold_sig))

    tmp = [ None ] * len(messages)

    for i in range(0, len(messages)):
        tmp[i] = bytes(messages[i], 'utf8')

    return scheme.aggregate_verify(pk, tmp, threshold_sig)
