from secrets import token_bytes

from blspy import AugSchemeMPL, PrivateKey, G1Element, G2Element

SK_SEED_SIZE = 64
scheme = AugSchemeMPL

def tss_gen_private_key() -> PrivateKey:
    seed = token_bytes(SK_SEED_SIZE)
    return scheme.key_gen(seed)

def tss_get_public_key(private_key: PrivateKey) -> G1Element:
    return private_key.get_g1()

def tss_share_sign(message: bytes, sk: PrivateKey) -> G2Element:
    return scheme.sign(sk, message)

def tss_share_verify(message: bytes, vk: G1Element, partial_sig: G2Element):
    return scheme.verify(vk, message, partial_sig)

def tss_combine(partial_sigs: list[G2Element]) -> G2Element:
    return scheme.aggregate(partial_sigs)

def tss_verify(messages: list[bytes], pk: list[G1Element], threshold_sig: G2Element) -> bool:
    return scheme.aggregate_verify(pk, messages, threshold_sig)
