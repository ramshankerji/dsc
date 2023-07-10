#Author: Ram Shanker
#MIT License
#Following script will create a self signed root ca certificate.
#2 Number file generated (one public key and one private key) shall be used to certify Code Signing certificate.
#The public key generated by this file has to be added to trusted root certificate store. Refer readme.md for instructions.
#2 Number file generated by the GenerateBinarySigner.py shall be used to sign the binary executable file.
#Provide all the necessary details in the # High Level Configuration parameter section below.

import os
import sys
import datetime
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# High Level Configuration parameters. Do not omit or leave blank any parameter.
certificateCommonName = u"RootCA-01" #Generated file will have this file name.
organizationName      = u"Your Company Name" # For individual people it is personal name.
dnsName               = u'example.com' # Put your corporate/personal website here. Do not write http:// or https://
countryCode2Digit     = u"IN"
stateOrProvince       = u"New Delhi"
locality              = u"Bhikaji Kama Place"

###################################################################
# Do not change any code below this line. Only do configuration above
asymmetric_algorithm = "rsa" # It can be either "rsa" or "ed25519"

# Check safely for existing of existing certificate private key to avoid accidentally deleting / overwriting it.
script_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_directory, certificateCommonName + u".key")
if os.path.isfile(file_path):
    print("A private key file with filename: " + certificateCommonName + u".key" + u" already exists.")
    print("Would you like to over-write this key with a newly generated one?")
    user_choice = input("If you choose yes, old keys will be lost forever. (yes/no): ")
    if user_choice.lower() == "no" or user_choice.lower() == "n":
        sys.exit()

# Random key generation
if asymmetric_algorithm == "ed25519":
    private_key = ed25519.Ed25519PrivateKey.generate() #Apparently windows8.1 not accepting ed25519 signature ?
    hashAlgorithm = None
else: # Default fallback rsa.
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    hashAlgorithm = hashes.SHA256()

#Compute the public key corresponding to private key. crypto library automatically recognizes type of private key.
public_key = private_key.public_key()

# Certificate configurations
# Build the subject of the certificate
subject = x509.Name([
    x509.NameAttribute(x509.NameOID.COUNTRY_NAME, countryCode2Digit),
    x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, stateOrProvince),
    x509.NameAttribute(x509.NameOID.LOCALITY_NAME, locality),
    x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, organizationName),
    x509.NameAttribute(x509.NameOID.COMMON_NAME, certificateCommonName)
])
# Define the issuance policy OID for "all"
issuance_policy_oid = x509.ObjectIdentifier("2.23.140.1.2.2")

builder = x509.CertificateBuilder()
builder = builder.subject_name(subject)
builder = builder.issuer_name(subject) # For Root certificate, Subject Name and Issued name are same.
one_day = datetime.timedelta(1, 0, 0)
builder = builder.not_valid_before(datetime.datetime.today() - one_day)
builder = builder.not_valid_after(datetime.datetime.today() + (one_day * 365 * 30)) # 30 Years.
builder = builder.serial_number(x509.random_serial_number())
builder = builder.public_key(public_key)

# Define the Key Usage extension
key_usage = x509.KeyUsage(
    digital_signature=True,
    content_commitment=False,
    key_encipherment=False,
    data_encipherment=False,
    key_agreement=False,
    key_cert_sign=True, #The bit keyCertSign is for use in CA  certificates only. 
    crl_sign=True,
    encipher_only=False,
    decipher_only=False
)
builder = builder.add_extension(key_usage,critical=True)
builder = builder.add_extension(x509.SubjectAlternativeName([x509.DNSName(dnsName)]),critical=False)
builder = builder.add_extension(x509.BasicConstraints(ca=True, path_length=None),critical=True,)
builder = builder.add_extension(x509.CertificatePolicies([x509.PolicyInformation(issuance_policy_oid,[])]),critical=False)

# Generate the SubjectKeyIdentifier and match the AuthorityKeyIdentifier to the same.
builder = builder.add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(public_key),critical=False)
builder = builder.add_extension(x509.SubjectKeyIdentifier.from_public_key(public_key),critical=False)

#Finally generate the certificate using all the options provided above.
# Algorithm must be None when signing via ed25519 or ed448. For RSA it can be hashes.SHA256()
certificate = builder.sign(
    private_key=private_key, algorithm= hashAlgorithm, backend=default_backend()
)

# Save to File after generating PEM-encoded string of the certificate object.
pem_data_public = certificate.public_bytes(encoding=serialization.Encoding.PEM)

# Convert the private key object to a PEM-encoded string
# We store our private key using some password only. Ask the user for password.
password = input("Enter password to store root certificate's private key: ")

# Derive a key from the password
# salt is some random sequence of characters required to defend against rainbow-table attack. It can be any long sentence
salt = b'salt_thiscanbeanylargesentenceforexampleearthortatesaroundthesunandsoon'
kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
key = kdf.derive(password.encode())

pem_data_private = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.BestAvailableEncryption(key)
)

# Write the PEM-encoded string to a file
with open(certificateCommonName + ".crt", 'wb') as file:
    file.write(pem_data_public)
with open(certificateCommonName + ".key", 'wb') as file:
    file.write(pem_data_private)
