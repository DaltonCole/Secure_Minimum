from random import randrange, choice, shuffle
from phe import paillier

# Pretend everyting is encrypted because -.-

# Z_n
N = 13

# Bit length
l = 3

# String formating for l bits 
bit_str = '{:0' + str(l) + 'b}'

# Generate pailliar keys
public_key, private_key = paillier.generate_paillier_keypair()

def secure_multiplication(a, b):
	### Party 1 ###
	ra = randrange(0, N)
	rb = randrange(0, N)

	a_prime = (a + public_key.encrypt(ra))
	b_prime = (b + public_key.encrypt(rb))

	### Party 2 ###
	h_a = private_key.decrypt(a_prime)
	h_b = private_key.decrypt(b_prime)

	h = (h_a * h_b) % N
	h_prime = public_key.encrypt(h)

	### Party 1 ###
	s = h_prime + (a * (N - rb))
	s_prime = s + (b * (N - ra))
	a_times_b = s_prime + (public_key.encrypt(ra * rb) * (N - 1))

	return a_times_b

def minimum(u, v):
	### Party 1 ###
	# Randomly choose functionality
	f = choice(["u > v", "u < v"])
	print("f: {}".format(f))

	# Initalize H_0
	h_i = public_key.encrypt(0)

	# Random s and t
	s = []
	t = []

	# L list
	L = []


	for i in range(l):
		print("For {} in {}".format(i, l))
		# Assume we can get each bit out of encrypted text
		u_i = public_key.encrypt(int(bit_str.format(x)[i]))
		v_i = public_key.encrypt(int(bit_str.format(y)[i]))
		print("U_{} = {}".format(i, private_key.decrypt(u_i)))
		print("V_{} = {}".format(i, private_key.decrypt(v_i)))

		# Secure minimum
		e_ui_times_vi = secure_multiplication(u_i, v_i)
		print("Secure Multiplication: E({})".format(private_key.decrypt(e_ui_times_vi) % N))
		#print(private_key.decrypt(e_ui_times_vi) % N)

		# Assign w_i based on f
		w_i = 0
		if f == 'u > v':
			w_i = u_i + (e_ui_times_vi * (N - 1))
		else:
			w_i = v_i + (e_ui_times_vi * (N - 1))

		print("W_{} = E({})".format(i, private_key.decrypt(w_i) % N))

		# G_i
		g_i = public_key.encrypt(int(bit_str.format(x)[i]) ^ int(bit_str.format(y)[i]))
		print("G_{} = E(U_{} XOR V_{}) = E({})".format(i, i, i, private_key.decrypt(g_i) % N))

		# H_i
		s.append(randrange(0, N))
		h_i = (h_i * s[-1]) + g_i
		print("H_{} = E({})".format(i, private_key.decrypt(h_i) % N))

		# Phi
		phi_i = public_key.encrypt(-1) + h_i
		print("Φ_{} = E({})".format(i, private_key.decrypt(phi_i) % N))

		# L_i
		t.append(randrange(0, N))
		l_i = w_i + (phi_i * t[-1])
		print("L_{} = W_{} * Φ^t_{} = E({}) * E({})^{} = E({})".format(\
			i, i, i, private_key.decrypt(w_i) % N, private_key.decrypt(phi_i) % N, \
			t[-1], private_key.decrypt(l_i) % N))
		L.append(l_i)

	print("E(L): ", end='')
	[print(private_key.decrypt(x) % N, end=', ') for x in L]
	print()
	# Permute L
	shuffle(L)
	print("E(L'): ", end='')
	[print(private_key.decrypt(x) % N, end=', ') for x in L]
	print()

	### Party 2 ###
	print("Party 2")
	M = [private_key.decrypt(x) % N for x in L]
	print("M: {}".format(M))

	# Alpha
	alpha = 0
	if 1 in M:
		alpha = 1
	print("α = {}".format(alpha))

	e_alpha = public_key.encrypt(alpha)
	print("E(α) = E({})".format(alpha))

	### Party 1 ###
	print("Party 1")
	if f == 'u > v':
		return e_alpha
	else:
		return (e_alpha + (public_key.encrypt(-1) * (N - 1))) # Double check


x = 5
y = 7

#c = secure_multiplication(a, b)
#print(private_key.decrypt(c) % N)

##### Phase 2 #####
### Party 1 ###
print("Party 1")
a = public_key.encrypt(x)
b = public_key.encrypt(y)

print("U = E({})".format(x))
print("V = E({})".format(y))

print("Perform Binary decomposition")

# Min Index
print("Perform Minimum")
min_index = public_key.encrypt(private_key.decrypt(minimum(a, b)) % N) # Mod Field
print("Min Index: {}".format(private_key.decrypt(min_index)))

# Gamma
gamma = []
r = []
for i in range(l):
	r.append(randrange(0, N))
	gamma.append(public_key.encrypt(int(bit_str.format(y)[i]) - int(bit_str.format(x)[i])) + \
		public_key.encrypt(r[-1]))

print("Γ: E(", end='')
[print(private_key.decrypt(x) % N, end=', ') for x in gamma]
print(")")

# Permutation
#shuffle(gamma)
gamma.append(gamma.pop(0))
print("Permuted Γ: E(", end='')
[print(private_key.decrypt(x) % N, end=', ') for x in gamma]
print(")")

### Party 2 ### (permuted gamma and min_index)
print("Party 2")
d_min_index = private_key.decrypt(min_index)
print("min_index: {}".format(d_min_index))

m_prime = []
for i in range(l):
	m_prime.append(gamma[i] * d_min_index)
print("M' = E(", end='')
[print(private_key.decrypt(x) % N, end=', ') for x in m_prime]
print(")")

### Party 1 ### (m_prime)
print("Party 1")
gamma = [gamma.pop()] + gamma
print("Un-Permuted Γ: E(", end='')
[print(private_key.decrypt(x) % N, end=', ') for x in gamma]
print(")")

# Lambda
lam = []
for i in range(l):
	lam.append(m_prime[i] + (min_index * (N - r[i])))
print("λ: E(", end='')
[print(private_key.decrypt(x) % N, end=', ') for x in lam]
print(")")

# Gamma
gamma = []
for i in range(l):
	gamma.append(public_key.encrypt(int(bit_str.format(x)[i])) + lam[i])

# Move back in field, and then to binary
for i in range(l):
	gamma[i] = public_key.encrypt((private_key.decrypt(gamma[i]) % N) % 2)

# Convert back into a single number (need to do because of phe limitations)
gamma = public_key.encrypt(int(''.join(str(x) for x in [private_key.decrypt(x) for x in gamma]), 2))
print("E(min(E(U), E(V))) = Γ = E({})".format(private_key.decrypt(gamma)))

print("Min: {}".format(private_key.decrypt(gamma)))