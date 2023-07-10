# Digital Certificate Helper
This repository (hosted at https://github.com/ramubhai/Vishwakarma) provides simple python scripts for following purpose.

1. Generate self-signed root certificate.
2. Generate code-signing certificate, counter signed by root certificate generated above.
3. TODO: Sign windows executable using the code signing certificate.


# How to use
1. Make sure python is installed on your system.
2. Make sure "cryptography" package is installed.
3. Change the high level configuration parameters in both script.
4. Run the GenerateRootCA.py 1st.
5. Than run the GenerateBinarySigner.py

# Contribute
Only small contributions / corrections welcome.