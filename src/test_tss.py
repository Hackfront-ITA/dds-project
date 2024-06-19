from tss import \
    tss_gen_private_key, tss_get_public_key, tss_share_sign, \
    tss_share_verify, tss_combine, tss_verify

sk1 = tss_gen_private_key()
vk1 = tss_get_public_key(sk1)

sk2 = tss_gen_private_key()
vk2 = tss_get_public_key(sk2)

pk = [ vk1, vk2 ]

msg1 = 'Prova dal nodo 1'.encode('ascii')
psig1 = tss_share_sign(msg1, sk1)
ok = tss_share_verify(msg1, vk1, psig1)
print(f'ok1 = {ok}')

msg2 = 'Prova dal nodo 2'.encode('ascii')
psig2 = tss_share_sign(msg2, sk2)
ok = tss_share_verify(msg2, vk2, psig2)
print(f'ok2 = {ok}')

tsig = tss_combine([ psig1, psig2 ])
print(f'tsig = {tsig}')

ok = tss_verify([ msg1, msg2 ], pk, tsig)
print(f'okt = {ok}')
